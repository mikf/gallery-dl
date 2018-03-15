# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.deviantart.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache, memcache
import itertools
import datetime
import time
import re


class DeviantartExtractor(Extractor):
    """Base class for deviantart extractors"""
    category = "deviantart"
    directory_fmt = ["{category}", "{author[username]!l}"]
    filename_fmt = "{category}_{index}_{title}.{extension}"

    def __init__(self, match=None):
        Extractor.__init__(self)
        self.api = DeviantartAPI(self)
        self.offset = 0
        self.flat = self.config("flat", True)
        self.original = self.config("original", True)
        self.user = match.group(1) if match else None
        self.group = False

    def skip(self, num):
        self.offset += num
        return num

    def items(self):
        if self.user:
            self.group = not self.api.user_profile(self.user)
            if self.group:
                self.subcategory = "group-" + self.subcategory

        yield Message.Version, 1
        for deviation in self.deviations():
            if isinstance(deviation, tuple):
                url, data = deviation
                yield Message.Queue, url, data
                continue

            self.prepare(deviation)
            yield Message.Directory, deviation

            if "content" in deviation:
                content = deviation["content"]
                if (self.original and deviation["is_downloadable"] and
                        content["filesize"] != deviation["download_filesize"]):
                    content.update(
                        self.api.deviation_download(deviation["deviationid"]))
                yield self.commit(deviation, content)

            if "videos" in deviation:
                video = max(deviation["videos"],
                            key=lambda x: util.safe_int(x["quality"][:-1]))
                yield self.commit(deviation, video)

            if "flash" in deviation:
                yield self.commit(deviation, deviation["flash"])

            if "excerpt" in deviation:
                journal = self.api.deviation_content(deviation["deviationid"])
                yield self.commit_journal(deviation, journal)

    def deviations(self):
        """Return an iterable containing all relevant Deviation-objects"""
        return []

    def prepare(self, deviation):
        """Adjust the contents of a Deviation-object"""
        for key in ("stats", "preview", "is_favourited", "allows_comments"):
            if key in deviation:
                del deviation[key]
        try:
            deviation["index"] = deviation["url"].rpartition("-")[2]
        except KeyError:
            deviation["index"] = 0

        if self.user:
            deviation["username"] = self.user
        deviation["da_category"] = deviation["category"]

    @staticmethod
    def commit(deviation, target):
        url = target["src"]
        deviation["target"] = text.nameext_from_url(url, target.copy())
        deviation["extension"] = deviation["target"]["extension"]
        if url.startswith("http:"):
            url = "https:" + url[5:]
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
                ('<span class="crumb"><a href="https://www.deviantart.com/{}/"'
                 '><span>{}</span></a></span>').format(cpath, cat.capitalize())
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

    @staticmethod
    def _find_folder(folders, name):
        pattern = r"[^\w]*" + name.replace("-", r"[^\w]+") + r"[^\w]*$"
        for folder in folders:
            if re.match(pattern, folder["name"]):
                return folder
        raise exception.NotFoundError("folder")

    def _folder_urls(self, folders, category):
        url = "https://{}.deviantart.com/{}/0/".format(self.user, category)
        return [(url + folder["name"], folder) for folder in folders]


class DeviantartGalleryExtractor(DeviantartExtractor):
    """Extractor for all deviations from an artist's gallery"""
    subcategory = "gallery"
    archive_fmt = "g_{username}_{index}.{extension}"

    pattern = [r"(?:https?://)?([^.]+)\.deviantart\.com"
               r"(?:/(?:gallery/?(?:\?catpath=/)?)?)?$"]
    test = [
        ("http://shimoda7.deviantart.com/gallery/", {
            "url": "2b80b212717da6971b92670de15a29f68429a067",
            "keyword": "15897b5090af460c814cdd3e5702de10517fc4cc",
        }),
        ("https://yakuzafc.deviantart.com/", {
            "url": "fa6ecb2c3aa78872f762d43f7809b7f0580debc1",
            "keyword": "b29746bac291d8c8e339f0256a2bd7bb3ebe1741",
        }),
        ("http://shimoda7.deviantart.com/gallery/?catpath=/", None),
    ]

    def deviations(self):
        if self.flat and not self.group:
            return self.api.gallery_all(self.user, self.offset)
        else:
            folders = self.api.gallery_folders(self.user)
            return self._folder_urls(folders, "gallery")


class DeviantartFolderExtractor(DeviantartExtractor):
    """Extractor for deviations inside an artist's gallery folder"""
    subcategory = "folder"
    directory_fmt = ["{category}", "{folder[owner]}", "{folder[title]}"]
    archive_fmt = "F_{folder[uuid]}_{index}.{extension}"
    pattern = [r"(?:https?://)?([^.]+)\.deviantart\.com"
               r"/gallery/(\d+)/([^/?&#]+)"]
    test = [
        ("http://shimoda7.deviantart.com/gallery/722019/Miscellaneous", {
            "url": "12c331eeff84bd47350af5a199cecc187ae03832",
            "keyword": "efc16f7aff0d070e7eb6394f080b790b1613609d",
        }),
        ("http://majestic-da.deviantart.com/gallery/63419606/CHIBI-KAWAII", {
            "url": "2ea2a3df9591c26568b09291acb453fb87ce9920",
            "keyword": "42ecdc1a4d7441628f4bcfbe4d2e683a3a4361e2",
            "options": (("original", False),),
        }),
    ]

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.user, fid, self.fname = match.groups()
        self.folder = {"owner": self.user, "index": fid}

    def deviations(self):
        folders = self.api.gallery_folders(self.user)
        folder = self._find_folder(folders, self.fname)
        self.folder["title"] = folder["name"]
        self.folder["uuid"] = folder["folderid"]
        return self.api.gallery(self.user, folder["folderid"], self.offset)

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["folder"] = self.folder


class DeviantartDeviationExtractor(DeviantartExtractor):
    """Extractor for single deviations"""
    subcategory = "deviation"
    archive_fmt = "{index}.{extension}"
    pattern = [(r"(?:https?://)?([^.]+\.deviantart\.com/"
                r"(?:art|journal)/[^/?&#]+-\d+)"),
               (r"(?:https?://)?(sta\.sh/[a-z0-9]+)")]
    test = [
        (("http://shimoda7.deviantart.com/art/"
          "For-the-sake-of-a-memory-10073852"), {
            "url": "eef0c01b3808c535ea673e7b3654ab5209b910b7",
            "keyword": "344b558dead0da0031ba8d1dffff06f13bbb8561",
            "content": "6a7c74dc823ebbd457bdd9b3c2838a6ee728091e",
        }),
        ("https://zzz.deviantart.com/art/zzz-1234567890", {
            "exception": exception.NotFoundError,
        }),
        ("http://sta.sh/01ijs78ebagf", {
            "url": "35c0cd0e51494a1e01bddf5414a0d1585cd9fb0e",
            "keyword": "225008b7d218d2cd1ac5d5bad3d74e3cc171a1cb",
        }),
        ("http://sta.sh/abcdefghijkl", {
            "exception": exception.NotFoundError,
        }),
        (("https://myria-moon.deviantart.com/art/"
          "Aime-Moi-part-en-vadrouille-261986576"), {
            "pattern": (r"https?://s3\.amazonaws\.com/origin-orig\."
                        r"deviantart\.net/a383/f/2013/135/e/7/[^.]+\.jpg\?"),
        }),
    ]

    def __init__(self, match):
        DeviantartExtractor.__init__(self)
        self.url = "https://" + match.group(1)

    def deviations(self):
        response = self.request(self.url, fatal=False)
        deviation_id = text.extract(response.text, '//deviation/', '"')[0]
        if response.status_code != 200 or not deviation_id:
            raise exception.NotFoundError("image")
        return (self.api.deviation(deviation_id),)


class DeviantartFavoriteExtractor(DeviantartExtractor):
    """Extractor for an artist's favorites"""
    subcategory = "favorite"
    directory_fmt = ["{category}", "{username}", "Favourites"]
    archive_fmt = "f_{username}_{index}.{extension}"
    pattern = [r"(?:https?://)?([^.]+)\.deviantart\.com"
               r"/favourites/?(?:\?catpath=/)?$"]
    test = [
        ("http://h3813067.deviantart.com/favourites/", {
            "url": "eef0c01b3808c535ea673e7b3654ab5209b910b7",
            "keyword": "4478a3fa7cf9c72947cd927e8b54dbec3db9d0b2",
            "content": "6a7c74dc823ebbd457bdd9b3c2838a6ee728091e",
        }),
        ("http://h3813067.deviantart.com/favourites/?catpath=/", None),
    ]

    def deviations(self):
        folders = self.api.collections_folders(self.user)
        if self.flat:
            return itertools.chain.from_iterable([
                self.api.collections(self.user, folder["folderid"])
                for folder in folders
            ])
        else:
            return self._folder_urls(folders, "favourites")


class DeviantartCollectionExtractor(DeviantartExtractor):
    """Extractor for a single favorite collection"""
    subcategory = "collection"
    directory_fmt = ["{category}", "{collection[owner]}",
                     "Favourites", "{collection[title]}"]
    archive_fmt = "C_{collection[uuid]}_{index}.{extension}"
    pattern = [r"(?:https?://)?([^.]+)\.deviantart\.com"
               r"/favourites/(\d+)/([^/?&#]+)"]
    test = [(("https://pencilshadings.deviantart.com"
              "/favourites/70595441/3D-Favorites"), {
        "url": "742f92199d5bc6a89cda6ec6133d46c7a523824d",
        "keyword": "d258ca05424b3586c4feec940158bca00acdf511",
        "options": (("original", False),),
    })]

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.user, cid, self.cname = match.groups()
        self.collection = {"owner": self.user, "index": cid}

    def deviations(self):
        folders = self.api.collections_folders(self.user)
        folder = self._find_folder(folders, self.cname)
        self.collection["title"] = folder["name"]
        self.collection["uuid"] = folder["folderid"]
        return self.api.collections(self.user, folder["folderid"], self.offset)

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["collection"] = self.collection


class DeviantartJournalExtractor(DeviantartExtractor):
    """Extractor for an artist's journals"""
    subcategory = "journal"
    directory_fmt = ["{category}", "{username}", "Journal"]
    archive_fmt = "j_{username}_{index}.{extension}"
    pattern = [r"(?:https?://)?([^.]+)\.deviantart\.com"
               r"/(?:journal|blog)/?(?:\?catpath=/)?$"]
    test = [
        ("https://angrywhitewanker.deviantart.com/journal/", {
            "url": "2a7dba8f18e0d7cb791cd8c78e35376f98933f9e",
            "keyword": "57a92f1ccdba4acfd4f264963fc41fc37aec4de3",
        }),
        ("http://shimoda7.deviantart.com/journal/?catpath=/", None),
    ]

    def deviations(self):
        return self.api.browse_user_journals(self.user, self.offset)


class DeviantartAPI():
    """Minimal interface for the deviantart API"""
    CLIENT_ID = "5388"
    CLIENT_SECRET = "76b08c69cfb27f26d6161f9ab6d061a1"

    def __init__(self, extractor):
        self.session = extractor.session
        self.log = extractor.log
        self.headers = {}
        self.delay = 0

        self.mature = extractor.config("mature", "true")
        if not isinstance(self.mature, str):
            self.mature = "true" if self.mature else "false"

        self.refresh_token = extractor.config("refresh-token")
        self.client_id = extractor.config("client-id", self.CLIENT_ID)
        self.client_secret = extractor.config(
            "client-secret", self.CLIENT_SECRET)

    def browse_user_journals(self, username, offset=0):
        """Yield all journal entries of a specific user"""
        endpoint = "browse/user/journals"
        params = {"username": username, "offset": offset, "limit": 50,
                  "mature_content": self.mature, "featured": "false"}
        return self._pagination(endpoint, params)

    def collections(self, username, folder_id, offset=0):
        """Yield all Deviation-objects contained in a collection folder"""
        endpoint = "collections/" + folder_id
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    @memcache(keyarg=1)
    def collections_folders(self, username, offset=0):
        """Yield all collection folders of a specific user"""
        endpoint = "collections/folders"
        params = {"username": username, "offset": offset, "limit": 50,
                  "mature_content": self.mature}
        return self._pagination_list(endpoint, params)

    def deviation(self, deviation_id):
        """Query and return info about a single Deviation"""
        endpoint = "deviation/" + deviation_id
        return self._call(endpoint)

    def deviation_content(self, deviation_id):
        """Get extended content of a single Deviation"""
        endpoint = "deviation/content"
        params = {"deviationid": deviation_id}
        return self._call(endpoint, params)

    def deviation_download(self, deviation_id):
        """Get the original file download (if allowed)"""
        endpoint = "deviation/download/" + deviation_id
        params = {"mature_content": self.mature}
        return self._call(endpoint, params)

    def gallery(self, username, folder_id="", offset=0):
        """Yield all Deviation-objects contained in a gallery folder"""
        endpoint = "gallery/" + folder_id
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature, "mode": "newest"}
        return self._pagination(endpoint, params)

    def gallery_all(self, username, offset=0):
        """Yield all Deviation-objects of a specific user"""
        endpoint = "gallery/all"
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    @memcache(keyarg=1)
    def gallery_folders(self, username, offset=0):
        """Yield all gallery folders of a specific user"""
        endpoint = "gallery/folders"
        params = {"username": username, "offset": offset, "limit": 50,
                  "mature_content": self.mature}
        return self._pagination_list(endpoint, params)

    @memcache(keyarg=1)
    def user_profile(self, username):
        """Get user profile information"""
        endpoint = "user/profile/" + username
        return self._call(endpoint, expect_error=True)

    def authenticate(self):
        """Authenticate the application by requesting an access token"""
        access_token = self._authenticate_impl(self.refresh_token)
        self.headers["Authorization"] = access_token

    @cache(maxage=3590, keyarg=1)
    def _authenticate_impl(self, refresh_token):
        """Actual authenticate implementation"""
        url = "https://www.deviantart.com/oauth2/token"
        if refresh_token:
            self.log.info("Refreshing access token")
            data = {"grant_type": "refresh_token",
                    "refresh_token": _refresh_token_cache(refresh_token)}
        else:
            self.log.info("Requesting public access token")
            data = {"grant_type": "client_credentials"}

        auth = (self.client_id, self.client_secret)
        response = self.session.post(url, data=data, auth=auth)
        if response.status_code != 200:
            raise exception.AuthenticationError()

        data = response.json()
        if refresh_token:
            _refresh_token_cache.invalidate(refresh_token)
            _refresh_token_cache(refresh_token, data["refresh_token"])
        return "Bearer " + data["access_token"]

    def _call(self, endpoint, params=None, expect_error=False):
        """Call an API endpoint"""
        url = "https://www.deviantart.com/api/v1/oauth2/" + endpoint
        while True:
            if self.delay > 0:
                time.sleep(2 ** (self.delay-1))

            self.authenticate()
            response = self.session.get(
                url, headers=self.headers, params=params)

            if response.status_code == 200:
                if self.delay > 2:
                    self.delay -= 1
                break

            else:
                if response.status_code == 429:
                    msg = "Rate limit reached"
                else:
                    if expect_error:
                        return None
                    msg = "API responded with {} {}".format(
                        response.status_code, response.reason)
                self.delay += 1
                self.log.warning(
                    "%s. Using %ds delay.", msg, 2 ** (self.delay-1))
                self.log.debug(response.text)
        try:
            return response.json()
        except ValueError:
            self.log.error("Failed to parse API response")
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

    def _pagination_list(self, endpoint, params=None):
        result = []
        result.extend(self._pagination(endpoint, params))
        return result


@cache(maxage=365*24*60*60, keyarg=0)
def _refresh_token_cache(original_token, new_token=None):
    return new_token or original_token


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
    <img src="https://st.deviantart.net/minish/gruzecontrol/icons/journal.gif\
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
    <link rel="stylesheet" href="https://st.deviantart.net/\
css/deviantart-network_lc.css?3843780832">
    <link rel="stylesheet" href="https://st.deviantart.net/\
css/group_secrets_lc.css?3250492874">
    <link rel="stylesheet" href="https://st.deviantart.net/\
css/v6core_lc.css?4246581581">
    <link rel="stylesheet" href="https://st.deviantart.net/\
css/sidebar_lc.css?1490570941">
    <link rel="stylesheet" href="https://st.deviantart.net/\
css/writer_lc.css?3090682151">
    <link rel="stylesheet" href="https://st.deviantart.net/\
css/v6loggedin_lc.css?3001430805">
    <style>{css}</style>
    <link rel="stylesheet" href="https://st.deviantart.net/\
roses/cssmin/core.css?1488405371919" >
    <link rel="stylesheet" href="https://st.deviantart.net/\
roses/cssmin/peeky.css?1487067424177" >
    <link rel="stylesheet" href="https://st.deviantart.net/\
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
