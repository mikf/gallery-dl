# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
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
    filename_fmt = "{category}_{index}_{title}.{extension}"
    directory_fmt = ["{category}", "{author[username]!l}"]

    def __init__(self, match=None):
        Extractor.__init__(self)
        self.api = DeviantartAPI(self)
        self.offset = 0
        self.flat = self.config("flat", True)
        self.original = self.config("original", True)

        if match:
            self.user = match.group(1)
            self.group = not self.api.user_profile(self.user)
            if self.group:
                self.subcategory = "group-" + self.subcategory
        else:
            self.user = None
            self.group = False

    def skip(self, num):
        self.offset += num
        return num

    def items(self):
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
    pattern = [r"(?:https?://)?([^.]+)\.deviantart\.com"
               r"/gallery/(\d+)/([^/?&#]+)"]
    test = [
        ("http://shimoda7.deviantart.com/gallery/722019/Miscellaneous", {
            "url": "12c331eeff84bd47350af5a199cecc187ae03832",
            "keyword": "4e55acf35bd512d85b8e65d074c5f374ac369303",
        }),
        ("http://majestic-da.deviantart.com/gallery/63419606/CHIBI-KAWAII", {
            "url": "2ea2a3df9591c26568b09291acb453fb87ce9920",
            "keyword": "160b891599aa4ba1c799cd9e1696bcb1ddefeef4",
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
        return self.api.gallery(self.user, folder["folderid"], self.offset)

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["folder"] = self.folder


class DeviantartDeviationExtractor(DeviantartExtractor):
    """Extractor for single deviations"""
    subcategory = "deviation"
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
    pattern = [r"(?:https?://)?([^.]+)\.deviantart\.com"
               r"/favourites/(\d+)/([^/?&#]+)"]
    test = [(("https://pencilshadings.deviantart.com"
              "/favourites/70595441/3D-Favorites"), {
        "url": "36ea299132a6b0a0cd319318e9bf18ad32e9b8cc",
        "keyword": "6aada4e3159ca09ff8de9bae880952ce3b46d529",
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
        return self.api.collections(self.user, folder["folderid"], self.offset)

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["collection"] = self.collection


class DeviantartJournalExtractor(DeviantartExtractor):
    """Extractor for an artist's journals"""
    subcategory = "journal"
    directory_fmt = ["{category}", "{username}", "Journal"]
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
    def __init__(self, extractor, client_id="5388",
                 client_secret="76b08c69cfb27f26d6161f9ab6d061a1"):
        self.session = extractor.session
        self.headers = {}
        self.log = extractor.log
        self.client_id = extractor.config("client-id", client_id)
        self.client_secret = extractor.config("client-secret", client_secret)
        self.delay = 0
        self.mature = extractor.config("mature", "true")
        if not isinstance(self.mature, str):
            self.mature = "true" if self.mature else "false"

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
        access_token = self._authenticate_impl(
            self.client_id, self.client_secret
        )
        self.headers["Authorization"] = access_token

    @cache(maxage=3590, keyarg=1)
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

    def _call(self, endpoint, params=None, expect_error=False):
        """Call an API endpoint"""
        url = "https://www.deviantart.com/api/v1/oauth2/" + endpoint
        tries = 1
        while True:
            if self.delay:
                time.sleep(self.delay)

            self.authenticate()
            response = self.session.get(
                url, headers=self.headers, params=params)

            if response.status_code == 200:
                break
            elif response.status_code == 429:
                self.delay += 1
                self.log.debug("rate limit (delay: %d)", self.delay)
            else:
                if expect_error:
                    return None
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

    def _pagination_list(self, endpoint, params=None):
        result = []
        result.extend(self._pagination(endpoint, params))
        return result


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
