# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.deviantart.com/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
import itertools
import datetime
import time
import re


class DeviantartExtractor(Extractor):
    """Base class for deviantart extractors"""
    category = "deviantart"
    directory_fmt = ["{category}", "{author[username]}"]
    filename_fmt = "{category}_{index}_{title}.{extension}"

    def __init__(self):
        Extractor.__init__(self)
        self.api = DeviantartAPI(self)
        self.offset = 0

    def skip(self, num):
        self.offset += num
        return num

    def items(self):
        last_author = None
        yield Message.Version, 1
        for deviation in self.deviations():
            self.prepare(deviation)

            try:
                author = deviation["author"]
            except KeyError:
                author = None
                deviation["author"] = {"username": "", "userid": "",
                                       "usericon": "", "type": ""}
            if author != last_author:
                yield Message.Directory, deviation
                last_author = author

            if "content" in deviation:
                yield self.commit(deviation, deviation["content"])

            if "videos" in deviation:
                video = max(deviation["videos"],
                            key=lambda x: int(x["quality"][:-1]))
                yield self.commit(deviation, video)

            if "flash" in deviation:
                yield self.commit(deviation, deviation["flash"])

            if "excerpt" in deviation:
                journal = self.api.deviation_content(deviation["deviationid"])
                yield self.commit_journal(deviation, journal)

    def deviations(self):
        """Return an iterable containing all relevant Deviation-objects"""
        return []

    @staticmethod
    def prepare(deviation):
        """Adjust the contents of a Deviation-object"""
        for key in ("stats", "preview", "is_favourited", "allows_comments"):
            if key in deviation:
                del deviation[key]
        try:
            deviation["index"] = deviation["url"].rsplit("-", 1)[1]
        except KeyError:
            deviation["index"] = 0

    @staticmethod
    def commit(deviation, target):
        url = target["src"]
        deviation["target"] = text.nameext_from_url(url, target.copy())
        deviation["extension"] = deviation["target"]["extension"]
        return Message.Url, url, deviation

    @staticmethod
    def commit_journal(deviation, journal):
        title = text.escape(deviation["title"])
        url = deviation["url"]
        thumbs = deviation["thumbs"]
        html = journal["html"]
        date = datetime.datetime.utcfromtimestamp(deviation["published_time"])
        shadow = SHADOW_TEMPLATE.format_map(thumbs[0]) if thumbs else ""

        if "css" in journal:
            css, cls = journal["css"], "withskin"
        else:
            css, cls = "", "journal-green"

        if html.find('<div class="boxtop journaltop">', 0, 250) != -1:
            needle = '<div class="boxtop journaltop">'
            header = HEADER_CUSTOM_TEMPLATE.format(
                title=title, url=url, date=str(date),
            )
        else:
            needle = '<div usr class="gr">'
            catlist = deviation["category_path"].split("/")
            categories = " / ".join(
                ('<span class="crumb"><a href="http://www.deviantart.com/{}/">'
                 '<span>{}</span></a></span>').format(cpath, cat.capitalize())
                for cat, cpath in zip(
                    catlist,
                    itertools.accumulate(catlist, lambda t, c: t + "/" + c)
                )
            )
            header = HEADER_TEMPLATE.format(
                title=title,
                url=url,
                userurl=url[:url.find("/", 8)],
                username=deviation["author"]["username"],
                date=str(date),
                categories=categories,
            )

        html = JOURNAL_TEMPLATE.format(
            title=title,
            html=html.replace(needle, header, 1),
            shadow=shadow,
            css=css,
            cls=cls,
        )

        deviation["extension"] = "htm"
        return Message.Url, html, deviation


class DeviantartGalleryExtractor(DeviantartExtractor):
    """Extractor for all deviations from an artist's gallery"""
    subcategory = "gallery"
    pattern = [r"(?:https?://)?([^.]+)\.deviantart\.com(?:/gallery)?/?$"]
    test = [("http://shimoda7.deviantart.com/gallery/", {
        "url": "63bfa8efba199e27181943c9060f6770f91a8441",
        "keyword": "e017b1eec5d052dedbb219259ae8c01d0db678a3",
    })]

    def __init__(self, match):
        DeviantartExtractor.__init__(self)
        self.user = match.group(1)

    def deviations(self):
        return self.api.gallery_all(self.user, self.offset)


class DeviantartDeviationExtractor(DeviantartExtractor):
    """Extractor for single deviations"""
    subcategory = "deviation"
    pattern = [(r"(?:https?://)?([^.]+\.deviantart\.com/"
                r"(?:art|journal)/[^/?&#]+-\d+)"),
               r"(?:https?://)?(sta\.sh/[a-z0-9]+)"]
    test = [
        (("http://shimoda7.deviantart.com/art/"
          "For-the-sake-of-a-memory-10073852"), {
            "url": "71345ce3bef5b19bd2a56d7b96e6b5ddba747c2e",
            "keyword": "597be070582e105489e82cce531888d07f9d45b1",
            "content": "6a7c74dc823ebbd457bdd9b3c2838a6ee728091e",
        }),
        ("https://zzz.deviantart.com/art/zzz-1234567890", {
            "exception": exception.NotFoundError,
        }),
        ("http://sta.sh/01ijs78ebagf", {
            "url": "1692cd075059d24657a01b954413c84a56e2de8f",
            "keyword": "659fdf02d7de2e9181468286de19c526348ca1a1",
        }),
        ("http://sta.sh/abcdefghijkl", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        DeviantartExtractor.__init__(self)
        self.url = "https://" + match.group(1)

    def deviations(self):
        response = self.session.get(self.url)
        deviation_id = text.extract(response.text, '//deviation/', '"')[0]
        if response.status_code != 200 or not deviation_id:
            raise exception.NotFoundError("image")
        return (self.api.deviation(deviation_id),)


class DeviantartFavoriteExtractor(DeviantartExtractor):
    """Extractor for an artist's favourites"""
    subcategory = "favorite"
    directory_fmt = ["{category}", "{subcategory}",
                     "{collection[owner]} - {collection[title]}"]
    pattern = [r"(?:https?://)?([^.]+)\.deviantart\.com/favourites"
               r"(?:/((\d+)/([^/?]+)|\?catpath=/))?"]
    test = [
        ("http://rosuuri.deviantart.com/favourites/58951174/Useful", {
            "url": "65d070eae215b9375b4437a1ab4659efdad204e3",
            "keyword": "e5f3aaf35274e976ae81c5b151e650eea1dde775",
        }),
        ("http://h3813067.deviantart.com/favourites/", {
            "url": "71345ce3bef5b19bd2a56d7b96e6b5ddba747c2e",
            "keyword": "f0c557470ca850da65ec94804a20551b7bda7af5",
            "content": "6a7c74dc823ebbd457bdd9b3c2838a6ee728091e",
        }),
    ]

    def __init__(self, match):
        DeviantartExtractor.__init__(self)
        self.user, path, self.favid, self.favname = match.groups()
        if not self.favname:
            if path == "?catpath=/":
                self.favname = "All"
                self.deviations = self._deviations_all
            else:
                self.favname = "Featured"
        self.collection = {
            "owner": self.user,
            "title": self.favname,
            "index": self.favid or 0,
        }

    def deviations(self):
        regex = re.compile(self.favname.replace("-", ".") + "$")
        for folder in self.api.collections_folders(self.user):
            if regex.match(folder["name"]):
                self.collection["title"] = folder["name"]
                return self.api.collections(
                    self.user, folder["folderid"], self.offset)
        raise exception.NotFoundError("collection")

    def _deviations_all(self):
        return itertools.chain.from_iterable([
            self.api.collections(self.user, folder["folderid"], self.offset)
            for folder in self.api.collections_folders(self.user)
        ])

    def prepare(self, deviation):
        DeviantartExtractor.prepare(deviation)
        deviation["collection"] = self.collection


class DeviantartJournalExtractor(DeviantartExtractor):
    """Extractor for single deviations"""
    subcategory = "journal"
    pattern = [r"(?:https?://)?([^.]+)\.deviantart\.com/journal/?$"]
    test = [("http://shimoda7.deviantart.com/journal/", {
        "url": "f7960ae06e774d6931c61ad309c95a10710658b2",
        "keyword": "9ddc2e130198395c1dfaa55c65b6bf63713ec0a8",
    })]

    def __init__(self, match):
        DeviantartExtractor.__init__(self)
        self.user = match.group(1)

    def deviations(self):
        return self.api.browse_user_journals(self.user, self.offset)


class DeviantartAPI():
    """Minimal interface for the deviantart API"""
    def __init__(self, extractor, client_id="5388",
                 client_secret="76b08c69cfb27f26d6161f9ab6d061a1"):
        self.session = extractor.session
        self.session.headers["dA-minor-version"] = "20160316"
        self.log = extractor.log
        self.client_id = client_id
        self.client_secret = client_secret
        self.delay = 0
        self.mature = extractor.config("mature", "true")
        if not isinstance(self.mature, str):
            self.mature = "true" if self.mature else "false"

    def browse_user_journals(self, username, offset=0):
        """Yield all journal entries of a specific user"""
        endpoint = "browse/user/journals"
        params = {"username": username, "offset": offset, "limit": 10,
                  "mature_content": self.mature, "featured": "false"}
        return self._pagination(endpoint, params)

    def collections(self, username, folder_id, offset=0):
        """Yield all Deviation-objects contained in a collection folder"""
        endpoint = "collections/" + folder_id
        params = {"username": username, "offset": offset, "limit": 10,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    def collections_folders(self, username, offset=0):
        """Yield all collection folders of a specific user"""
        endpoint = "collections/folders"
        params = {"username": username, "offset": offset, "limit": 10,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    def deviation(self, deviation_id):
        """Query and return info about a single Deviation"""
        endpoint = "deviation/" + deviation_id
        return self._call(endpoint)

    def deviation_content(self, deviation_id):
        """Get extended content of a single Deviation"""
        endpoint = "deviation/content"
        params = {"deviationid": deviation_id}
        return self._call(endpoint, params)

    def gallery_all(self, username, offset=0):
        """Yield all Deviation-objects of a specific user"""
        endpoint = "gallery/all"
        params = {"username": username, "offset": offset, "limit": 10,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    def authenticate(self):
        """Authenticate the application by requesting an access token"""
        access_token = self._authenticate_impl(
            self.client_id, self.client_secret
        )
        self.session.headers["Authorization"] = access_token

    @cache(maxage=3600, keyarg=1)
    def _authenticate_impl(self, client_id, client_secret):
        """Actual authenticate implementation"""
        url = "https://www.deviantart.com/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        response = self.session.post(url, data=data)
        if response.status_code != 200:
            raise exception.AuthenticationError()
        return "Bearer " + response.json()["access_token"]

    def _call(self, endpoint, params=None):
        """Call an API endpoint"""
        url = "https://www.deviantart.com/api/v1/oauth2/" + endpoint
        tries = 1
        while True:
            if self.delay:
                time.sleep(self.delay)

            self.authenticate()
            response = self.session.get(url, params=params)

            if response.status_code == 200:
                break
            elif response.status_code == 429:
                self.delay += 1
                self.log.debug("rate limit (delay: %d)", self.delay)
            else:
                self.delay = 1
                self.log.debug("http status code %d (%d/3)",
                               response.status_code, tries)
            tries += 1
            if tries > 3:
                raise Exception(response.text)
        try:
            return response.json()
        except ValueError:
            return {}

    def _pagination(self, endpoint, params=None):
        while True:
            data = self._call(endpoint, params)
            if "results" in data:
                yield from data["results"]
                if not data["has_more"]:
                    return
                params["offset"] = data["next_offset"]
            else:
                self.log.error("Unexpected API response: %s", data)
                return


SHADOW_TEMPLATE = """
<span class="shadow">
    <img src="{src}" class="smshadow" width="{width}" height="{height}">
</span>
<br><br>
"""


HEADER_TEMPLATE = """<div usr class="gr">
<div class="metadata">
    <h2><a href="{url}">{title}</a></h2>
    <ul>
        <li class="author">
            by <span class="name"><span class="username-with-symbol u">
            <a class="u regular username" href="{userurl}">{username}</a>\
<span class="user-symbol regular"></span></span></span>,
            <span>{date}</span>
        </li>
        <li class="category">
            {categories}
        </li>
    </ul>
</div>
"""

HEADER_CUSTOM_TEMPLATE = """<div class='boxtop journaltop'>
<h2>
    <img src="http://st.deviantart.net/minish/gruzecontrol/icons/journal.gif\
?2" style="vertical-align:middle" alt=""/>
    <a href="{url}">{title}</a>
</h2>
Journal Entry: <span>{date}</span>
"""


JOURNAL_TEMPLATE = """text:<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <link rel="stylesheet" href="http://st.deviantart.net/\
css/deviantart-network_lc.css?3843780832">
    <link rel="stylesheet" href="http://st.deviantart.net/\
css/group_secrets_lc.css?3250492874">
    <link rel="stylesheet" href="http://st.deviantart.net/\
css/v6core_lc.css?4246581581">
    <link rel="stylesheet" href="http://st.deviantart.net/\
css/sidebar_lc.css?1490570941">
    <link rel="stylesheet" href="http://st.deviantart.net/\
css/writer_lc.css?3090682151">
    <link rel="stylesheet" href="http://st.deviantart.net/\
css/v6loggedin_lc.css?3001430805">
    <style>{css}</style>
    <link rel="stylesheet" href="http://st.deviantart.net/\
roses/cssmin/core.css?1488405371919" >
    <link rel="stylesheet" href="http://st.deviantart.net/\
roses/cssmin/peeky.css?1487067424177" >
    <link rel="stylesheet" href="http://st.deviantart.net/\
roses/cssmin/desktop.css?1491362542749" >
</head>
<body id="deviantART-v7" class="bubble no-apps loggedout w960 deviantart">
    <div id="output">
    <div class="dev-page-container bubbleview">
    <div class="dev-page-view view-mode-normal">
    <div class="dev-view-main-content">
    <div class="dev-view-deviation">
    {shadow}
    <div class="journal-wrapper tt-a">
    <div class="journal-wrapper2">
    <div class="journal {cls} journalcontrol">
    {html}
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    </div>
</body>
</html>
"""
