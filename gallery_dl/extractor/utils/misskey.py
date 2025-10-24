# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import exception
from ...cache import memcache


class MisskeyAPI():
    """Interface for Misskey API

    https://github.com/misskey-dev/misskey
    https://misskey-hub.net/en/docs/api/
    https://misskey-hub.net/docs/api/endpoints.html
    """

    def __init__(self, extractor):
        self.root = extractor.root
        self.extractor = extractor
        self.access_token = extractor.config("access-token")

    def user_id_by_username(self, username):
        return self.users_show(username)["id"]

    def users_following(self, user_id):
        endpoint = "/users/following"
        data = {"userId": user_id}
        return self._pagination(endpoint, data)

    def users_notes(self, user_id):
        endpoint = "/users/notes"
        data = {"userId": user_id}
        return self._pagination(endpoint, data)

    @memcache(keyarg=1)
    def users_show(self, username):
        endpoint = "/users/show"
        username, _, host = username.partition("@")
        data = {"username": username, "host": host or None}
        return self._call(endpoint, data)

    def notes_show(self, note_id):
        endpoint = "/notes/show"
        data = {"noteId": note_id}
        return self._call(endpoint, data)

    def i_favorites(self):
        endpoint = "/i/favorites"
        if not self.access_token:
            raise exception.AuthenticationError()
        data = {"i": self.access_token}
        return self._pagination(endpoint, data)

    def _call(self, endpoint, data):
        url = f"{self.root}/api{endpoint}"
        return self.extractor.request_json(url, method="POST", json=data)

    def _pagination(self, endpoint, data):
        data["limit"] = 100
        data["withRenotes"] = self.extractor.renotes

        while True:
            notes = self._call(endpoint, data)
            if not notes:
                return
            yield from notes
            data["untilId"] = notes[-1]["id"]
