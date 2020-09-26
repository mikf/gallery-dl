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
    filename_fmt = "{id}_{title}.{extension}"
    archive_fmt = "{id}"
    root = "https://www.weasyl.com"

    @staticmethod
    def submission_data(data):
        if "media" in data and "submission" in data["media"]:
            data["url"] = data["media"]["submission"][0]["url"]
            data["extension"] = text.ext_from_url(data["url"])
            return data

    def __init__(self, match):
        Extractor.__init__(self, match)

    def get(self, category, id):
        data = self.request(
            "{}/api/{}/{}/view".format(self.root, category, id)).json()
        data["id"] = id
        if WeasylExtractor.submission_data(data):
            return data
        if "content" in data:
            data["url"] = "text:" + data["content"]
            data["extension"] = "html"
            return data

    def items(self):
        yield Message.Version, 1
        if hasattr(self, "owner_login") and self.owner_login:
            yield Message.Directory, {"owner_login": self.owner_login}

    # takes the singular form of the target ie journal, character
    def scrape(self, category):
        text = self.request("{}/{}s/{}".format(
            self.root, category, self.owner_login
        )).text

        for match in re.finditer(r'"/{}/(\d+)/([\w-]+)">[^\n]'
                                 .format(category), text):
            data = self.get(category + 's', int(match[1]))
            data["title"] = match[2]
            yield Message.Url, data["url"], data

    def submissions(self, folderid=None):
        nextid = 0
        while nextid is not None:
            url = "{}/api/users/{}/gallery?nextid={}".format(
                self.root, self.owner_login, nextid
            )
            if folderid:
                url += "&folderid={}".format(self.folderid)
            json = self.request(url).json()
            for data in json["submissions"]:
                if WeasylExtractor.submission_data(data):
                    data["id"] = data["submitid"]
                    data["folderid"] = folderid
                    # Do any submissions have more than one url? If so
                    # a urllist of the submission array urls would work.
                    yield Message.Url, data["url"], data
            nextid = json["nextid"]


class WeasylSubmissionExtractor(WeasylExtractor):
    subcategory = "submission"
    pattern = (BASE_PATTERN +
               r"(?:~[\w-]+/submissions|submission)/(\d+)/?([\w-]+)?")
    test = (
        "https://www.weasyl.com/submission/2031/a-wesley", {
            "keyword": {
                "url": "https://cdn.weasyl.com/~fiz/submissions/2031/41ebc1c29"
                       "40be928532785dfbf35c37622664d2fbb8114c3b063df969562fc5"
                       "1/fiz-a-wesley.png",
            }
        }
    )

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.submitid = int(match[1])
        if len(match.groups()) == 3:
            self.title = match[2]

    def items(self):
        yield from WeasylExtractor.items(self)
        # could use an assignment expression here in the future 3.8+
        data = self.get("submissions", self.submitid)
        if data:
            yield Message.Directory, data
            yield Message.Url, data["url"], data


class WeasylSubmissionsExtractor(WeasylExtractor):
    subcategory = "submissions"
    pattern = BASE_PATTERN + r"submissions/([\w-]+)/?$"
    test = (
        "https://www.weasyl.com/submissions/tanidareal", {
            "count": ">= 200"
        }
    )

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.owner_login = match[1]

    def items(self):
        yield from WeasylExtractor.items(self)
        yield from self.submissions()


class WeasylFolderExtractor(WeasylExtractor):
    subcategory = "folder"
    directory_fmt = ("{category}", "{owner_login}", "{folder_name}")
    pattern = BASE_PATTERN + r"submissions/([\w-]+)\?folderid=(\d+)"
    test = (
        "https://www.weasyl.com/submissions/tanidareal?folderid=7403", {
            "count": ">= 12"
        }
    )

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.owner_login = match[1]
        self.folderid = int(match[2])

    def items(self):
        yield Message.Version, 1
        iter = self.submissions(self.folderid)
        # Folder names are only on submission api calls
        msg, url, data = next(iter)
        details = self.get("submissions", data["submitid"])
        yield Message.Directory, details
        yield msg, url, data
        yield from iter


class WeasylCharacterExtractor(WeasylExtractor):
    subcategory = "character"
    pattern = BASE_PATTERN + r"character/(\d+)(?:/([\w-]+))?"
    test = (
            ("https://www.weasyl.com/character/4348/tanidareal", {
                "keyword": {
                    "url": "https://cdn.weasyl.com/static/character/"
                           "c7/f8/8e/c8/1e/ff/tanidareal-4348.submit.5084.jpg",
                    "title": "tanidareal",
                }
            }),
            ("https://www.weasyl.com/character/4348", {
                "keyword": {
                    "url": "https://cdn.weasyl.com/static/character/"
                           "c7/f8/8e/c8/1e/ff/tanidareal-4348.submit.5084.jpg",
                    "title": "TaniDaReal",
                }
            }),
        )

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.charid = int(match[1])
        if len(match.groups()) == 3:
            self.title = match[2]

    def items(self):
        yield from WeasylExtractor.items(self)
        data = self.get("characters", self.charid)
        if data:
            if hasattr(self, "title"):
                data["title"] = self.title
            yield Message.Directory, data
            yield Message.Url, data["url"], data


class WeasylCharactersExtractor(WeasylExtractor):
    subcategory = "characters"
    pattern = BASE_PATTERN + r"characters/([\w-]+)"
    test = (
        "https://www.weasyl.com/characters/tanidareal", {
            "count": ">= 2"
        }
    )

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.owner_login = match[1]

    def items(self):
        yield from WeasylExtractor.items(self)
        yield from self.scrape("character")


class WeasylJournalExtractor(WeasylExtractor):
    subcategory = "journal"
    pattern = BASE_PATTERN + r"journal/(\d+)/?([\w-]+)?"
    test = (
        ("https://www.weasyl.com/journal/17647", {
            "keyword": {
                "content":
                "<p><a>javascript:alert(42);</a></p><p>No more of that!</p>",
                "title": "bbcode",
            }
        }),
        ("https://www.weasyl.com/journal/17647/bbcode", {
            "keyword": {
                "content":
                "<p><a>javascript:alert(42);</a></p><p>No more of that!</p>",
                "title": "bbcode",
            }
        })
    )

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.journalid = int(match[1])
        if match[2]:
            self.title = match[2]

    def items(self):
        yield from WeasylExtractor.items(self)
        data = self.get("journals", self.journalid)
        if hasattr(self, "title"):
            data["title"] = self.title
        else:
            data["title"] = data["title"].lower()
        yield Message.Directory, data
        yield Message.Url, data["url"], data


class WeasylJournalsExtractor(WeasylExtractor):
    subcategory = "journals"
    pattern = BASE_PATTERN + r"journals/([\w-]+)"
    test = (
        "https://www.weasyl.com/journals/charmander", {
            "count": ">= 2",
        }
    )

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.owner_login = match[1]

    def items(self):
        yield from WeasylExtractor.items(self)
        yield from self.scrape("journal")


class WeasylUserExtractor(WeasylExtractor):
    subcategory = "user"
    pattern = BASE_PATTERN + r"~([\w-]+)"
    test = ("https://www.weasyl.com/~tanidareal", {
        })

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        self.owner_login = match[1]

    def items(self):
        yield from WeasylExtractor.items(self)
        yield from self.submissions()
        yield from self.scrape("character")
        yield from self.scrape("journal")


class WeasylFavoritesExtractor(WeasylExtractor):
    subcategory = "favorites"
    pattern = BASE_PATTERN + r"favorites(?:/([\w-]+)|\?.*userid=(\d+))"
    test = (
        ("https://www.weasyl.com/favorites/tanidareal", {
            
        }),
        ("https://www.weasyl.com/favorites?userid=5084", {
            
        }),
        ("https://www.weasyl.com/favorites?userid=12777", {
            
        }),
        ("https://www.weasyl.com/favorites?userid=12777&feature=char", {
            
        }),
        ("https://www.weasyl.com/favorites?feature=submit&userid=12777", {
            
        }),
        ("https://www.weasyl.com/favorites?userid=12777&feature=journal", {
            
        }),
    )

    def __init__(self, match):
        WeasylExtractor.__init__(self, match)
        if match[1]:
            self.owner_login = match[1]
        else:
            self.userid = int(match[2])
            match = re.search("feature=(w+)", match.string)
            if match:
                self.feature = match[1]

    def items(self):
        yield from WeasylExtractor.items(self)

        if self.owner_login:
            resp = self.request("{}/favorites/{}", self.root, self.owner_login)
            match = re.search(r"userid=(\d+)", resp.text)
            self.userid = int(match[1])
        sources = {
            "submit": "submissions",
            "char": "character",
            "journal": "journal",
        }
        groups = [self.feature] if hasattr(self,
                                           "feature") else sources.keys()
        for group in groups:
            nextid = 0
            while True:
                text = self.request(
                    "{}/favorites?userid={}&feature={}&nextid={}"
                    .format(self.userid, group, nextid).text
                )
                if not hasattr(self, "owner_login"):
                    match = re.search(r"recipient=([\w-]+)", text)
                    self.owner_login = match[1]
                    yield Message.Directory, {"owner_login": self.owner_login}
                subgroup = sources(group)
                matches = re.finditer(r'/{}/(\d+)/([\w-]+)">\n'
                                      .format(subgroup))
                if subgroup[-1] != 's':
                    subgroup += 's'
                for match in matches:
                    data = self.get(subgroup, int(match[1]))
                    data["title"] = match[2]
                    yield Message.Url, data["url"], data
                try:
                    nextid = re.search(r"nextid=(\d+)", text)[1]
                except IndexError:
                    break
