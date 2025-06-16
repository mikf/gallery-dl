# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Misskey instances"""

from .common import BaseExtractor, Message, Dispatch
from .. import text, exception
from ..cache import memcache


class MisskeyExtractor(BaseExtractor):
    """Base class for Misskey extractors"""
    basecategory = "misskey"
    directory_fmt = ("misskey", "{instance}", "{user[username]}")
    filename_fmt = "{category}_{id}_{file[id]}.{extension}"
    archive_fmt = "{id}_{file[id]}"

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        self.item = match.group(match.lastindex)

    def _init(self):
        self.api = MisskeyAPI(self)
        self.instance = self.root.rpartition("://")[2]
        self.renotes = self.config("renotes", False)
        self.replies = self.config("replies", True)

    def items(self):
        for note in self.notes():
            if "note" in note:
                note = note["note"]
            files = note.pop("files") or []
            renote = note.get("renote")
            if renote:
                if not self.renotes:
                    self.log.debug("Skipping %s (renote)", note["id"])
                    continue
                files.extend(renote.get("files") or ())

            reply = note.get("reply")
            if reply:
                if not self.replies:
                    self.log.debug("Skipping %s (reply)", note["id"])
                    continue
                files.extend(reply.get("files") or ())

            note["instance"] = self.instance
            note["instance_remote"] = note["user"]["host"]
            note["count"] = len(files)
            note["date"] = text.parse_datetime(
                note["createdAt"], "%Y-%m-%dT%H:%M:%S.%f%z")

            yield Message.Directory, note
            for note["num"], file in enumerate(files, 1):
                file["date"] = text.parse_datetime(
                    file["createdAt"], "%Y-%m-%dT%H:%M:%S.%f%z")
                note["file"] = file
                url = file["url"]
                yield Message.Url, url, text.nameext_from_url(url, note)

    def notes(self):
        """Return an iterable containing all relevant Note objects"""
        return ()

    def _make_note(self, type, user, url):
        # extract real URL from potential proxy
        path, sep, query = url.partition("?")
        if sep:
            url = text.parse_query(query).get("url") or path

        return {
            "id"   : type,
            "user" : user,
            "files": ({
                "id" : url.rpartition("/")[2].partition(".")[0],  # ID from URL
                "url": url,
                "createdAt": "",
            },),
            "createdAt": "",
        }


BASE_PATTERN = MisskeyExtractor.update({
    "misskey.io": {
        "root": "https://misskey.io",
        "pattern": r"misskey\.io",
    },
    "misskey.design": {
        "root": "https://misskey.design",
        "pattern": r"misskey\.design",
    },
    "lesbian.energy": {
        "root": "https://lesbian.energy",
        "pattern": r"lesbian\.energy",
    },
    "sushi.ski": {
        "root": "https://sushi.ski",
        "pattern": r"sushi\.ski",
    },
})


class MisskeyUserExtractor(Dispatch, MisskeyExtractor):
    """Extractor for all images of a Misskey user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/@([^/?#]+)/?$"
    example = "https://misskey.io/@USER"

    def items(self):
        base = "{}/@{}/".format(self.root, self.item)
        return self._dispatch_extractors((
            (MisskeyInfoExtractor      , base + "info"),
            (MisskeyAvatarExtractor    , base + "avatar"),
            (MisskeyBackgroundExtractor, base + "banner"),
            (MisskeyNotesExtractor     , base + "notes"),
        ), ("notes",))


class MisskeyNotesExtractor(MisskeyExtractor):
    """Extractor for a Misskey user's notes"""
    subcategory = "notes"
    pattern = BASE_PATTERN + r"/@([^/?#]+)/notes"
    example = "https://misskey.io/@USER/notes"

    def notes(self):
        return self.api.users_notes(self.api.user_id_by_username(self.item))


class MisskeyInfoExtractor(MisskeyExtractor):
    """Extractor for a Misskey user's profile data"""
    subcategory = "info"
    pattern = BASE_PATTERN + r"/@([^/?#]+)/info"
    example = "https://misskey.io/@USER/info"

    def items(self):
        user = self.api.users_show(self.item)
        return iter(((Message.Directory, user),))


class MisskeyAvatarExtractor(MisskeyExtractor):
    """Extractor for a Misskey user's avatar"""
    subcategory = "avatar"
    pattern = BASE_PATTERN + r"/@([^/?#]+)/avatar"
    example = "https://misskey.io/@USER/avatar"

    def notes(self):
        user = self.api.users_show(self.item)
        url = user.get("avatarUrl")
        return (self._make_note("avatar", user, url),) if url else ()


class MisskeyBackgroundExtractor(MisskeyExtractor):
    """Extractor for a Misskey user's banner image"""
    subcategory = "background"
    pattern = BASE_PATTERN + r"/@([^/?#]+)/ba(?:nner|ckground)"
    example = "https://misskey.io/@USER/banner"

    def notes(self):
        user = self.api.users_show(self.item)
        url = user.get("bannerUrl")
        return (self._make_note("background", user, url),) if url else ()


class MisskeyFollowingExtractor(MisskeyExtractor):
    """Extractor for followed Misskey users"""
    subcategory = "following"
    pattern = BASE_PATTERN + r"/@([^/?#]+)/following"
    example = "https://misskey.io/@USER/following"

    def items(self):
        user_id = self.api.user_id_by_username(self.item)
        for user in self.api.users_following(user_id):
            user = user["followee"]
            url = self.root + "/@" + user["username"]
            host = user["host"]
            if host is not None:
                url += "@" + host
            user["_extractor"] = MisskeyUserExtractor
            yield Message.Queue, url, user


class MisskeyNoteExtractor(MisskeyExtractor):
    """Extractor for images from a Note"""
    subcategory = "note"
    pattern = BASE_PATTERN + r"/notes/(\w+)"
    example = "https://misskey.io/notes/98765"

    def notes(self):
        return (self.api.notes_show(self.item),)


class MisskeyFavoriteExtractor(MisskeyExtractor):
    """Extractor for favorited notes"""
    subcategory = "favorite"
    pattern = BASE_PATTERN + r"/(?:my|api/i)/favorites"
    example = "https://misskey.io/my/favorites"

    def notes(self):
        return self.api.i_favorites()


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
        url = self.root + "/api" + endpoint
        return self.extractor.request_json(url, method="POST", json=data)

    def _pagination(self, endpoint, data):
        data["limit"] = 100
        while True:
            notes = self._call(endpoint, data)
            if not notes:
                return
            yield from notes
            data["untilId"] = notes[-1]["id"]
