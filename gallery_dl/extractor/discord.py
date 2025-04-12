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
    directory_fmt = ("{category}", "{server_id}_{server}",
                     "{channel_id}_{channel}")
    filename_fmt = "{message_id}_{num:>02}_{filename}.{extension}"
    archive_fmt = "{message_id}_{num}"

    cdn_fmt = "https://cdn.discordapp.com/{}/{}/{}.png?size=4096"

    server_metadata = {}
    server_channels_metadata = {}

    def _init(self):
        self.token = self.config("token")
        self.enabled_embeds = self.config("embeds", ["image", "gifv", "video"])
        self.enabled_threads = self.config("threads", True)
        self.api = DiscordAPI(self)

    def extract_message_text(self, message):
        text_content = [message["content"]]

        for embed in message["embeds"]:
            if embed["type"] == "rich":
                try:
                    text_content.append(embed["author"]["name"])
                except Exception:
                    pass
                text_content.append(embed.get("title", ""))
                text_content.append(embed.get("description", ""))

                for field in embed.get("fields", []):
                    text_content.append(field.get("name", ""))
                    text_content.append(field.get("value", ""))

                try:
                    text_content.append(embed["footer"]["text"])
                except Exception:
                    pass

        if message.get("poll"):
            text_content.append(message["poll"]["question"]["text"])
            for answer in message["poll"]["answers"]:
                text_content.append(answer["poll_media"]["text"])

        return "\n".join(t for t in text_content if t)

    def extract_message(self, message):
        # https://discord.com/developers/docs/resources/message#message-object-message-types
        if message["type"] in (0, 19, 21):
            message_metadata = {}
            message_metadata.update(self.server_metadata)
            message_metadata.update(
                self.server_channels_metadata[message["channel_id"]])
            message_metadata.update({
                "author": message["author"]["username"],
                "author_id": message["author"]["id"],
                "author_files": [],
                "message": self.extract_message_text(message),
                "message_id": message["id"],
                "date": text.parse_datetime(
                    message["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z"
                ),
                "files": []
            })

            for icon_type, icon_path in (
                ("avatar", "avatars"),
                ("banner", "banners")
            ):
                if message["author"].get(icon_type):
                    message_metadata["author_files"].append({
                        "url": self.cdn_fmt.format(
                            icon_path,
                            message_metadata["author_id"],
                            message["author"][icon_type]
                        ),
                        "filename": icon_type,
                        "extension": "png",
                    })

            for attachment in message["attachments"]:
                message_metadata["files"].append({
                    "url": attachment["url"],
                    "type": "attachment",
                })

            for embed in message["embeds"]:
                if embed["type"] in self.enabled_embeds:
                    for field in ("video", "image", "thumbnail"):
                        if field not in embed:
                            continue
                        url = embed[field].get("proxy_url")
                        if url is not None:
                            message_metadata["files"].append({
                                "url": url,
                                "type": "embed",
                            })
                            break

            for num, file in enumerate(message_metadata["files"], start=1):
                text.nameext_from_url(file["url"], file)
                file["num"] = num

            yield Message.Directory, message_metadata

            for file in message_metadata["files"]:
                message_metadata_file = message_metadata.copy()
                message_metadata_file.update(file)
                yield Message.Url, file["url"], message_metadata_file

    def extract_channel_text(self, channel_id):
        for message in self.api.get_channel_messages(channel_id):
            yield from self.extract_message(message)

    def extract_channel_threads(self, channel_id):
        for thread in self.api.get_channel_threads(channel_id):
            id = self.parse_channel(thread)["channel_id"]
            yield from self.extract_channel_text(id)

    def extract_channel(self, channel_id, safe=False):
        try:
            if channel_id not in self.server_channels_metadata:
                self.parse_channel(self.api.get_channel(channel_id))

            channel_type = (
                self.server_channels_metadata[channel_id]["channel_type"]
            )

            # https://discord.com/developers/docs/resources/channel#channel-object-channel-types
            if channel_type in (0, 5):
                yield from self.extract_channel_text(channel_id)
                if self.enabled_threads:
                    yield from self.extract_channel_threads(channel_id)
            elif channel_type in (1, 3, 10, 11, 12):
                yield from self.extract_channel_text(channel_id)
            elif channel_type in (15, 16):
                yield from self.extract_channel_threads(channel_id)
            elif channel_type in (4,):
                for channel in self.server_channels_metadata.copy().values():
                    if channel["parent_id"] == channel_id:
                        yield from self.extract_channel(
                            channel["channel_id"], safe=True)
            elif not safe:
                raise exception.StopExtraction(
                    "This channel type is not supported."
                )
        except exception.HttpError as exc:
            if not (exc.status == 403 and safe):
                raise

    def parse_channel(self, channel):
        parent_id = channel.get("parent_id")
        channel_metadata = {
            "channel": channel.get("name", ""),
            "channel_id": channel.get("id"),
            "channel_type": channel.get("type"),
            "channel_topic": channel.get("topic", ""),
            "parent_id": parent_id,
            "is_thread": "thread_metadata" in channel
        }

        if parent_id in self.server_channels_metadata:
            parent_metadata = self.server_channels_metadata[parent_id]
            channel_metadata.update({
                "parent": parent_metadata["channel"],
                "parent_type": parent_metadata["channel_type"]
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

        channel_id = channel_metadata["channel_id"]

        self.server_channels_metadata[channel_id] = channel_metadata
        return channel_metadata

    def parse_server(self, server):
        self.server_metadata = {
            "server": server["name"],
            "server_id": server["id"],
            "server_files": [],
            "owner_id": server["owner_id"]
        }

        for icon_type, icon_path in (
            ("icon", "icons"),
            ("banner", "banners"),
            ("splash", "splashes"),
            ("discovery_splash", "discovery-splashes")
        ):
            if server.get(icon_type):
                self.server_metadata["server_files"].append({
                    "url": self.cdn_fmt.format(
                        icon_path,
                        self.server_metadata["server_id"],
                        server[icon_type]
                    ),
                    "filename": icon_type,
                    "extension": "png",
                })

        return self.server_metadata

    def build_server_and_channels(self, server_id):
        self.parse_server(self.api.get_server(server_id))

        for channel in sorted(
            self.api.get_server_channels(server_id),
            key=lambda ch: ch["type"] != 4
        ):
            self.parse_channel(channel)


class DiscordChannelExtractor(DiscordExtractor):
    subcategory = "channel"
    pattern = BASE_PATTERN + r"/channels/(\d+)/(?:\d+/threads/)?(\d+)/?$"
    example = "https://discord.com/channels/1234567890/9876543210"

    def items(self):
        server_id, channel_id = self.groups

        self.build_server_and_channels(server_id)

        return self.extract_channel(channel_id)


class DiscordMessageExtractor(DiscordExtractor):
    subcategory = "message"
    pattern = BASE_PATTERN + r"/channels/(\d+)/(\d+)/(\d+)/?$"
    example = "https://discord.com/channels/1234567890/9876543210/2468013579"

    def items(self):
        server_id, channel_id, message_id = self.groups

        self.build_server_and_channels(server_id)

        if channel_id not in self.server_channels_metadata:
            self.parse_channel(self.api.get_channel(channel_id))

        return self.extract_message(
            self.api.get_message(channel_id, message_id))


class DiscordServerExtractor(DiscordExtractor):
    subcategory = "server"
    pattern = BASE_PATTERN + r"/channels/(\d+)/?$"
    example = "https://discord.com/channels/1234567890"

    def items(self):
        server_id = self.groups[0]

        self.build_server_and_channels(server_id)

        for channel in self.server_channels_metadata.copy().values():
            if channel["channel_type"] in (0, 5, 15, 16):
                yield from self.extract_channel(
                    channel["channel_id"], safe=True)


class DiscordDirectMessagesExtractor(DiscordExtractor):
    subcategory = "direct-messages"
    directory_fmt = ("{category}", "Direct Messages",
                     "{channel_id}_{recipients:J,}")
    pattern = BASE_PATTERN + r"/channels/@me/(\d+)/?$"
    example = "https://discord.com/channels/@me/1234567890"

    def items(self):
        return self.extract_channel(self.groups[0])


class DiscordDirectMessageExtractor(DiscordExtractor):
    subcategory = "direct-message"
    directory_fmt = ("{category}", "Direct Messages",
                     "{channel_id}_{recipients:J,}")
    pattern = BASE_PATTERN + r"/channels/@me/(\d+)/(\d+)/?$"
    example = "https://discord.com/channels/@me/1234567890/9876543210"

    def items(self):
        channel_id, message_id = self.groups

        self.parse_channel(self.api.get_channel(channel_id))

        return self.extract_message(
            self.api.get_message(channel_id, message_id))


class DiscordAPI():
    """Interface for the Discord API v10

    https://discord.com/developers/docs/reference
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = extractor.root + "/api/v10"
        self.headers = {"Authorization": extractor.token}

    def get_server(self, server_id):
        """Get server information"""
        return self._call("/guilds/" + server_id)

    def get_server_channels(self, server_id):
        """Get server channels"""
        return self._call("/guilds/" + server_id + "/channels")

    def get_channel(self, channel_id):
        """Get channel information"""
        return self._call("/channels/" + channel_id)

    def get_channel_threads(self, channel_id):
        """Get channel threads"""
        THREADS_BATCH = 25

        def _method(offset):
            return self._call("/channels/" + channel_id + "/threads/search", {
                "sort_by": "last_message_time",
                "sort_order": "desc",
                "limit": THREADS_BATCH,
                "offset": + offset,
            })["threads"]

        return self._pagination(_method, THREADS_BATCH)

    def get_channel_messages(self, channel_id):
        """Get channel messages"""
        MESSAGES_BATCH = 100

        before = None

        def _method(_):
            nonlocal before
            messages = self._call("/channels/" + channel_id + "/messages", {
                "limit": MESSAGES_BATCH,
                "before": before
            })
            if messages:
                before = messages[-1]["id"]
            return messages

        return self._pagination(_method, MESSAGES_BATCH)

    def get_message(self, channel_id, message_id):
        """Get message information"""
        return self._call("/channels/" + channel_id + "/messages", {
            "limit": 1,
            "around": message_id
        })[0]

    def _call(self, endpoint, params=None):
        url = self.root + endpoint
        try:
            response = self.extractor.request(
                url, params=params, headers=self.headers)
        except exception.HttpError as exc:
            if exc.status == 401:
                self._raise_invalid_token()
            raise
        return response.json()

    def _pagination(self, method, batch):
        offset = 0
        while True:
            data = method(offset)
            yield from data
            if len(data) < batch:
                return
            offset += len(data)

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
