# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://discord.com/"""

from .common import Extractor, Message
from .. import text, exception


BASE_PATTERN = r"(?:https?://)?discord\.com"


class DiscordExtractor(Extractor):
    """Base class for Discord extractors"""
    category = "discord"
    root = "https://discord.com"
    filename_fmt = "{message_id}_{num:>02}_{filename}.{extension}"
    archive_fmt = "{message_id}_{num}.{extension}"

    server_metadata = {}
    channel_metadata = {}

    def _init(self):
        self.token = self.config("token")
        self.extract_threads = self.config("threads", True)
        self.api = DiscordAPI(self)

    def extract_default_message(self, message):
        message_metadata = {
            **self.server_metadata,
            **self.channel_metadata,
            "date": text.parse_datetime(
                message["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z"
            ),
            "message": message["content"],
            "message_id": message["id"],
            "author": message["author"]["username"],
            "author_id": message["author"]["id"],
        }

        all_files = []

        for attachment in message["attachments"]:
            attachment["from"] = "attachment"
            all_files.append(attachment)

        for embed in message["embeds"]:
            if embed["type"] == "gifv":
                embed["url"] = embed["video"]["url"]
            if embed["type"] in ("image", "gifv"):
                embed["from"] = "embed"
                all_files.append(embed)

        for num, file in enumerate(all_files, start=1):
            parsed_file = {
                **message_metadata,
                "type": file["from"],
                "num": num,
            }
            text.nameext_from_url(file["url"], parsed_file)
            yield Message.Url, file["url"], parsed_file

    def extract_channel_text(self, channel_id):
        api = DiscordAPI(self)
        oldest_message_id = None

        def _api_call(_):
            return api.get_channel_messages(channel_id, oldest_message_id)

        for message in api._loop_call(_api_call, DiscordAPI.MESSAGES_LIMIT):
            if message["type"] in (0, 19, 21):
                yield from self.extract_default_message(message)
            oldest_message_id = message["id"]

    def extract_channel_threads(self, channel_id):
        def _api_call(offset):
            return self.api.get_channel_threads(channel_id, offset)["threads"]

        for thread in self.api._loop_call(_api_call, DiscordAPI.THREADS_LIMIT):
            yield Message.Directory, self.parse_channel(thread["id"])
            yield from self.extract_channel_text(thread["id"])

    def extract_generic_channel(self, channel_id):
        self.channel_metadata = self.parse_channel(channel_id)

        # https://discord.com/developers/docs/resources/channel#channel-object-channel-types
        if self.channel_metadata["channel_type"] in (0, 5):
            has_text = True
            has_threads = True
        elif self.channel_metadata["channel_type"] in (1, 3, 10, 11, 12):
            has_text = True
            has_threads = False
        elif self.channel_metadata["channel_type"] in (15, 16):
            has_text = False
            has_threads = True
        else:
            raise exception.StopExtraction(
                "This channel type is not supported."
            )

        if has_text:
            yield Message.Directory, self.channel_metadata
            yield from self.extract_channel_text(
                self.channel_metadata["channel_id"]
            )

        if has_threads and (self.extract_threads or not has_text):
            yield from self.extract_channel_threads(
                self.channel_metadata["channel_id"]
            )

    def parse_channel(self, channel_id):
        channel = self.api.get_channel(channel_id)

        base_channel_metadata = {
            "channel_id": channel_id,
            "channel_type": channel["type"],
            "is_thread": "thread_metadata" in channel
        }

        if base_channel_metadata["channel_type"] in (0, 5, 10, 11, 12):
            channel_metadata = {
                "channel": channel["name"]
            }
        elif base_channel_metadata["channel_type"] in (1, 3):
            channel_metadata = {
                "recipients": (
                    [user["username"] for user in channel["recipients"]]
                ),
                "recipients_id": (
                    [user["id"] for user in channel["recipients"]]
                ),
                "channel": "DMs"
            }
        elif base_channel_metadata["channel_type"] in (15, 16):
            channel_metadata = {}
        else:
            raise exception.StopExtraction(
                "This channel type is not supported."
            )

        return {
            **self.server_metadata,
            **base_channel_metadata,
            **channel_metadata
        }

    def parse_server(self, server_id):
        server = self.api.get_server(server_id)

        self.server_metadata = {
            "server": server["name"],
            "server_id": server["id"],
            "owner_id": server["owner_id"]
        }

        return self.server_metadata


class DiscordChannelExtractor(DiscordExtractor):
    subcategory = "channel"
    directory_fmt = (
        "{category}", "{server_id}_{server}", "{channel_id}_{channel}"
    )
    pattern = BASE_PATTERN + r"/channels/(\d+)/(\d+)"
    example = (
        "https://discord.com/channels/302094807046684672/302094807046684672"
    )

    def items(self):
        server_id, channel_id = self.groups

        self.parse_server(server_id)

        yield from self.extract_generic_channel(channel_id)


class DiscordServerExtractor(DiscordExtractor):
    subcategory = "server"
    directory_fmt = (
        "{category}", "{server_id}_{server}", "{channel_id}_{channel}"
    )
    pattern = BASE_PATTERN + r"/channels/(\d+)/?$"
    example = (
        "https://discord.com/channels/302094807046684672"
    )

    def items(self):
        server_id = self.groups[0]

        self.parse_server(server_id)
        server_channels = self.api.get_server_channels(server_id)

        for channel in server_channels:
            try:
                yield from self.extract_generic_channel(channel["id"])
            except exception.StopExtraction:
                pass


class DiscordDirectMessagesExtractor(DiscordExtractor):
    subcategory = "direct-messages"
    directory_fmt = (
        "{category}", "{subcategory}", "{channel_id}_{recipients:J,}"
    )
    pattern = BASE_PATTERN + r"/channels/@me/(\d+)/?$"
    example = (
        "https://discord.com/channels/@me/302094807046684672"
    )

    def items(self):
        channel_id = self.groups[0]

        yield from self.extract_generic_channel(channel_id)


class DiscordAPI():
    """Interface for the Discord API v10

    https://discord.com/developers/docs/reference
    """

    MESSAGES_LIMIT = 100
    THREADS_LIMIT = 25

    def __init__(self, extractor):
        self.extractor = extractor
        self.token = extractor.token
        self.root = extractor.root + "/api/v10"

    def get_server(self, server_id):
        """Get server information"""
        return self._call("/guilds/" + server_id)

    def get_server_channels(self, server_id):
        """Get server channels"""
        return self._call("/guilds/" + server_id + "/channels")

    def get_channel(self, channel_id):
        """Get channel information"""
        return self._call("/channels/" + channel_id)

    def get_channel_threads(self, channel_id, offset=0):
        """Get channel threads"""
        return self._call(
            "/channels/" + channel_id + "/threads/search?"
            "sort_by=last_message_time&sort_order=desc"
            "&limit=" + str(self.THREADS_LIMIT) + "&offset=" + str(offset)
        )

    def get_channel_messages(self, channel_id, before=None):
        """Get channel messages"""
        return self._call(
            "/channels/" + channel_id +
            "/messages?limit=" + str(self.MESSAGES_LIMIT) +
            (("&before=" + before) if before else "")
        )

    def _call(self, endpoint, params=None):
        url = self.root + endpoint
        try:
            response = self.extractor.request(url, params=params, headers={
                "Authorization": self.token,
            })
        except exception.HttpError as e:
            if e.status == 401:
                self._raise_invalid_token()
            raise
        return response.json()

    @staticmethod
    def _loop_call(call, target_count):
        offset = 0
        while True:
            response = call(offset)
            yield from response
            if len(response) < target_count:
                break
            offset += len(response)

    @staticmethod
    def _raise_invalid_token():
        raise exception.AuthenticationError("""Invalid or missing token.
Please provide a valid token following these instructions:

1) Open Discord in your browser (https://discord.com/app);
2) Open your browser's Developer Tools (F12) and switch to the Network panel;
3) Reload the page and select any request going to https://discord.com/api/...;
4) In the "Headers" tab, look for an entry beginning with "Authorization: ";
6) Right-click the entry and click "copy value";
5) Paste the token in your configuration file under "extractor.discord.token",
or run this command with the -o "token=[your token]" argument.""")
