# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.deviantart.com/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache, memcache
import itertools
import mimetypes
import time
import math
import re


BASE_PATTERN = (
    r"(?:https?://)?(?:"
    r"(?:www\.)?deviantart\.com/([\w-]+)|"
    r"(?!www\.)([\w-]+)\.deviantart\.com)"
)


class DeviantartExtractor(Extractor):
    """Base class for deviantart extractors"""
    category = "deviantart"
    directory_fmt = ("{category}", "{author[username]!l}")
    filename_fmt = "{category}_{index}_{title}.{extension}"
    root = "https://www.deviantart.com"

    def __init__(self, match=None):
        Extractor.__init__(self, match)
        self.api = DeviantartAPI(self)
        self.offset = 0
        self.flat = self.config("flat", True)
        self.original = self.config("original", True)
        self.user = match.group(1) or match.group(2)
        self.group = False

        self.commit_journal = {
            "html": self._commit_journal_html,
            "text": self._commit_journal_text,
        }.get(self.config("journals", "html"))

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

                if self.original and deviation["is_downloadable"] and \
                        text.ext_from_url(content["src"]) != "gif":
                    self._update_content(deviation, content)

                if deviation["index"] <= 790677560 and \
                        content["src"].startswith("https://images-wixmp-"):
                    # https://github.com/r888888888/danbooru/issues/4069
                    content["src"] = re.sub(
                        r"(/f/[^/]+/[^/]+)/v\d+/.*",
                        r"/intermediary\1", content["src"])

                yield self.commit(deviation, content)

            if "videos" in deviation:
                video = max(deviation["videos"],
                            key=lambda x: text.parse_int(x["quality"][:-1]))
                yield self.commit(deviation, video)

            if "flash" in deviation:
                yield self.commit(deviation, deviation["flash"])

            if "excerpt" in deviation and self.commit_journal:
                journal = self.api.deviation_content(deviation["deviationid"])
                yield self.commit_journal(deviation, journal)

    def deviations(self):
        """Return an iterable containing all relevant Deviation-objects"""
        return []

    def prepare(self, deviation):
        """Adjust the contents of a Deviation-object"""
        try:
            deviation["index"] = text.parse_int(
                deviation["url"].rpartition("-")[2])
        except KeyError:
            deviation["index"] = 0
        if self.user:
            deviation["username"] = self.user
        deviation["da_category"] = deviation["category"]
        deviation["published_time"] = text.parse_int(
            deviation["published_time"])
        deviation["date"] = text.parse_timestamp(
            deviation["published_time"])

    @staticmethod
    def commit(deviation, target):
        url = target["src"]
        deviation["target"] = text.nameext_from_url(url, target.copy())
        deviation["extension"] = deviation["target"]["extension"]
        return Message.Url, url, deviation

    def _commit_journal_html(self, deviation, journal):
        title = text.escape(deviation["title"])
        url = deviation["url"]
        thumbs = deviation["thumbs"]
        html = journal["html"]
        shadow = SHADOW_TEMPLATE.format_map(thumbs[0]) if thumbs else ""

        if "css" in journal:
            css, cls = journal["css"], "withskin"
        else:
            css, cls = "", "journal-green"

        if html.find('<div class="boxtop journaltop">', 0, 250) != -1:
            needle = '<div class="boxtop journaltop">'
            header = HEADER_CUSTOM_TEMPLATE.format(
                title=title, url=url, date=deviation["date"],
            )
        else:
            needle = '<div usr class="gr">'
            catlist = deviation["category_path"].split("/")
            categories = " / ".join(
                ('<span class="crumb"><a href="{}/{}/"><span>{}</span></a>'
                 '</span>').format(self.root, cpath, cat.capitalize())
                for cat, cpath in zip(
                    catlist,
                    itertools.accumulate(catlist, lambda t, c: t + "/" + c)
                )
            )
            username = deviation["author"]["username"]
            urlname = deviation.get("username") or username.lower()
            header = HEADER_TEMPLATE.format(
                title=title,
                url=url,
                userurl="{}/{}/".format(self.root, urlname),
                username=username,
                date=deviation["date"],
                categories=categories,
            )

        html = JOURNAL_TEMPLATE_HTML.format(
            title=title,
            html=html.replace(needle, header, 1),
            shadow=shadow,
            css=css,
            cls=cls,
        )

        deviation["extension"] = "htm"
        return Message.Url, html, deviation

    @staticmethod
    def _commit_journal_text(deviation, journal):
        content = "\n".join(
            text.unescape(text.remove_html(txt))
            for txt in journal["html"].rpartition("<script")[0].split("<br />")
        )
        txt = JOURNAL_TEMPLATE_TEXT.format(
            title=deviation["title"],
            username=deviation["author"]["username"],
            date=deviation["date"],
            content=content,
        )

        deviation["extension"] = "txt"
        return Message.Url, txt, deviation

    @staticmethod
    def _find_folder(folders, name):
        pattern = r"[^\w]*" + name.replace("-", r"[^\w]+") + r"[^\w]*$"
        for folder in folders:
            if re.match(pattern, folder["name"]):
                return folder
        raise exception.NotFoundError("folder")

    def _folder_urls(self, folders, category):
        url = "{}/{}/{}/0/".format(self.root, self.user, category)
        return [(url + folder["name"], folder) for folder in folders]

    def _update_content(self, deviation, content):
        data = self.api.deviation_download(deviation["deviationid"])
        if self.original == "images":
            url = data["src"].partition("?")[0]
            mtype = mimetypes.guess_type(url, False)[0]
            if not mtype or not mtype.startswith("image/"):
                return
        content.update(data)


class DeviantartGalleryExtractor(DeviantartExtractor):
    """Extractor for all deviations from an artist's gallery"""
    subcategory = "gallery"
    archive_fmt = "g_{username}_{index}.{extension}"
    pattern = BASE_PATTERN + r"(?:/(?:gallery/?(?:\?catpath=/)?)?)?$"
    test = (
        ("https://www.deviantart.com/shimoda7/gallery/", {
            "pattern": r"https://(s3.amazonaws.com/origin-(img|orig)"
                       r".deviantart.net/|images-wixmp-\w+.wixmp.com/)",
            "count": ">= 30",
            "keyword": {
                "allows_comments": bool,
                "author": {
                    "type": "regular",
                    "usericon": str,
                    "userid": "9AE51FC7-0278-806C-3FFF-F4961ABF9E2B",
                    "username": "shimoda7",
                },
                "category_path": str,
                "content": {
                    "filesize": int,
                    "height": int,
                    "src": str,
                    "transparency": bool,
                    "width": int,
                },
                "da_category": str,
                "date": "type:datetime",
                "deviationid": str,
                "?download_filesize": int,
                "extension": str,
                "index": int,
                "is_deleted": bool,
                "is_downloadable": bool,
                "is_favourited": bool,
                "is_mature": bool,
                "preview": {
                    "height": int,
                    "src": str,
                    "transparency": bool,
                    "width": int,
                },
                "published_time": int,
                "stats": {
                    "comments": int,
                    "favourites": int,
                },
                "target": dict,
                "thumbs": list,
                "title": str,
                "url": r"re:https://www.deviantart.com/shimoda7/art/[^/]+-\d+",
                "username": "shimoda7",
            },
        }),
        ("https://www.deviantart.com/yakuzafc", {
            "pattern": r"https://www.deviantart.com/yakuzafc/gallery/0/",
            "count": ">= 15",
        }),
        ("https://www.deviantart.com/shimoda8/gallery/", {
            "exception": exception.NotFoundError,
        }),
        ("https://www.deviantart.com/shimoda7/gallery/?catpath=/"),
        ("https://shimoda7.deviantart.com/gallery/"),
        ("https://yakuzafc.deviantart.com/"),
        ("https://shimoda7.deviantart.com/gallery/?catpath=/"),
    )

    def deviations(self):
        if self.flat and not self.group:
            return self.api.gallery_all(self.user, self.offset)
        else:
            folders = self.api.gallery_folders(self.user)
            return self._folder_urls(folders, "gallery")


class DeviantartFolderExtractor(DeviantartExtractor):
    """Extractor for deviations inside an artist's gallery folder"""
    subcategory = "folder"
    directory_fmt = ("{category}", "{folder[owner]}", "{folder[title]}")
    archive_fmt = "F_{folder[uuid]}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/gallery/(\d+)/([^/?&#]+)"
    test = (
        ("https://www.deviantart.com/shimoda7/gallery/722019/Miscellaneous", {
            "count": 5,
            "options": (("original", False),),
        }),
        ("https://www.deviantart.com/yakuzafc/gallery/37412168/Crafts", {
            "count": ">= 4",
            "options": (("original", False),),
        }),
        ("https://shimoda7.deviantart.com/gallery/722019/Miscellaneous"),
        ("https://yakuzafc.deviantart.com/gallery/37412168/Crafts"),
    )

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        _, _, fid, self.fname = match.groups()
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
    pattern = BASE_PATTERN + r"/((?:art|journal)/[^/?&#]+-\d+)"
    test = (
        (("https://www.deviantart.com/shimoda7/art/"
          "For-the-sake-of-a-memory-10073852"), {
            "content": "6a7c74dc823ebbd457bdd9b3c2838a6ee728091e",
        }),
        ("https://www.deviantart.com/zzz/art/zzz-1234567890", {
            "exception": exception.NotFoundError,
        }),
        (("https://www.deviantart.com/myria-moon/art/"
          "Aime-Moi-part-en-vadrouille-261986576"), {
            "pattern": (r"https?://s3\.amazonaws\.com/origin-orig\."
                        r"deviantart\.net/a383/f/2013/135/e/7/[^.]+\.jpg\?"),
        }),
        # wixmp URL rewrite
        (("https://www.deviantart.com/citizenfresh/art/"
          "Hverarond-14-the-beauty-of-the-earth-789295466"), {
            "pattern": (r"https://images-wixmp-\w+\.wixmp\.com"
                        r"/intermediary/f/[^/]+/[^.]+\.jpg$")
        }),
        # non-download URL for GIFs (#242)
        (("https://www.deviantart.com/skatergators/art/"
          "COM-Monique-Model-781571783"), {
            "pattern": (r"https://images-wixmp-\w+\.wixmp\.com"
                        r"/f/[^/]+/[^.]+\.gif\?token="),
        }),
        # old-style URLs
        ("https://shimoda7.deviantart.com"
         "/art/For-the-sake-of-a-memory-10073852"),
        ("https://myria-moon.deviantart.com"
         "/art/Aime-Moi-part-en-vadrouille-261986576"),
        ("https://zzz.deviantart.com/art/zzz-1234567890"),
    )

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.path = match.group(3)

    def deviations(self):
        url = "{}/{}/{}".format(self.root, self.user, self.path)
        response = self.request(url, expect=range(400, 500))
        deviation_id = text.extract(response.text, '//deviation/', '"')[0]
        if response.status_code >= 400 or not deviation_id:
            raise exception.NotFoundError("image")
        return (self.api.deviation(deviation_id),)


class DeviantartStashExtractor(DeviantartExtractor):
    """Extractor for sta.sh-ed deviations"""
    subcategory = "stash"
    archive_fmt = "{index}.{extension}"
    pattern = r"(?:https?://)?sta\.sh/([a-z0-9]+)"
    test = (
        ("https://sta.sh/022c83odnaxc", {
            "pattern": r"https://s3.amazonaws.com/origin-orig.deviantart.net",
            "count": 1,
        }),
        ("https://sta.sh/21jf51j7pzl2", {
            "pattern": pattern,
            "count": 4,
        }),
        ("https://sta.sh/abcdefghijkl", {
            "exception": exception.HttpError,
        }),
    )

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.stash_id = match.group(1)

    def deviations(self):
        url = "https://sta.sh/" + self.stash_id
        page = self.request(url).text
        deviation_id = text.extract(page, '//deviation/', '"')[0]

        if deviation_id:
            yield self.api.deviation(deviation_id)
        else:
            data = {"_extractor": DeviantartStashExtractor}
            page = text.extract(
                page, '<div id="stash-body"', '<div class="footer"')[0]
            for url in text.extract_iter(page, '<a href="', '"'):
                yield url, data


class DeviantartFavoriteExtractor(DeviantartExtractor):
    """Extractor for an artist's favorites"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "{username}", "Favourites")
    archive_fmt = "f_{username}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/favourites/?(?:\?catpath=/)?$"
    test = (
        ("https://www.deviantart.com/h3813067/favourites/", {
            "content": "6a7c74dc823ebbd457bdd9b3c2838a6ee728091e",
        }),
        ("https://www.deviantart.com/h3813067/favourites/?catpath=/"),
        ("https://h3813067.deviantart.com/favourites/"),
        ("https://h3813067.deviantart.com/favourites/?catpath=/"),
    )

    def deviations(self):
        folders = self.api.collections_folders(self.user)
        if self.flat:
            return itertools.chain.from_iterable(
                self.api.collections(self.user, folder["folderid"])
                for folder in folders
            )
        else:
            return self._folder_urls(folders, "favourites")


class DeviantartCollectionExtractor(DeviantartExtractor):
    """Extractor for a single favorite collection"""
    subcategory = "collection"
    directory_fmt = ("{category}", "{collection[owner]}",
                     "Favourites", "{collection[title]}")
    archive_fmt = "C_{collection[uuid]}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/favourites/(\d+)/([^/?&#]+)"
    test = (
        (("https://www.deviantart.com/pencilshadings"
          "/favourites/70595441/3D-Favorites"), {
            "count": ">= 20",
            "options": (("original", False),),
        }),
        ("https://pencilshadings.deviantart.com"
         "/favourites/70595441/3D-Favorites"),
    )

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        _, _, cid, self.cname = match.groups()
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
    directory_fmt = ("{category}", "{username}", "Journal")
    archive_fmt = "j_{username}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/(?:journal|blog)/?(?:\?catpath=/)?$"
    test = (
        ("https://www.deviantart.com/angrywhitewanker/journal/", {
            "url": "38db2a0d3a587a7e0f9dba7ff7d274610ebefe44",
        }),
        ("https://www.deviantart.com/angrywhitewanker/journal/", {
            "url": "b2a8e74d275664b1a4acee0fca0a6fd33298571e",
            "options": (("journals", "text"),),
        }),
        ("https://www.deviantart.com/angrywhitewanker/journal/", {
            "count": 0,
            "options": (("journals", "none"),),
        }),
        ("https://www.deviantart.com/shimoda7/journal/?catpath=/"),
        ("https://shimoda7.deviantart.com/journal/"),
        ("https://shimoda7.deviantart.com/journal/?catpath=/"),
    )

    def deviations(self):
        return self.api.browse_user_journals(self.user, self.offset)


class DeviantartScrapsExtractor(DeviantartExtractor):
    """Extractor for an artist's scraps"""
    subcategory = "scraps"
    directory_fmt = ("{category}", "{username}", "Scraps")
    archive_fmt = "s_{username}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/gallery/\?catpath=scraps\b"
    test = (
        ("https://www.deviantart.com/shimoda7/gallery/?catpath=scraps", {
            "count": 12,
            "options": (("original", False),),
        }),
        ("https://shimoda7.deviantart.com/gallery/?catpath=scraps"),
    )

    def deviations(self):
        url = "{}/{}/gallery/?catpath=scraps".format(self.root, self.user)
        page = self.request(url).text
        csrf, pos = text.extract(page, '"csrf":"', '"')
        iid , pos = text.extract(page, '"requestid":"', '"', pos)

        url = "https://www.deviantart.com/dapi/v1/gallery/0"
        data = {
            "username": self.user,
            "offset": self.offset,
            "limit": "24",
            "catpath": "scraps",
            "_csrf": csrf,
            "dapiIid": iid + "-jsok7403-1.1"
        }

        while True:
            content = self.request(
                url, method="POST", data=data).json()["content"]

            for item in content["results"]:
                if item["html"].startswith('<div class="ad-container'):
                    continue
                deviation_url = text.extract(item["html"], 'href="', '"')[0]
                page = self.request(deviation_url).text
                deviation_id = text.extract(page, '//deviation/', '"')[0]
                if deviation_id:
                    yield self.api.deviation(deviation_id)

            if not content["has_more"]:
                return
            data["offset"] = content["next_offset"]


class DeviantartPopularExtractor(DeviantartExtractor):
    """Extractor for popular deviations"""
    subcategory = "popular"
    directory_fmt = ("{category}", "Popular",
                     "{popular[range]}", "{popular[search]}")
    archive_fmt = "P_{popular[range]}_{popular[search]}_{index}.{extension}"
    pattern = (r"(?:https?://)?www\.deviantart\.com"
               r"((?:/\w+)*)/(?:popular-([^/?&#]+))/?(?:\?([^#]*))?")
    test = (
        ("https://www.deviantart.com/popular-24-hours/?q=tree+house", {
            "options": (("original", False),),
        }),
        ("https://www.deviantart.com/artisan/popular-all-time/?q=tree"),
    )

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.search_term = self.time_range = self.category_path = None
        self.user = ""

        path, trange, query = match.groups()
        if path:
            self.category_path = path.lstrip("/")
        if trange:
            self.time_range = trange.replace("-", "").replace("hours", "hr")
        if query:
            self.search_term = text.parse_query(query).get("q")

        self.popular = {
            "search": self.search_term or "",
            "range": trange or "24-hours",
            "path": self.category_path,
        }

    def deviations(self):
        return self.api.browse_popular(
            self.search_term, self.time_range, self.category_path, self.offset)

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["popular"] = self.popular


class DeviantartAPI():
    """Minimal interface for the DeviantArt API

    Ref: https://www.deviantart.com/developers/http/v1/20160316
    """
    CLIENT_ID = "5388"
    CLIENT_SECRET = "76b08c69cfb27f26d6161f9ab6d061a1"

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log
        self.headers = {}

        delay = extractor.config("wait-min", 0)
        self.delay = math.ceil(math.log2(delay)) if delay >= 1 else -1
        self.delay_min = max(2, self.delay)

        self.mature = extractor.config("mature", "true")
        if not isinstance(self.mature, str):
            self.mature = "true" if self.mature else "false"
        self.metadata = extractor.config("metadata", False)

        self.refresh_token = extractor.config("refresh-token")
        self.client_id = extractor.config("client-id", self.CLIENT_ID)
        self.client_secret = extractor.config(
            "client-secret", self.CLIENT_SECRET)

    def browse_popular(self, query=None, timerange=None,
                       category_path=None, offset=0):
        """Yield popular deviations"""
        endpoint = "browse/popular"
        params = {"q": query, "offset": offset, "limit": 120,
                  "timerange": timerange, "category_path": category_path,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

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
        deviation = self._call(endpoint)
        return self._extend((deviation,))[0]

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

    def deviation_metadata(self, deviations):
        """ Fetch deviation metadata for a set of deviations"""
        endpoint = "deviation/metadata?" + "&".join(
            "deviationids[{}]={}".format(num, deviation["deviationid"])
            for num, deviation in enumerate(deviations)
        )
        params = {"mature_content": self.mature}
        return self._call(endpoint, params)["metadata"]

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

    def authenticate(self, refresh_token):
        """Authenticate the application by requesting an access token"""
        self.headers["Authorization"] = self._authenticate_impl(refresh_token)

    @cache(maxage=3600, keyarg=1)
    def _authenticate_impl(self, refresh_token):
        """Actual authenticate implementation"""
        url = "https://www.deviantart.com/oauth2/token"
        if refresh_token:
            self.log.info("Refreshing private access token")
            data = {"grant_type": "refresh_token",
                    "refresh_token": _refresh_token_cache(refresh_token)}
        else:
            self.log.info("Requesting public access token")
            data = {"grant_type": "client_credentials"}

        auth = (self.client_id, self.client_secret)
        response = self.extractor.request(
            url, method="POST", data=data, auth=auth)
        data = response.json()

        if response.status_code != 200:
            raise exception.AuthenticationError('"{} ({})"'.format(
                data.get("error_description"), data.get("error")))
        if refresh_token:
            _refresh_token_cache.update(refresh_token, data["refresh_token"])
        return "Bearer " + data["access_token"]

    def _call(self, endpoint, params=None, expect_error=False, public=True):
        """Call an API endpoint"""
        url = "https://www.deviantart.com/api/v1/oauth2/" + endpoint
        while True:
            if self.delay >= 0:
                time.sleep(2 ** self.delay)

            self.authenticate(None if public else self.refresh_token)
            response = self.extractor.request(
                url,
                params=params,
                headers=self.headers,
                expect=range(400, 500),
            )
            data = response.json()
            status = response.status_code

            if 200 <= status < 400:
                if self.delay > self.delay_min:
                    self.delay -= 1
                return data
            elif expect_error:
                return None
            elif data.get("error_description") == "User not found.":
                raise exception.NotFoundError("user or group")

            self.log.debug(response.text)
            msg = "API responded with {} {}".format(
                status, response.reason)
            if status == 429:
                self.delay += 1
                self.log.warning("%s. Using %ds delay.", msg, 2 ** self.delay)
            else:
                self.log.error(msg)
                return data

    def _pagination(self, endpoint, params):
        public = True
        while True:
            data = self._call(endpoint, params, public=public)
            if "results" not in data:
                self.log.error("Unexpected API response: %s", data)
                return
            if (public and self.refresh_token and
                    len(data["results"]) < params["limit"]):
                self.log.debug("Switching to private access token")
                public = False
                continue
            yield from self._extend(data["results"])
            if not data["has_more"]:
                return
            params["offset"] = data["next_offset"]

    def _pagination_list(self, endpoint, params):
        result = []
        result.extend(self._pagination(endpoint, params))
        return result

    def _extend(self, deviations):
        """Add extended metadata to a list of deviation objects"""
        if self.metadata:
            for deviation, metadata in zip(
                    deviations, self.deviation_metadata(deviations)):
                deviation.update(metadata)
                deviation["tags"] = [t["tag_name"] for t in deviation["tags"]]
        return deviations


@cache(maxage=10*365*24*3600, keyarg=0)
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

JOURNAL_TEMPLATE_HTML = """text:<!DOCTYPE html>
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

JOURNAL_TEMPLATE_TEXT = """text:{title}
by {username}, {date}

{content}
"""
