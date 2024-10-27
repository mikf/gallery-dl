# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.weasyl.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https://)?(?:www\.)?weasyl.com/"


class WeasylExtractor(Extractor):
    category = "weasyl"
    directory_fmt = ("{category}", "{owner_login}")
    filename_fmt = "{submitid} {title}.{extension}"
    archive_fmt = "{submitid}"
    root = "https://www.weasyl.com"

    @staticmethod
    def populate_submission(data):
        # Some submissions don't have content and can be skipped
        if "submission" in data["media"]:
            data["url"] = data["media"]["submission"][0]["url"]
            data["date"] = text.parse_datetime(
                data["posted_at"][:19], "%Y-%m-%dT%H:%M:%S")
            text.nameext_from_url(data["url"], data)
            return True
        return False

    def _init(self):
        self.session.headers['X-Weasyl-API-Key'] = self.config("api-key")

    def request_submission(self, submitid):
        return self.request(
            "{}/api/submissions/{}/view".format(self.root, submitid)).json()

    def retrieve_journal(self, journalid):
        data = self.request(
            "{}/api/journals/{}/view".format(self.root, journalid)).json()
        data["extension"] = "html"
        data["html"] = "text:" + data["content"]
        data["date"] = text.parse_datetime(data["posted_at"])
        return data

    def submissions(self, owner_login, folderid=None):
        metadata = self.config("metadata")
        url = "{}/api/users/{}/gallery".format(self.root, owner_login)
        params = {
            "nextid"  : None,
            "folderid": folderid,
        }

        while True:
            data = self.request(url, params=params).json()
            for submission in data["submissions"]:
                if metadata:
                    submission = self.request_submission(
                        submission["submitid"])
                if self.populate_submission(submission):
                    submission["folderid"] = folderid
                    # Do any submissions have more than one url? If so
                    # a urllist of the submission array urls would work.
                    yield Message.Url, submission["url"], submission
            if not data["nextid"]:
                return
            params["nextid"] = data["nextid"]


class WeasylSubmissionExtractor(WeasylExtractor):
    subcategory = "submission"
    pattern = BASE_PATTERN + r"(?:~[\w~-]+/submissions|submission)/(\d+)"
    example = "https://www.weasyl.com/~USER/submissions/12345/TITLE"

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.submitid = match.group(1)

    def items(self):
        data = self.request_submission(self.submitid)
        if self.populate_submission(data):
            yield Message.Directory, data
            yield Message.Url, data["url"], data


class WeasylSubmissionsExtractor(WeasylExtractor):
    subcategory = "submissions"
    pattern = BASE_PATTERN + r"(?:~|submissions/)([\w~-]+)/?$"
    example = "https://www.weasyl.com/submissions/USER"

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.owner_login = match.group(1)

    def items(self):
        yield Message.Directory, {"owner_login": self.owner_login}
        yield from self.submissions(self.owner_login)


class WeasylFolderExtractor(WeasylExtractor):
    subcategory = "folder"
    directory_fmt = ("{category}", "{owner_login}", "{folder_name}")
    pattern = BASE_PATTERN + r"submissions/([\w~-]+)\?folderid=(\d+)"
    example = "https://www.weasyl.com/submissions/USER?folderid=12345"

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.owner_login, self.folderid = match.groups()

    def items(self):
        iter = self.submissions(self.owner_login, self.folderid)
        # Folder names are only on single submission api calls
        msg, url, data = next(iter)
        details = self.request_submission(data["submitid"])
        yield Message.Directory, details
        yield msg, url, data
        yield from iter


class WeasylJournalExtractor(WeasylExtractor):
    subcategory = "journal"
    filename_fmt = "{journalid} {title}.{extension}"
    archive_fmt = "{journalid}"
    pattern = BASE_PATTERN + r"journal/(\d+)"
    example = "https://www.weasyl.com/journal/12345"

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.journalid = match.group(1)

    def items(self):
        data = self.retrieve_journal(self.journalid)
        yield Message.Directory, data
        yield Message.Url, data["html"], data


class WeasylJournalsExtractor(WeasylExtractor):
    subcategory = "journals"
    filename_fmt = "{journalid} {title}.{extension}"
    archive_fmt = "{journalid}"
    pattern = BASE_PATTERN + r"journals/([\w~-]+)"
    example = "https://www.weasyl.com/journals/USER"

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.owner_login = match.group(1)

    def items(self):
        yield Message.Directory, {"owner_login": self.owner_login}

        url = "{}/journals/{}".format(self.root, self.owner_login)
        page = self.request(url).text
        for journalid in text.extract_iter(page, 'href="/journal/', '/'):
            data = self.retrieve_journal(journalid)
            yield Message.Url, data["html"], data


class WeasylFavoriteExtractor(WeasylExtractor):
    subcategory = "favorite"
    directory_fmt = ("{category}", "{user}", "Favorites")
    pattern = BASE_PATTERN + r"favorites(?:\?userid=(\d+)|/([^/?#]+))"
    example = "https://www.weasyl.com/favorites?userid=12345"

    def items(self):
        userid, username = self.groups
        owner_login = lastid = None

        if username:
            owner_login = username
            path = "/favorites/" + username
        else:
            path = "/favorites"
        params = {
            "userid" : userid,
            "feature": "submit",
        }

        while True:
            page = self.request(self.root + path, params=params).text
            pos = page.index('id="favorites-content"')

            if not owner_login:
                owner_login = text.extr(page, '<a href="/~', '"')

            for submitid in text.extract_iter(page, "/submissions/", "/", pos):
                if submitid == lastid:
                    continue
                lastid = submitid

                submission = self.request_submission(submitid)
                if self.populate_submission(submission):
                    submission["user"] = owner_login
                    yield Message.Directory, submission
                    yield Message.Url, submission["url"], submission

            try:
                pos = page.index('">Next (', pos)
            except ValueError:
                return
            path = text.unescape(text.rextract(page, 'href="', '"', pos)[0])
            params = None
