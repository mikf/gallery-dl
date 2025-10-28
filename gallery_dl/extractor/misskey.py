# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Misskey instances"""

from .common import BaseExtractor, Message, Dispatch
from .. import text


class MisskeyExtractor(BaseExtractor):
    """Base class for Misskey extractors"""
    basecategory = "misskey"
    directory_fmt = ("misskey", "{instance}", "{user[username]}")
    filename_fmt = "{category}_{id}_{file[id]}.{extension}"
    archive_fmt = "{id}_{file[id]}"

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        self.item = self.groups[-1]

    def _init(self):
        self.api = self.utils("misskey").MisskeyAPI(self)
        self.instance = self.root.rpartition("://")[2]
        self.renotes = True if self.config("renotes", False) else False
        self.replies = True if self.config("replies", True) else False

    def items(self):
        for note in self.notes():
            if "note" in note:
                note = note["note"]
            files = note.pop("files") or []
            if renote := note.get("renote"):
                if not self.renotes:
                    self.log.debug("Skipping %s (renote)", note["id"])
                    continue
                files.extend(renote.get("files") or ())

            if reply := note.get("reply"):
                if not self.replies:
                    self.log.debug("Skipping %s (reply)", note["id"])
                    continue
                files.extend(reply.get("files") or ())

            note["instance"] = self.instance
            note["instance_remote"] = note["user"]["host"]
            note["count"] = len(files)
            note["date"] = self.parse_datetime_iso(note["createdAt"])

            yield Message.Directory, note
            for note["num"], file in enumerate(files, 1):
                file["date"] = self.parse_datetime_iso(file["createdAt"])
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
    "misskey.art": {
        "root": "https://misskey.art",
        "pattern": r"misskey\.art",
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
    pattern = rf"{BASE_PATTERN}/@([^/?#]+)/?$"
    example = "https://misskey.io/@USER"

    def items(self):
        base = f"{self.root}/@{self.item}/"
        return self._dispatch_extractors((
            (MisskeyInfoExtractor      , f"{base}info"),
            (MisskeyAvatarExtractor    , f"{base}avatar"),
            (MisskeyBackgroundExtractor, f"{base}banner"),
            (MisskeyNotesExtractor     , f"{base}notes"),
        ), ("notes",))


class MisskeyNotesExtractor(MisskeyExtractor):
    """Extractor for a Misskey user's notes"""
    subcategory = "notes"
    pattern = rf"{BASE_PATTERN}/@([^/?#]+)/notes"
    example = "https://misskey.io/@USER/notes"

    def notes(self):
        return self.api.users_notes(self.api.user_id_by_username(self.item))


class MisskeyInfoExtractor(MisskeyExtractor):
    """Extractor for a Misskey user's profile data"""
    subcategory = "info"
    pattern = rf"{BASE_PATTERN}/@([^/?#]+)/info"
    example = "https://misskey.io/@USER/info"

    def items(self):
        user = self.api.users_show(self.item)
        return iter(((Message.Directory, user),))


class MisskeyAvatarExtractor(MisskeyExtractor):
    """Extractor for a Misskey user's avatar"""
    subcategory = "avatar"
    pattern = rf"{BASE_PATTERN}/@([^/?#]+)/avatar"
    example = "https://misskey.io/@USER/avatar"

    def notes(self):
        user = self.api.users_show(self.item)
        url = user.get("avatarUrl")
        return (self._make_note("avatar", user, url),) if url else ()


class MisskeyBackgroundExtractor(MisskeyExtractor):
    """Extractor for a Misskey user's banner image"""
    subcategory = "background"
    pattern = rf"{BASE_PATTERN}/@([^/?#]+)/ba(?:nner|ckground)"
    example = "https://misskey.io/@USER/banner"

    def notes(self):
        user = self.api.users_show(self.item)
        url = user.get("bannerUrl")
        return (self._make_note("background", user, url),) if url else ()


class MisskeyFollowingExtractor(MisskeyExtractor):
    """Extractor for followed Misskey users"""
    subcategory = "following"
    pattern = rf"{BASE_PATTERN}/@([^/?#]+)/following"
    example = "https://misskey.io/@USER/following"

    def items(self):
        user_id = self.api.user_id_by_username(self.item)
        for user in self.api.users_following(user_id):
            user = user["followee"]
            url = f"{self.root}/@{user['username']}"
            if (host := user["host"]) is not None:
                url = f"{url}@{host}"
            user["_extractor"] = MisskeyUserExtractor
            yield Message.Queue, url, user


class MisskeyNoteExtractor(MisskeyExtractor):
    """Extractor for images from a Note"""
    subcategory = "note"
    pattern = rf"{BASE_PATTERN}/notes/(\w+)"
    example = "https://misskey.io/notes/98765"

    def notes(self):
        return (self.api.notes_show(self.item),)


class MisskeyFavoriteExtractor(MisskeyExtractor):
    """Extractor for favorited notes"""
    subcategory = "favorite"
    pattern = rf"{BASE_PATTERN}/(?:my|api/i)/favorites"
    example = "https://misskey.io/my/favorites"

    def notes(self):
        return self.api.i_favorites()
