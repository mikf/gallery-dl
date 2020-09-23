# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.weasyl.com/"""

from .common import Extractor, Message
from .. import text
import re

BASE_PATTERN = r"(?:https://)?(?:www\.)?weasyl.com/"


class WeasylExtractor(Extractor):
    category = "weasyl"
    directory_fmt = ("{category}", "{owner_login}")
    filename_fmt = "{category}_{filename}_{date}.{extension}"
    archive_fmt = "{submitid}"
    root = "https://www.weasyl.com"

    def __init__(self, match):
        Extractor.__init__(self, match)

    @staticmethod
    def date(isodt):
        return isodt.split('T')[0]

    @staticmethod
    def populate_submission(data):
        data["url"] = data["media"]["submission"][0]["url"]
        data["date"] = WeasylExtractor.date(data["posted_at"])
        return text.nameext_from_url(data["url"], data)

    def request_submission(self, submitid):
        return self.request(
            "{}/api/submissions/{}/view".format(self.root, submitid)).json()

    def retrieve_journal(self):
        data = self.request(
            "{}/api/journals/{}/view".format(self.root, self.journalid)).json()
        data["date"] = self.date(data["posted_at"])
        data["extension"] = "html"
        data["html"] = "text:" + data["content"]
        return data

    def submissions(self):
        nextid = 0
        while nextid is not None:
            url = "{}/api/users/{}/gallery?nextid={}".format(
                self.root, self.owner_login, nextid
            )
            folderid = self.folderid if hasattr(self, "folderid") else None
            if folderid:
                url += "&folderid={}".format(self.folderid)
            json = self.request(url).json()
            for data in json["submissions"]:
                self.populate_submission(data)
                data["folderid"] = folderid
                # Do any submissions have more than one url? If so
                # a urllist of the submission array urls would work.
                yield Message.Url, data["url"], data
            nextid = json["nextid"]


class WeasylSubmissionExtractor(WeasylExtractor):
    subcategory = "submission"
    pattern = (BASE_PATTERN +
               r"(?:~[\w\d]+/submissions|submission)/(\d+)/?([\w\d-]+)?")
    test = (
        "https://www.weasyl.com/submission/2031/a-wesley", {
            "keyword": {
                "url": "https://cdn.weasyl.com/~fiz/submissions/2031/41ebc1c29"
                       "40be928532785dfbf35c37622664d2fbb8114c3b063df969562fc5"
                       "1/fiz-a-wesley.png",
                "date": "2012-04-20",
            }
        }
    )

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.submitid = int(match.group(1))
        if len(match.groups()) == 3:
            self.title = match.group(2)

    def items(self):
        yield Message.Version, 1
        data = self.request_submission(self.submitid)
        yield Message.Directory, data
        self.populate_submission(data)
        yield Message.Url, data["url"], data


class WeasylSubmissionsExtractor(WeasylExtractor):
    subcategory = "submissions"
    pattern = BASE_PATTERN + r"(?:~([\w\d]+)/?|submissions/([\w\d]+))$"
    test = (
        ("https://www.weasyl.com/~tanidareal", {
            "count": ">= 200"
        }),
        ("https://www.weasyl.com/submissions/tanidareal", {
            "count": ">= 200"
        })
    )

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.owner_login = match.group(1) if match.group(1) else match.group(2)

    def items(self):
        yield Message.Version, 1
        yield Message.Directory, {"owner_login": self.owner_login}
        yield from self.submissions()


class WeasylFolderExtractor(WeasylExtractor):
    subcategory = "folder"
    directory_fmt = ("{category}", "{owner_login}", "{folder_name}")
    pattern = BASE_PATTERN + r"submissions/([\w\d]+)\?folderid=(\d+)"
    test = (
        "https://www.weasyl.com/submissions/tanidareal?folderid=7403", {
            "count": ">= 12"
        }
    )

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.owner_login = match.group(1)
        self.folderid = int(match.group(2))

    def items(self):
        yield Message.Version, 1
        iter = self.submissions()
        # Folder names are only on single submission api calls
        msg, url, data = next(iter)
        details = self.request_submission(data["submitid"])
        yield Message.Directory, details
        yield msg, url, data
        yield from iter


class WeasylJournalExtractor(WeasylExtractor):
    subcategory = "journal"
    filename_fmt = "{category}_{owner_login}_{title}_{date}.{extension}"
    archive_fmt = "{journalid}"
    pattern = BASE_PATTERN + r"journal/(\d+)/?([\w\d-]+)?"
    test = (
        ("https://www.weasyl.com/journal/17647", {
            "keyword": {
                "content":
                "<p><a>javascript:alert(42);</a></p><p>No more of that!</p>",
                "title": "bbcode",
                "date": "2013-09-19",
            }
        }),
        ("https://www.weasyl.com/journal/17647/bbcode", {
            "keyword": {
                "content":
                "<p><a>javascript:alert(42);</a></p><p>No more of that!</p>",
                "title": "bbcode",
                "date": "2013-09-19",
            }
        })
    )

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.journalid = int(match.group(1))
        if match.group(2):
            self.title = match.group(2)

    def items(self):
        yield Message.Version, 1
        data = self.retrieve_journal()
        if hasattr(self, "title"):
            data["title"] = self.title
        else:
            data["title"] = data["title"].lower()
        yield Message.Directory, data
        yield Message.Url, data["html"], data


class WeasylJournalsExtractor(WeasylExtractor):
    subcategory = "journals"
    filename_fmt = "{category}_{owner_login}_{title}_{date}.{extension}"
    archive_fmt = "{journalid}"
    pattern = BASE_PATTERN + r"journals/([\w\d]+)"
    test = (
        "https://www.weasyl.com/journals/charmander", {
            "count": ">= 2",
        }
    )

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.owner_login = match.group(1)

    def items(self):
        yield Message.Version, 1
        yield Message.Directory, {"owner_login": self.owner_login}
        response = self.request("{}/journals/{}".format(
            self.root, self.owner_login
        ))

        for journal in re.finditer(r'"/journal/(\d+)/([\w\d-]+)"',
                                   response.text):
            self.journalid = int(journal.group(1))
            data = self.retrieve_journal()
            data["title"] = journal.group(2)
            yield Message.Url, data["html"], data
