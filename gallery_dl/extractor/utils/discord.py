# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import exception


class DiscordAPI():
    """Interface for the Discord API v10

    https://discord.com/developers/docs/reference
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = f"{extractor.root}/api/v10"
        self.headers = {"Authorization": extractor.token}

    def get_server(self, server_id):
        """Get server information"""
        return self._call(f"/guilds/{server_id}")

    def get_server_channels(self, server_id):
        """Get server channels"""
        return self._call(f"/guilds/{server_id}/channels")

    def get_channel(self, channel_id):
        """Get channel information"""
        return self._call(f"/channels/{channel_id}")

    def get_channel_threads(self, channel_id):
        """Get channel threads"""
        THREADS_BATCH = 25

        def _method(offset):
            return self._call(f"/channels/{channel_id}/threads/search", {
                "sort_by": "last_message_time",
                "sort_order": "desc",
                "limit": THREADS_BATCH,
                "offset": + offset,
            }).get("threads", [])

        return self._pagination(_method, THREADS_BATCH)

    def get_channel_messages(self, channel_id):
        """Get channel messages"""
        MESSAGES_BATCH = 100

        before = None

        def _method(_):
            nonlocal before
            messages = self._call(f"/channels/{channel_id}/messages", {
                "limit": MESSAGES_BATCH,
                "before": before
            })
            if messages:
                before = messages[-1]["id"]
            return messages

        return self._pagination(_method, MESSAGES_BATCH)

    def get_message(self, channel_id, message_id):
        """Get message information"""
        return self._call(f"/channels/{channel_id}/messages", {
            "limit": 1,
            "around": message_id
        })[0]

    def _call(self, endpoint, params=None):
        url = f"{self.root}{endpoint}"
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

    def _raise_invalid_token(self):
        raise exception.AuthenticationError("""Invalid or missing token.
Please provide a valid token following these instructions:

1) Open Discord in your browser (https://discord.com/app);
2) Open your browser's Developer Tools (F12) and switch to the Network panel;
3) Reload the page and select any request going to https://discord.com/api/...;
4) In the "Headers" tab, look for an entry beginning with "Authorization: ";
5) Right-click the entry and click "Copy Value";
6) Paste the token in your configuration file under "extractor.discord.token",
or run this command with the -o "token=[your token]" argument.""")
