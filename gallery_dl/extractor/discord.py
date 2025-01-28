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
    all_channels_metadata = {}

    def _init(self):
        self.token = self.config("token")
        self.extract_threads = self.config("threads", True)
        self.api = DiscordAPI(self)

    def extract_message(self, message):
        # https://discord.com/developers/docs/resources/message#message-object-message-types
        if message["type"] in (0, 19, 21):
            message_metadata = {
                **self.server_metadata,
                **self.all_channels_metadata[message["channel_id"]],
                "date": text.parse_datetime(
                    message["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z"
                ),
                "message": message["content"],
                "message_id": message["id"],
                "author": message["author"]["username"],
                "author_id": message["author"]["id"],
                "files": []
            }

            for attachment in message["attachments"]:
                message_metadata["files"].append({
                    "url": attachment["url"],
                    "type": "attachment"
                })

            for embed in message["embeds"]:
                url = None
                if embed["type"] in ("image",):
                    url = embed["thumbnail"].get("proxy_url")
                elif embed["type"] in ("gifv", "video"):
                    url = embed["video"].get("proxy_url")

                if url is not None:
                    message_metadata["files"].append({
                        "url": url,
                        "type": "embed"
                    })

            for num, file in enumerate(message_metadata["files"], start=1):
                text.nameext_from_url(file["url"], file)
                file["num"] = num

            yield Message.Directory, message_metadata

            for file in message_metadata["files"]:
                parsed_file = {
                    **message_metadata,
                    **file
                }
                yield Message.Url, file["url"], parsed_file

    def extract_channel_text(self, channel_id):
        api = DiscordAPI(self)
        oldest_message_id = None

        def _api_call(_):
            return api.get_channel_messages(channel_id, oldest_message_id)

        for message in api._loop_call(_api_call, DiscordAPI.MESSAGES_LIMIT):
            yield from self.extract_message(message)
            oldest_message_id = message["id"]

    def extract_channel_threads(self, channel_id):
        def _api_call(offset):
            return self.api.get_channel_threads(channel_id, offset)["threads"]

        for thread in self.api._loop_call(_api_call, DiscordAPI.THREADS_LIMIT):
            self.parse_channel(thread["id"])
            yield from self.extract_channel_text(thread["id"])

    def extract_category_channels(self, channel_id):
        for channel in self.api.get_server_channels(
            self.server_metadata["server_id"]
        ):
            if channel["parent_id"] == channel_id:
                yield from self.extract_generic_channel(
                    channel["id"], safe=True
                )

    def extract_generic_channel(self, channel_id, safe=False):
        try:
            channel_type = self.parse_channel(channel_id)["channel_type"]

            has_text = False
            has_threads = False

            # https://discord.com/developers/docs/resources/channel#channel-object-channel-types
            if channel_type in (0, 5):
                has_text = True
                has_threads = self.extract_threads
            elif channel_type in (1, 3, 10, 11, 12):
                has_text = True
            elif channel_type in (4,):
                yield from self.extract_category_channels(channel_id)
            elif channel_type in (15, 16):
                has_threads = True
            elif not safe:
                raise exception.StopExtraction(
                    "This channel type is not supported."
                )

            if has_text:
                yield from self.extract_channel_text(channel_id)
            if has_threads:
                yield from self.extract_channel_threads(channel_id)
        except exception.HttpError as e:
            if not (e.status == 403 and safe):
                raise

    def parse_channel(self, channel_id):
        if channel_id in self.all_channels_metadata:
            return self.all_channels_metadata[channel_id]

        channel = self.api.get_channel(channel_id)

        channel_metadata = {
            "channel": channel.get("name"),
            "channel_id": channel_id,
            "channel_type": channel.get("type"),
            "channel_topic": channel.get("topic", ""),
            "parent_id": channel.get("parent_id"),
            "is_thread": "thread_metadata" in channel
        }

        if channel_metadata["parent_id"] in self.all_channels_metadata:
            parent_channel_metadata = (
                self.all_channels_metadata[channel_metadata["parent_id"]]
            )
            channel_metadata.update({
                "parent": parent_channel_metadata["channel"],
                "parent_type": parent_channel_metadata["channel_type"]
            })

        if channel_metadata["channel_type"] in (1, 3):
            channel_metadata.update({
                "channel": "DMs",
                "recipients": (
                    [user["username"] for user in channel["recipients"]]
                ),
                "recipients_id": (
                    [user["id"] for user in channel["recipients"]]
                )
            })

        self.all_channels_metadata[channel_id] = {
            **self.server_metadata,
            **channel_metadata
        }

        return self.all_channels_metadata[channel_id]

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
    pattern = BASE_PATTERN + r"/channels/(\d+)/(\d+)(?:/threads/(\d+))?"
    example = (
        "https://discord.com/channels/302094807046684672/302094807046684672"
    )

    def items(self):
        server_id = self.groups[0]
        channel_id = self.groups[2] or self.groups[1]

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
            if channel["type"] in (0, 5, 15, 16):
                yield from self.extract_generic_channel(
                    channel["id"], safe=True
                )


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
5) Right-click the entry and click "Copy Value";
6) Paste the token in your configuration file under "extractor.discord.token",
or run this command with the -o "token=[your token]" argument.""")
