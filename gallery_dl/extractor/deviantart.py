# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.deviantart.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache, memcache
import collections
import itertools
import mimetypes
import binascii
import time
import re


BASE_PATTERN = (
    r"(?:https?://)?(?:"
    r"(?:www\.)?(?:fx)?deviantart\.com/(?!watch/)([\w-]+)|"
    r"(?!www\.)([\w-]+)\.(?:fx)?deviantart\.com)"
)


class DeviantartExtractor(Extractor):
    """Base class for deviantart extractors"""
    category = "deviantart"
    root = "https://www.deviantart.com"
    directory_fmt = ("{category}", "{username}")
    filename_fmt = "{category}_{index}_{title}.{extension}"
    cookiedomain = None
    cookienames = ("auth", "auth_secure", "userinfo")
    _last_request = 0

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.flat = self.config("flat", True)
        self.extra = self.config("extra", False)
        self.original = self.config("original", True)
        self.comments = self.config("comments", False)
        self.user = match.group(1) or match.group(2)
        self.group = False
        self.offset = 0
        self.api = None

        unwatch = self.config("auto-unwatch")
        if unwatch:
            self.unwatch = []
            self.finalize = self._unwatch_premium
        else:
            self.unwatch = None

        if self.original != "image":
            self._update_content = self._update_content_default
        else:
            self._update_content = self._update_content_image
            self.original = True

        self._premium_cache = {}
        self.commit_journal = {
            "html": self._commit_journal_html,
            "text": self._commit_journal_text,
        }.get(self.config("journals", "html"))

    def skip(self, num):
        self.offset += num
        return num

    def login(self):
        if not self._check_cookies(self.cookienames):
            username, password = self._get_auth_info()
            if not username:
                return False
            self._update_cookies(_login_impl(self, username, password))
        return True

    def items(self):
        self.api = DeviantartOAuthAPI(self)

        if self.user and self.config("group", True):
            profile = self.api.user_profile(self.user)
            self.group = not profile
            if self.group:
                self.subcategory = "group-" + self.subcategory
                self.user = self.user.lower()
            else:
                self.user = profile["user"]["username"]

        for deviation in self.deviations():
            if isinstance(deviation, tuple):
                url, data = deviation
                yield Message.Queue, url, data
                continue

            if deviation["is_deleted"]:
                # prevent crashing in case the deviation really is
                # deleted
                self.log.debug(
                    "Skipping %s (deleted)", deviation["deviationid"])
                continue

            if "premium_folder_data" in deviation:
                data = self._fetch_premium(deviation)
                if not data:
                    continue
                deviation.update(data)

            self.prepare(deviation)
            yield Message.Directory, deviation

            if "content" in deviation:
                content = deviation["content"]

                if self.original and deviation["is_downloadable"]:
                    self._update_content(deviation, content)
                else:
                    self._update_token(deviation, content)

                yield self.commit(deviation, content)

            elif deviation["is_downloadable"]:
                content = self.api.deviation_download(deviation["deviationid"])
                yield self.commit(deviation, content)

            if "videos" in deviation and deviation["videos"]:
                video = max(deviation["videos"],
                            key=lambda x: text.parse_int(x["quality"][:-1]))
                yield self.commit(deviation, video)

            if "flash" in deviation:
                yield self.commit(deviation, deviation["flash"])

            if self.commit_journal:
                if "excerpt" in deviation:
                    journal = self.api.deviation_content(
                        deviation["deviationid"])
                elif "body" in deviation:
                    journal = {"html": deviation.pop("body")}
                else:
                    journal = None
                if journal:
                    if self.extra:
                        deviation["_journal"] = journal["html"]
                    yield self.commit_journal(deviation, journal)

            if not self.extra:
                continue

            # ref: https://www.deviantart.com
            #      /developers/http/v1/20210526/object/editor_text
            # the value of "features" is a JSON string with forward
            # slashes escaped
            text_content = \
                deviation["text_content"]["body"]["features"].replace(
                    "\\/", "/") if "text_content" in deviation else None
            for txt in (text_content, deviation.get("description"),
                        deviation.get("_journal")):
                if txt is None:
                    continue
                for match in DeviantartStashExtractor.pattern.finditer(txt):
                    url = text.ensure_http_scheme(match.group(0))
                    deviation["_extractor"] = DeviantartStashExtractor
                    yield Message.Queue, url, deviation

    def deviations(self):
        """Return an iterable containing all relevant Deviation-objects"""

    def prepare(self, deviation):
        """Adjust the contents of a Deviation-object"""
        if "index" not in deviation:
            try:
                if deviation["url"].startswith("https://sta.sh"):
                    filename = deviation["content"]["src"].split("/")[5]
                    deviation["index_base36"] = filename.partition("-")[0][1:]
                    deviation["index"] = id_from_base36(
                        deviation["index_base36"])
                else:
                    deviation["index"] = text.parse_int(
                        deviation["url"].rpartition("-")[2])
            except KeyError:
                deviation["index"] = 0
                deviation["index_base36"] = "0"
        if "index_base36" not in deviation:
            deviation["index_base36"] = base36_from_id(deviation["index"])

        if self.user:
            deviation["username"] = self.user
            deviation["_username"] = self.user.lower()
        else:
            deviation["username"] = deviation["author"]["username"]
            deviation["_username"] = deviation["username"].lower()

        deviation["da_category"] = deviation["category"]
        deviation["published_time"] = text.parse_int(
            deviation["published_time"])
        deviation["date"] = text.parse_timestamp(
            deviation["published_time"])

        if self.comments:
            deviation["comments"] = (
                self.api.comments(deviation["deviationid"], target="deviation")
                if deviation["stats"]["comments"] else ()
            )

        # filename metadata
        sub = re.compile(r"\W").sub
        deviation["filename"] = "".join((
            sub("_", deviation["title"].lower()), "_by_",
            sub("_", deviation["author"]["username"].lower()), "-d",
            deviation["index_base36"],
        ))

    @staticmethod
    def commit(deviation, target):
        url = target["src"]
        name = target.get("filename") or url
        target = target.copy()
        target["filename"] = deviation["filename"]
        deviation["target"] = target
        deviation["extension"] = target["extension"] = text.ext_from_url(name)
        return Message.Url, url, deviation

    def _commit_journal_html(self, deviation, journal):
        title = text.escape(deviation["title"])
        url = deviation["url"]
        thumbs = deviation.get("thumbs") or deviation.get("files")
        html = journal["html"]
        shadow = SHADOW_TEMPLATE.format_map(thumbs[0]) if thumbs else ""

        if "css" in journal:
            css, cls = journal["css"], "withskin"
        elif html.startswith("<style"):
            css, _, html = html.partition("</style>")
            css = css.partition(">")[2]
            cls = "withskin"
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

        if needle in html:
            html = html.replace(needle, header, 1)
        else:
            html = JOURNAL_TEMPLATE_HTML_EXTRA.format(header, html)

        html = JOURNAL_TEMPLATE_HTML.format(
            title=title, html=html, shadow=shadow, css=css, cls=cls)

        deviation["extension"] = "htm"
        return Message.Url, html, deviation

    @staticmethod
    def _commit_journal_text(deviation, journal):
        html = journal["html"]
        if html.startswith("<style"):
            html = html.partition("</style>")[2]
        head, _, tail = html.rpartition("<script")
        content = "\n".join(
            text.unescape(text.remove_html(txt))
            for txt in (head or tail).split("<br />")
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
    def _find_folder(folders, name, uuid):
        if uuid.isdecimal():
            match = re.compile(name.replace(
                "-", r"[^a-z0-9]+") + "$", re.IGNORECASE).match
            for folder in folders:
                if match(folder["name"]):
                    return folder
        else:
            for folder in folders:
                if folder["folderid"] == uuid:
                    return folder
        raise exception.NotFoundError("folder")

    def _folder_urls(self, folders, category, extractor):
        base = "{}/{}/{}/".format(self.root, self.user, category)
        for folder in folders:
            folder["_extractor"] = extractor
            url = "{}{}/{}".format(base, folder["folderid"], folder["name"])
            yield url, folder

    def _update_content_default(self, deviation, content):
        public = False if "premium_folder_data" in deviation else None
        data = self.api.deviation_download(deviation["deviationid"], public)
        content.update(data)

    def _update_content_image(self, deviation, content):
        data = self.api.deviation_download(deviation["deviationid"])
        url = data["src"].partition("?")[0]
        mtype = mimetypes.guess_type(url, False)[0]
        if mtype and mtype.startswith("image/"):
            content.update(data)

    def _update_token(self, deviation, content):
        """Replace JWT to be able to remove width/height limits

        All credit goes to @Ironchest337
        for discovering and implementing this method
        """
        url, sep, _ = content["src"].partition("/v1/")
        if not sep:
            return

        #  header = b'{"typ":"JWT","alg":"none"}'
        payload = (
            b'{"sub":"urn:app:","iss":"urn:app:","obj":[[{"path":"/f/' +
            url.partition("/f/")[2].encode() +
            b'"}]],"aud":["urn:service:file.download"]}'
        )

        deviation["_fallback"] = (content["src"],)
        content["src"] = (
            "{}?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.{}.".format(
                url,
                #  base64 of 'header' is precomputed as 'eyJ0eX...'
                #  binascii.a2b_base64(header).rstrip(b"=\n").decode(),
                binascii.b2a_base64(payload).rstrip(b"=\n").decode())
        )

    def _limited_request(self, url, **kwargs):
        """Limits HTTP requests to one every 2 seconds"""
        kwargs["fatal"] = None
        diff = time.time() - DeviantartExtractor._last_request
        if diff < 2.0:
            self.sleep(2.0 - diff, "request")

        while True:
            response = self.request(url, **kwargs)
            if response.status_code != 403 or \
                    b"Request blocked." not in response.content:
                DeviantartExtractor._last_request = time.time()
                return response
            self.wait(seconds=180)

    def _fetch_premium(self, deviation):
        try:
            return self._premium_cache[deviation["deviationid"]]
        except KeyError:
            pass

        if not self.api.refresh_token_key:
            self.log.warning(
                "Unable to access premium content (no refresh-token)")
            self._fetch_premium = lambda _: None
            return None

        dev = self.api.deviation(deviation["deviationid"], False)
        folder = dev["premium_folder_data"]
        username = dev["author"]["username"]
        has_access = folder["has_access"]

        if not has_access and folder["type"] == "watchers" and \
                self.config("auto-watch"):
            if self.unwatch is not None:
                self.unwatch.append(username)
            if self.api.user_friends_watch(username):
                has_access = True
                self.log.info(
                    "Watching %s for premium folder access", username)
            else:
                self.log.warning(
                    "Error when trying to watch %s. "
                    "Try again with a new refresh-token", username)

        if has_access:
            self.log.info("Fetching premium folder data")
        else:
            self.log.warning("Unable to access premium content (type: %s)",
                             folder["type"])

        cache = self._premium_cache
        for dev in self.api.gallery(
                username, folder["gallery_id"], public=False):
            cache[dev["deviationid"]] = dev if has_access else None

        return cache[deviation["deviationid"]]

    def _unwatch_premium(self):
        for username in self.unwatch:
            self.log.info("Unwatching %s", username)
            self.api.user_friends_unwatch(username)

    def _eclipse_to_oauth(self, eclipse_api, deviations):
        for obj in deviations:
            deviation = obj["deviation"] if "deviation" in obj else obj
            deviation_uuid = eclipse_api.deviation_extended_fetch(
                deviation["deviationId"],
                deviation["author"]["username"],
                "journal" if deviation["isJournal"] else "art",
            )["deviation"]["extended"]["deviationUuid"]
            yield self.api.deviation(deviation_uuid)


class DeviantartUserExtractor(DeviantartExtractor):
    """Extractor for an artist's user profile"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/?$"
    test = (
        ("https://www.deviantart.com/shimoda7", {
            "pattern": r"/shimoda7/gallery$",
        }),
        ("https://www.deviantart.com/shimoda7", {
            "options": (("include", "all"),),
            "pattern": r"/shimoda7/"
                       r"(gallery(/scraps)?|posts(/statuses)?|favourites)$",
            "count": 5,
        }),
        ("https://shimoda7.deviantart.com/"),
    )

    def items(self):
        base = "{}/{}/".format(self.root, self.user)
        return self._dispatch_extractors((
            (DeviantartGalleryExtractor , base + "gallery"),
            (DeviantartScrapsExtractor  , base + "gallery/scraps"),
            (DeviantartJournalExtractor , base + "posts"),
            (DeviantartStatusExtractor  , base + "posts/statuses"),
            (DeviantartFavoriteExtractor, base + "favourites"),
        ), ("gallery",))


###############################################################################
# OAuth #######################################################################

class DeviantartGalleryExtractor(DeviantartExtractor):
    """Extractor for all deviations from an artist's gallery"""
    subcategory = "gallery"
    archive_fmt = "g_{_username}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/gallery(?:/all|/?\?catpath=)?/?$"
    test = (
        ("https://www.deviantart.com/shimoda7/gallery/", {
            "pattern": r"https://(images-)?wixmp-[^.]+\.wixmp\.com"
                       r"/f/.+/.+\.(jpg|png)\?token=.+",
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
        # group
        ("https://www.deviantart.com/yakuzafc/gallery", {
            "pattern": r"https://www.deviantart.com/yakuzafc/gallery"
                       r"/\w{8}-\w{4}-\w{4}-\w{4}-\w{12}/",
            "count": ">= 15",
        }),
        # 'folders' option (#276)
        ("https://www.deviantart.com/justatest235723/gallery", {
            "count": 3,
            "options": (("metadata", 1), ("folders", 1), ("original", 0)),
            "keyword": {
                "description": str,
                "folders": list,
                "is_watching": bool,
                "license": str,
                "tags": list,
            },
        }),
        ("https://www.deviantart.com/shimoda8/gallery/", {
            "exception": exception.NotFoundError,
        }),

        ("https://www.deviantart.com/shimoda7/gallery"),
        ("https://www.deviantart.com/shimoda7/gallery/all"),
        ("https://www.deviantart.com/shimoda7/gallery/?catpath=/"),
        ("https://shimoda7.deviantart.com/gallery/"),
        ("https://shimoda7.deviantart.com/gallery/all/"),
        ("https://shimoda7.deviantart.com/gallery/?catpath=/"),
    )

    def deviations(self):
        if self.flat and not self.group:
            return self.api.gallery_all(self.user, self.offset)
        folders = self.api.gallery_folders(self.user)
        return self._folder_urls(folders, "gallery", DeviantartFolderExtractor)


class DeviantartFolderExtractor(DeviantartExtractor):
    """Extractor for deviations inside an artist's gallery folder"""
    subcategory = "folder"
    directory_fmt = ("{category}", "{username}", "{folder[title]}")
    archive_fmt = "F_{folder[uuid]}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/gallery/([^/?#]+)/([^/?#]+)"
    test = (
        # user
        ("https://www.deviantart.com/shimoda7/gallery/722019/Miscellaneous", {
            "count": 5,
            "options": (("original", False),),
        }),
        # group
        ("https://www.deviantart.com/yakuzafc/gallery/37412168/Crafts", {
            "count": ">= 4",
            "options": (("original", False),),
        }),
        # uuid
        (("https://www.deviantart.com/shimoda7/gallery"
          "/B38E3C6A-2029-6B45-757B-3C8D3422AD1A/misc"), {
            "count": 5,
            "options": (("original", False),),
        }),
        # name starts with '_', special characters (#1451)
        (("https://www.deviantart.com/justatest235723"
          "/gallery/69302698/-test-b-c-d-e-f-"), {
            "count": 1,
            "options": (("original", False),),
        }),
        ("https://shimoda7.deviantart.com/gallery/722019/Miscellaneous"),
        ("https://yakuzafc.deviantart.com/gallery/37412168/Crafts"),
    )

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.folder = None
        self.folder_id = match.group(3)
        self.folder_name = match.group(4)

    def deviations(self):
        folders = self.api.gallery_folders(self.user)
        folder = self._find_folder(folders, self.folder_name, self.folder_id)
        self.folder = {
            "title": folder["name"],
            "uuid" : folder["folderid"],
            "index": self.folder_id,
            "owner": self.user,
        }
        return self.api.gallery(self.user, folder["folderid"], self.offset)

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["folder"] = self.folder


class DeviantartStashExtractor(DeviantartExtractor):
    """Extractor for sta.sh-ed deviations"""
    subcategory = "stash"
    archive_fmt = "{index}.{extension}"
    pattern = r"(?:https?://)?sta\.sh/([a-z0-9]+)"
    test = (
        ("https://sta.sh/022c83odnaxc", {
            "pattern": r"https://wixmp-[^.]+\.wixmp\.com"
                       r"/f/.+/.+\.png\?token=.+",
            "content": "057eb2f2861f6c8a96876b13cca1a4b7a408c11f",
            "count": 1,
        }),
        # multiple stash items
        ("https://sta.sh/21jf51j7pzl2", {
            "options": (("original", False),),
            "count": 4,
        }),
        # downloadable, but no "content" field (#307)
        ("https://sta.sh/024t4coz16mi", {
            "pattern": r"https://wixmp-[^.]+\.wixmp\.com"
                       r"/f/.+/.+\.rar\?token=.+",
            "count": 1,
        }),
        # mixed folders and images (#659)
        ("https://sta.sh/215twi387vfj", {
            "options": (("original", False),),
            "count": 4,
        }),
        ("https://sta.sh/abcdefghijkl", {
            "count": 0,
        }),
    )

    skip = Extractor.skip

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.user = None
        self.stash_id = match.group(1)

    def deviations(self, stash_id=None):
        if stash_id is None:
            stash_id = self.stash_id
        url = "https://sta.sh/" + stash_id
        page = self._limited_request(url).text

        if stash_id[0] == "0":
            uuid = text.extr(page, '//deviation/', '"')
            if uuid:
                deviation = self.api.deviation(uuid)
                deviation["index"] = text.parse_int(text.extr(
                    page, 'gmi-deviationid="', '"'))
                yield deviation
                return

        for item in text.extract_iter(
                page, 'class="stash-thumb-container', '</div>'):
            url = text.extr(item, '<a href="', '"')

            if url:
                stash_id = url.rpartition("/")[2]
            else:
                stash_id = text.extr(item, 'gmi-stashid="', '"')
                stash_id = "2" + util.bencode(text.parse_int(
                    stash_id), "0123456789abcdefghijklmnopqrstuvwxyz")

            if len(stash_id) > 2:
                yield from self.deviations(stash_id)


class DeviantartFavoriteExtractor(DeviantartExtractor):
    """Extractor for an artist's favorites"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "{username}", "Favourites")
    archive_fmt = "f_{_username}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/favourites(?:/all|/?\?catpath=)?/?$"
    test = (
        ("https://www.deviantart.com/h3813067/favourites/", {
            "options": (("metadata", True), ("flat", False)),  # issue #271
            "count": 1,
        }),
        ("https://www.deviantart.com/h3813067/favourites/", {
            "content": "6a7c74dc823ebbd457bdd9b3c2838a6ee728091e",
        }),
        ("https://www.deviantart.com/h3813067/favourites/all"),
        ("https://www.deviantart.com/h3813067/favourites/?catpath=/"),
        ("https://h3813067.deviantart.com/favourites/"),
        ("https://h3813067.deviantart.com/favourites/all"),
        ("https://h3813067.deviantart.com/favourites/?catpath=/"),
    )

    def deviations(self):
        if self.flat:
            return self.api.collections_all(self.user, self.offset)
        folders = self.api.collections_folders(self.user)
        return self._folder_urls(
            folders, "favourites", DeviantartCollectionExtractor)


class DeviantartCollectionExtractor(DeviantartExtractor):
    """Extractor for a single favorite collection"""
    subcategory = "collection"
    directory_fmt = ("{category}", "{username}", "Favourites",
                     "{collection[title]}")
    archive_fmt = "C_{collection[uuid]}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/favourites/([^/?#]+)/([^/?#]+)"
    test = (
        (("https://www.deviantart.com/pencilshadings/favourites"
          "/70595441/3D-Favorites"), {
            "count": ">= 15",
            "options": (("original", False),),
        }),
        (("https://www.deviantart.com/pencilshadings/favourites"
          "/F050486B-CB62-3C66-87FB-1105A7F6379F/3D Favorites"), {
            "count": ">= 15",
            "options": (("original", False),),
        }),
        ("https://pencilshadings.deviantart.com"
         "/favourites/70595441/3D-Favorites"),
    )

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.collection = None
        self.collection_id = match.group(3)
        self.collection_name = match.group(4)

    def deviations(self):
        folders = self.api.collections_folders(self.user)
        folder = self._find_folder(
            folders, self.collection_name, self.collection_id)
        self.collection = {
            "title": folder["name"],
            "uuid" : folder["folderid"],
            "index": self.collection_id,
            "owner": self.user,
        }
        return self.api.collections(self.user, folder["folderid"], self.offset)

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["collection"] = self.collection


class DeviantartJournalExtractor(DeviantartExtractor):
    """Extractor for an artist's journals"""
    subcategory = "journal"
    directory_fmt = ("{category}", "{username}", "Journal")
    archive_fmt = "j_{_username}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/(?:posts(?:/journals)?|journal)/?(?:\?.*)?$"
    test = (
        ("https://www.deviantart.com/angrywhitewanker/posts/journals/", {
            "url": "38db2a0d3a587a7e0f9dba7ff7d274610ebefe44",
        }),
        ("https://www.deviantart.com/angrywhitewanker/posts/journals/", {
            "url": "b2a8e74d275664b1a4acee0fca0a6fd33298571e",
            "options": (("journals", "text"),),
        }),
        ("https://www.deviantart.com/angrywhitewanker/posts/journals/", {
            "count": 0,
            "options": (("journals", "none"),),
        }),
        ("https://www.deviantart.com/shimoda7/posts/"),
        ("https://www.deviantart.com/shimoda7/journal/"),
        ("https://www.deviantart.com/shimoda7/journal/?catpath=/"),
        ("https://shimoda7.deviantart.com/journal/"),
        ("https://shimoda7.deviantart.com/journal/?catpath=/"),
    )

    def deviations(self):
        return self.api.browse_user_journals(self.user, self.offset)


class DeviantartStatusExtractor(DeviantartExtractor):
    """Extractor for an artist's status updates"""
    subcategory = "status"
    directory_fmt = ("{category}", "{username}", "Status")
    filename_fmt = "{category}_{index}_{title}_{date}.{extension}"
    archive_fmt = "S_{_username}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/posts/statuses"
    test = (
        ("https://www.deviantart.com/t1na/posts/statuses", {
            "count": 0,
        }),
        ("https://www.deviantart.com/justgalym/posts/statuses", {
            "count": 4,
            "url": "bf4c44c0c60ff2648a880f4c3723464ad3e7d074",
        }),
        # shared deviation
        ("https://www.deviantart.com/justgalym/posts/statuses", {
            "options": (("journals", "none"),),
            "count": 1,
            "pattern": r"https://images-wixmp-\w+\.wixmp\.com/f"
                       r"/[^/]+/[^.]+\.jpg\?token=",
        }),
        # shared sta.sh item
        ("https://www.deviantart.com/vanillaghosties/posts/statuses", {
            "options": (("journals", "none"), ("original", False)),
            "range": "5-",
            "count": 1,
            "keyword": {
                "index"       : int,
                "index_base36": "re:^[0-9a-z]+$",
                "url"         : "re:^https://sta.sh",
            },
        }),
        # "deleted" deviations in 'items'
        ("https://www.deviantart.com/AndrejSKalin/posts/statuses", {
            "options": (("journals", "none"), ("original", 0),
                        ("image-filter", "deviationid[:8] == '147C8B03'")),
            "count": 2,
            "archive": False,
            "keyword": {"deviationid": "147C8B03-7D34-AE93-9241-FA3C6DBBC655"}
        }),
        ("https://www.deviantart.com/justgalym/posts/statuses", {
            "options": (("journals", "text"),),
            "url": "c8744f7f733a3029116607b826321233c5ca452d",
        }),
    )

    def deviations(self):
        for status in self.api.user_statuses(self.user, self.offset):
            yield from self.status(status)

    def status(self, status):
        for item in status.get("items") or ():  # do not trust is_share
            # shared deviations/statuses
            if "deviation" in item:
                yield item["deviation"].copy()
            if "status" in item:
                yield from self.status(item["status"].copy())
        # assume is_deleted == true means necessary fields are missing
        if status["is_deleted"]:
            self.log.warning(
                "Skipping status %s (deleted)", status.get("statusid"))
            return
        yield status

    def prepare(self, deviation):
        if "deviationid" in deviation:
            return DeviantartExtractor.prepare(self, deviation)

        try:
            path = deviation["url"].split("/")
            deviation["index"] = text.parse_int(path[-1] or path[-2])
        except KeyError:
            deviation["index"] = 0

        if self.user:
            deviation["username"] = self.user
            deviation["_username"] = self.user.lower()
        else:
            deviation["username"] = deviation["author"]["username"]
            deviation["_username"] = deviation["username"].lower()

        deviation["date"] = dt = text.parse_datetime(deviation["ts"])
        deviation["published_time"] = int(util.datetime_to_timestamp(dt))

        deviation["da_category"] = "Status"
        deviation["category_path"] = "status"
        deviation["is_downloadable"] = False
        deviation["title"] = "Status Update"

        comments_count = deviation.pop("comments_count", 0)
        deviation["stats"] = {"comments": comments_count}
        if self.comments:
            deviation["comments"] = (
                self.api.comments(deviation["statusid"], target="status")
                if comments_count else ()
            )


class DeviantartPopularExtractor(DeviantartExtractor):
    """Extractor for popular deviations"""
    subcategory = "popular"
    directory_fmt = ("{category}", "Popular",
                     "{popular[range]}", "{popular[search]}")
    archive_fmt = "P_{popular[range]}_{popular[search]}_{index}.{extension}"
    pattern = (r"(?:https?://)?www\.deviantart\.com/(?:"
               r"(?:deviations/?)?\?order=(popular-[^/?#]+)"
               r"|((?:[\w-]+/)*)(popular-[^/?#]+)"
               r")/?(?:\?([^#]*))?")
    test = (
        ("https://www.deviantart.com/?order=popular-all-time", {
            "options": (("original", False),),
            "range": "1-30",
            "count": 30,
        }),
        ("https://www.deviantart.com/popular-24-hours/?q=tree+house", {
            "options": (("original", False),),
            "range": "1-30",
            "count": 30,
        }),
        ("https://www.deviantart.com/artisan/popular-all-time/?q=tree"),
    )

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.user = ""

        trange1, path, trange2, query = match.groups()
        query = text.parse_query(query)
        self.search_term = query.get("q")

        trange = trange1 or trange2 or query.get("order", "")
        if trange.startswith("popular-"):
            trange = trange[8:]
        self.time_range = {
            "newest"      : "now",
            "most-recent" : "now",
            "this-week"   : "1week",
            "this-month"  : "1month",
            "this-century": "alltime",
            "all-time"    : "alltime",
        }.get(trange, "alltime")

        self.popular = {
            "search": self.search_term or "",
            "range" : trange or "all-time",
            "path"  : path.strip("/") if path else "",
        }

    def deviations(self):
        if self.time_range == "now":
            return self.api.browse_newest(self.search_term, self.offset)
        return self.api.browse_popular(
            self.search_term, self.time_range, self.offset)

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["popular"] = self.popular


class DeviantartTagExtractor(DeviantartExtractor):
    """Extractor for deviations from tag searches"""
    subcategory = "tag"
    directory_fmt = ("{category}", "Tags", "{search_tags}")
    archive_fmt = "T_{search_tags}_{index}.{extension}"
    pattern = r"(?:https?://)?www\.deviantart\.com/tag/([^/?#]+)"
    test = ("https://www.deviantart.com/tag/nature", {
        "options": (("original", False),),
        "range": "1-30",
        "count": 30,
    })

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.tag = text.unquote(match.group(1))

    def deviations(self):
        return self.api.browse_tags(self.tag, self.offset)

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["search_tags"] = self.tag


class DeviantartWatchExtractor(DeviantartExtractor):
    """Extractor for Deviations from watched users"""
    subcategory = "watch"
    pattern = (r"(?:https?://)?(?:www\.)?deviantart\.com"
               r"/(?:watch/deviations|notifications/watch)()()")
    test = (
        ("https://www.deviantart.com/watch/deviations"),
        ("https://www.deviantart.com/notifications/watch"),
    )

    def deviations(self):
        return self.api.browse_deviantsyouwatch()


class DeviantartWatchPostsExtractor(DeviantartExtractor):
    """Extractor for Posts from watched users"""
    subcategory = "watch-posts"
    pattern = r"(?:https?://)?(?:www\.)?deviantart\.com/watch/posts()()"
    test = ("https://www.deviantart.com/watch/posts",)

    def deviations(self):
        return self.api.browse_posts_deviantsyouwatch()


###############################################################################
# Eclipse #####################################################################

class DeviantartDeviationExtractor(DeviantartExtractor):
    """Extractor for single deviations"""
    subcategory = "deviation"
    archive_fmt = "g_{_username}_{index}.{extension}"
    pattern = (BASE_PATTERN + r"/(art|journal)/(?:[^/?#]+-)?(\d+)"
               r"|(?:https?://)?(?:www\.)?(?:fx)?deviantart\.com/"
               r"(?:view/|deviation/|view(?:-full)?\.php/*\?(?:[^#]+&)?id=)"
               r"(\d+)"  # bare deviation ID without slug
               r"|(?:https?://)?fav\.me/d([0-9a-z]+)")  # base36
    test = (
        (("https://www.deviantart.com/shimoda7/art/For-the-sake-10073852"), {
            "options": (("original", 0),),
            "content": "6a7c74dc823ebbd457bdd9b3c2838a6ee728091e",
        }),
        ("https://www.deviantart.com/zzz/art/zzz-1234567890", {
            "exception": exception.NotFoundError,
        }),
        (("https://www.deviantart.com/myria-moon/art/Aime-Moi-261986576"), {
            "options": (("comments", True),),
            "keyword": {"comments": list},
            "pattern": r"https://wixmp-[^.]+\.wixmp\.com"
                       r"/f/.+/.+\.jpg\?token=.+",
        }),
        # wixmp URL rewrite
        (("https://www.deviantart.com/citizenfresh/art/Hverarond-789295466"), {
            "pattern": (r"https://images-wixmp-\w+\.wixmp\.com/f"
                        r"/[^/]+/[^.]+\.jpg\?token="),
        }),
        # GIF (#242)
        (("https://www.deviantart.com/skatergators/art/COM-Moni-781571783"), {
            "pattern": r"https://wixmp-\w+\.wixmp\.com/f/03fd2413-efe9-4e5c-"
                       r"8734-2b72605b3fbb/dcxbsnb-1bbf0b38-42af-4070-8878-"
                       r"f30961955bec\.gif\?token=ey...",
        }),
        # Flash animation with GIF preview (#1731)
        ("https://www.deviantart.com/yuumei/art/Flash-Comic-214724929", {
            "pattern": r"https://wixmp-[^.]+\.wixmp\.com"
                       r"/f/.+/.+\.swf\?token=.+",
            "keyword": {
                "filename": "flash_comic_tutorial_by_yuumei-d3juatd",
                "extension": "swf",
            },
        }),
        # sta.sh URLs from description (#302)
        (("https://www.deviantart.com/uotapo/art/INANAKI-Memo-590297498"), {
            "options": (("extra", 1), ("original", 0)),
            "pattern": DeviantartStashExtractor.pattern,
            "range": "2-",
            "count": 4,
        }),
        # sta.sh URL from deviation["text_content"]["body"]["features"]
        (("https://www.deviantart.com"
          "/cimar-wildehopps/art/Honorary-Vixen-859809305"), {
            "options": (("extra", 1),),
            "pattern": ("text:<!DOCTYPE html>\n|" +
                        DeviantartStashExtractor.pattern),
            "count": 2,
        }),
        # journal
        ("https://www.deviantart.com/shimoda7/journal/ARTility-583755752", {
            "url": "d34b2c9f873423e665a1b8ced20fcb75951694a3",
            "pattern": "text:<!DOCTYPE html>\n",
        }),
        # journal-like post with isJournal == False (#419)
        ("https://www.deviantart.com/gliitchlord/art/brashstrokes-812942668", {
            "url": "e2e0044bd255304412179b6118536dbd9bb3bb0e",
            "pattern": "text:<!DOCTYPE html>\n",
        }),
        # /view/ URLs
        ("https://deviantart.com/view/904858796/", {
            "content": "8770ec40ad1c1d60f6b602b16301d124f612948f",
        }),
        ("http://www.deviantart.com/view/890672057", {
            "content": "1497e13d925caeb13a250cd666b779a640209236",
        }),
        ("https://www.deviantart.com/view/706871727", {
            "content": "3f62ae0c2fca2294ac28e41888ea06bb37c22c65",
        }),
        ("https://www.deviantart.com/view/1", {
            "exception": exception.NotFoundError,
        }),
        # /deviation/ (#3558)
        ("https://www.deviantart.com/deviation/817215762"),
        # fav.me (#3558)
        ("https://fav.me/ddijrpu", {
            "count": 1,
        }),
        ("https://fav.me/dddd", {
            "exception": exception.NotFoundError,
        }),
        # old-style URLs
        ("https://shimoda7.deviantart.com"
         "/art/For-the-sake-of-a-memory-10073852"),
        ("https://myria-moon.deviantart.com"
         "/art/Aime-Moi-part-en-vadrouille-261986576"),
        ("https://zzz.deviantart.com/art/zzz-1234567890"),
        # old /view/ URLs from the Wayback Machine
        ("https://www.deviantart.com/view.php?id=14864502"),
        ("http://www.deviantart.com/view-full.php?id=100842"),

        ("https://www.fxdeviantart.com/zzz/art/zzz-1234567890"),
        ("https://www.fxdeviantart.com/view/1234567890"),
    )

    skip = Extractor.skip

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.type = match.group(3)
        self.deviation_id = \
            match.group(4) or match.group(5) or id_from_base36(match.group(6))

    def deviations(self):
        url = "{}/{}/{}/{}".format(
            self.root, self.user or "u", self.type or "art", self.deviation_id)

        uuid = text.extract(self._limited_request(url).text,
                            '"deviationUuid\\":\\"', '\\')[0]
        if not uuid:
            raise exception.NotFoundError("deviation")
        return (self.api.deviation(uuid),)


class DeviantartScrapsExtractor(DeviantartExtractor):
    """Extractor for an artist's scraps"""
    subcategory = "scraps"
    directory_fmt = ("{category}", "{username}", "Scraps")
    archive_fmt = "s_{_username}_{index}.{extension}"
    cookiedomain = ".deviantart.com"
    pattern = BASE_PATTERN + r"/gallery/(?:\?catpath=)?scraps\b"
    test = (
        ("https://www.deviantart.com/shimoda7/gallery/scraps", {
            "count": 12,
        }),
        ("https://www.deviantart.com/shimoda7/gallery/?catpath=scraps"),
        ("https://shimoda7.deviantart.com/gallery/?catpath=scraps"),
    )

    def deviations(self):
        self.login()

        eclipse_api = DeviantartEclipseAPI(self)
        return self._eclipse_to_oauth(
            eclipse_api, eclipse_api.gallery_scraps(self.user, self.offset))


class DeviantartSearchExtractor(DeviantartExtractor):
    """Extractor for deviantart search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search_tags}")
    archive_fmt = "Q_{search_tags}_{index}.{extension}"
    cookiedomain = ".deviantart.com"
    pattern = (r"(?:https?://)?www\.deviantart\.com"
               r"/search(?:/deviations)?/?\?([^#]+)")
    test = (
        ("https://www.deviantart.com/search?q=tree"),
        ("https://www.deviantart.com/search/deviations?order=popular-1-week"),
    )

    skip = Extractor.skip

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.query = text.parse_query(self.user)
        self.search = self.query.get("q", "")
        self.user = ""

    def deviations(self):
        logged_in = self.login()

        eclipse_api = DeviantartEclipseAPI(self)
        search = (eclipse_api.search_deviations
                  if logged_in else self._search_html)
        return self._eclipse_to_oauth(eclipse_api, search(self.query))

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["search_tags"] = self.search

    def _search_html(self, params):
        url = self.root + "/search"
        deviation = {
            "deviationId": None,
            "author": {"username": "u"},
            "isJournal": False,
        }

        while True:
            response = self.request(url, params=params)

            if response.history and "/users/login" in response.url:
                raise exception.StopExtraction("HTTP redirect to login page")
            page = response.text

            items , pos = text.rextract(page, r'\"items\":[', ']')
            cursor, pos = text.extract(page, r'\"cursor\":\"', '\\', pos)

            for deviation_id in items.split(","):
                deviation["deviationId"] = deviation_id
                yield deviation

            if not cursor:
                return
            params["cursor"] = cursor


class DeviantartGallerySearchExtractor(DeviantartExtractor):
    """Extractor for deviantart gallery searches"""
    subcategory = "gallery-search"
    archive_fmt = "g_{_username}_{index}.{extension}"
    cookiedomain = ".deviantart.com"
    pattern = BASE_PATTERN + r"/gallery/?\?(q=[^#]+)"
    test = (
        ("https://www.deviantart.com/shimoda7/gallery?q=memory", {
            "options": (("original", 0),),
            "content": "6a7c74dc823ebbd457bdd9b3c2838a6ee728091e",
        }),
        ("https://www.deviantart.com/shimoda7/gallery?q=memory&sort=popular"),
    )

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.query = match.group(3)

    def deviations(self):
        self.login()

        eclipse_api = DeviantartEclipseAPI(self)
        info = eclipse_api.user_info(self.user)

        query = text.parse_query(self.query)
        self.search = query["q"]

        return self._eclipse_to_oauth(
            eclipse_api, eclipse_api.galleries_search(
                info["user"]["userId"],
                self.search,
                self.offset,
                query.get("sort", "most-recent"),
            ))

    def prepare(self, deviation):
        DeviantartExtractor.prepare(self, deviation)
        deviation["search_tags"] = self.search


class DeviantartFollowingExtractor(DeviantartExtractor):
    """Extractor for user's watched users"""
    subcategory = "following"
    pattern = BASE_PATTERN + "/about#watching$"
    test = ("https://www.deviantart.com/shimoda7/about#watching", {
        "pattern": DeviantartUserExtractor.pattern,
        "range": "1-50",
        "count": 50,
    })

    def items(self):
        eclipse_api = DeviantartEclipseAPI(self)

        for user in eclipse_api.user_watching(self.user, self.offset):
            url = "{}/{}".format(self.root, user["username"])
            user["_extractor"] = DeviantartUserExtractor
            yield Message.Queue, url, user


###############################################################################
# API Interfaces ##############################################################

class DeviantartOAuthAPI():
    """Interface for the DeviantArt OAuth API

    Ref: https://www.deviantart.com/developers/http/v1/20160316
    """
    CLIENT_ID = "5388"
    CLIENT_SECRET = "76b08c69cfb27f26d6161f9ab6d061a1"

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log
        self.headers = {"dA-minor-version": "20200519"}
        self._warn_429 = True

        self.delay = extractor.config("wait-min", 0)
        self.delay_min = max(2, self.delay)

        self.mature = extractor.config("mature", "true")
        if not isinstance(self.mature, str):
            self.mature = "true" if self.mature else "false"

        self.folders = extractor.config("folders", False)
        self.metadata = extractor.extra or extractor.config("metadata", False)
        self.strategy = extractor.config("pagination")
        self.public = extractor.config("public", True)

        self.client_id = extractor.config("client-id")
        if self.client_id:
            self.client_secret = extractor.config("client-secret")
        else:
            self.client_id = self.CLIENT_ID
            self.client_secret = self.CLIENT_SECRET

        token = extractor.config("refresh-token")
        if token is None or token == "cache":
            token = "#" + str(self.client_id)
            if not _refresh_token_cache(token):
                token = None
        self.refresh_token_key = token

        self.log.debug(
            "Using %s API credentials (client-id %s)",
            "default" if self.client_id == self.CLIENT_ID else "custom",
            self.client_id,
        )

    def browse_deviantsyouwatch(self, offset=0):
        """Yield deviations from users you watch"""
        endpoint = "/browse/deviantsyouwatch"
        params = {"limit": "50", "offset": offset,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params, public=False)

    def browse_posts_deviantsyouwatch(self, offset=0):
        """Yield posts from users you watch"""
        endpoint = "/browse/posts/deviantsyouwatch"
        params = {"limit": "50", "offset": offset,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params, public=False, unpack=True)

    def browse_newest(self, query=None, offset=0):
        """Browse newest deviations"""
        endpoint = "/browse/newest"
        params = {
            "q"             : query,
            "limit"         : 50 if self.metadata else 120,
            "offset"        : offset,
            "mature_content": self.mature,
        }
        return self._pagination(endpoint, params)

    def browse_popular(self, query=None, timerange=None, offset=0):
        """Yield popular deviations"""
        endpoint = "/browse/popular"
        params = {
            "q"             : query,
            "limit"         : 50 if self.metadata else 120,
            "timerange"     : timerange,
            "offset"        : offset,
            "mature_content": self.mature,
        }
        return self._pagination(endpoint, params)

    def browse_tags(self, tag, offset=0):
        """ Browse a tag """
        endpoint = "/browse/tags"
        params = {
            "tag"           : tag,
            "offset"        : offset,
            "limit"         : 50,
            "mature_content": self.mature,
        }
        return self._pagination(endpoint, params)

    def browse_user_journals(self, username, offset=0):
        """Yield all journal entries of a specific user"""
        endpoint = "/browse/user/journals"
        params = {"username": username, "offset": offset, "limit": 50,
                  "mature_content": self.mature, "featured": "false"}
        return self._pagination(endpoint, params)

    def collections(self, username, folder_id, offset=0):
        """Yield all Deviation-objects contained in a collection folder"""
        endpoint = "/collections/" + folder_id
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    def collections_all(self, username, offset=0):
        """Yield all deviations in a user's collection"""
        endpoint = "/collections/all"
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    @memcache(keyarg=1)
    def collections_folders(self, username, offset=0):
        """Yield all collection folders of a specific user"""
        endpoint = "/collections/folders"
        params = {"username": username, "offset": offset, "limit": 50,
                  "mature_content": self.mature}
        return self._pagination_list(endpoint, params)

    def comments(self, id, target, offset=0):
        """Fetch comments posted on a target"""
        endpoint = "/comments/{}/{}".format(target, id)
        params = {"maxdepth": "5", "offset": offset, "limit": 50,
                  "mature_content": self.mature}
        return self._pagination_list(endpoint, params=params, key="thread")

    def deviation(self, deviation_id, public=None):
        """Query and return info about a single Deviation"""
        endpoint = "/deviation/" + deviation_id
        deviation = self._call(endpoint, public=public)
        if self.metadata:
            self._metadata((deviation,))
        if self.folders:
            self._folders((deviation,))
        return deviation

    def deviation_content(self, deviation_id, public=None):
        """Get extended content of a single Deviation"""
        endpoint = "/deviation/content"
        params = {"deviationid": deviation_id}
        content = self._call(endpoint, params=params, public=public)
        if public and content["html"].startswith(
                '        <span class=\"username-with-symbol'):
            if self.refresh_token_key:
                content = self._call(endpoint, params=params, public=False)
            else:
                self.log.warning("Private Journal")
        return content

    def deviation_download(self, deviation_id, public=None):
        """Get the original file download (if allowed)"""
        endpoint = "/deviation/download/" + deviation_id
        params = {"mature_content": self.mature}

        try:
            return self._call(
                endpoint, params=params, public=public, log=False)
        except Exception:
            if not self.refresh_token_key:
                raise
            return self._call(endpoint, params=params, public=False)

    def deviation_metadata(self, deviations):
        """ Fetch deviation metadata for a set of deviations"""
        endpoint = "/deviation/metadata?" + "&".join(
            "deviationids[{}]={}".format(num, deviation["deviationid"])
            for num, deviation in enumerate(deviations)
        )
        params = {"mature_content": self.mature}
        return self._call(endpoint, params=params)["metadata"]

    def gallery(self, username, folder_id, offset=0, extend=True, public=None):
        """Yield all Deviation-objects contained in a gallery folder"""
        endpoint = "/gallery/" + folder_id
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature, "mode": "newest"}
        return self._pagination(endpoint, params, extend, public)

    def gallery_all(self, username, offset=0):
        """Yield all Deviation-objects of a specific user"""
        endpoint = "/gallery/all"
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature}
        return self._pagination(endpoint, params)

    @memcache(keyarg=1)
    def gallery_folders(self, username, offset=0):
        """Yield all gallery folders of a specific user"""
        endpoint = "/gallery/folders"
        params = {"username": username, "offset": offset, "limit": 50,
                  "mature_content": self.mature}
        return self._pagination_list(endpoint, params)

    @memcache(keyarg=1)
    def user_profile(self, username):
        """Get user profile information"""
        endpoint = "/user/profile/" + username
        return self._call(endpoint, fatal=False)

    def user_statuses(self, username, offset=0):
        """Yield status updates of a specific user"""
        endpoint = "/user/statuses/"
        params = {"username": username, "offset": offset, "limit": 50}
        return self._pagination(endpoint, params)

    def user_friends_watch(self, username):
        """Watch a user"""
        endpoint = "/user/friends/watch/" + username
        data = {
            "watch[friend]"       : "0",
            "watch[deviations]"   : "0",
            "watch[journals]"     : "0",
            "watch[forum_threads]": "0",
            "watch[critiques]"    : "0",
            "watch[scraps]"       : "0",
            "watch[activity]"     : "0",
            "watch[collections]"  : "0",
            "mature_content"      : self.mature,
        }
        return self._call(
            endpoint, method="POST", data=data, public=False, fatal=False,
        ).get("success")

    def user_friends_unwatch(self, username):
        """Unwatch a user"""
        endpoint = "/user/friends/unwatch/" + username
        return self._call(
            endpoint, method="POST", public=False, fatal=False,
        ).get("success")

    def authenticate(self, refresh_token_key):
        """Authenticate the application by requesting an access token"""
        self.headers["Authorization"] = \
            self._authenticate_impl(refresh_token_key)

    @cache(maxage=3600, keyarg=1)
    def _authenticate_impl(self, refresh_token_key):
        """Actual authenticate implementation"""
        url = "https://www.deviantart.com/oauth2/token"
        if refresh_token_key:
            self.log.info("Refreshing private access token")
            data = {"grant_type": "refresh_token",
                    "refresh_token": _refresh_token_cache(refresh_token_key)}
        else:
            self.log.info("Requesting public access token")
            data = {"grant_type": "client_credentials"}

        auth = (self.client_id, self.client_secret)
        response = self.extractor.request(
            url, method="POST", data=data, auth=auth, fatal=False)
        data = response.json()

        if response.status_code != 200:
            self.log.debug("Server response: %s", data)
            raise exception.AuthenticationError('"{}" ({})'.format(
                data.get("error_description"), data.get("error")))
        if refresh_token_key:
            _refresh_token_cache.update(
                refresh_token_key, data["refresh_token"])
        return "Bearer " + data["access_token"]

    def _call(self, endpoint, fatal=True, log=True, public=None, **kwargs):
        """Call an API endpoint"""
        url = "https://www.deviantart.com/api/v1/oauth2" + endpoint
        kwargs["fatal"] = None

        if public is None:
            public = self.public

        while True:
            if self.delay:
                self.extractor.sleep(self.delay, "api")

            self.authenticate(None if public else self.refresh_token_key)
            kwargs["headers"] = self.headers
            response = self.extractor.request(url, **kwargs)
            data = response.json()
            status = response.status_code

            if 200 <= status < 400:
                if self.delay > self.delay_min:
                    self.delay -= 1
                return data
            if not fatal and status != 429:
                return None
            if data.get("error_description") == "User not found.":
                raise exception.NotFoundError("user or group")

            self.log.debug(response.text)
            msg = "API responded with {} {}".format(
                status, response.reason)
            if status == 429:
                if self.delay < 30:
                    self.delay += 1
                self.log.warning("%s. Using %ds delay.", msg, self.delay)

                if self._warn_429 and self.delay >= 3:
                    self._warn_429 = False
                    if self.client_id == self.CLIENT_ID:
                        self.log.info(
                            "Register your own OAuth application and use its "
                            "credentials to prevent this error: "
                            "https://github.com/mikf/gallery-dl/blob/master/do"
                            "cs/configuration.rst#extractordeviantartclient-id"
                            "--client-secret")
            else:
                if log:
                    self.log.error(msg)
                return data

    def _pagination(self, endpoint, params,
                    extend=True, public=None, unpack=False, key="results"):
        warn = True
        if public is None:
            public = self.public

        while True:
            data = self._call(endpoint, params=params, public=public)
            try:
                results = data[key]
            except KeyError:
                self.log.error("Unexpected API response: %s", data)
                return

            if unpack:
                results = [item["journal"] for item in results
                           if "journal" in item]
            if extend:
                if public and len(results) < params["limit"]:
                    if self.refresh_token_key:
                        self.log.debug("Switching to private access token")
                        public = False
                        continue
                    elif data["has_more"] and warn:
                        warn = False
                        self.log.warning(
                            "Private deviations detected! Run 'gallery-dl "
                            "oauth:deviantart' and follow the instructions to "
                            "be able to access them.")
                # "statusid" cannot be used instead
                if results and "deviationid" in results[0]:
                    if self.metadata:
                        self._metadata(results)
                    if self.folders:
                        self._folders(results)
                else:  # attempt to fix "deleted" deviations
                    for dev in self._shared_content(results):
                        if not dev["is_deleted"]:
                            continue
                        patch = self._call(
                            "/deviation/" + dev["deviationid"], fatal=False)
                        if patch:
                            dev.update(patch)

            yield from results

            if not data["has_more"] and (
                    self.strategy != "manual" or not results or not extend):
                return

            if "next_cursor" in data:
                params["offset"] = None
                params["cursor"] = data["next_cursor"]
            elif data["next_offset"] is not None:
                params["offset"] = data["next_offset"]
                params["cursor"] = None
            else:
                if params.get("offset") is None:
                    return
                params["offset"] = int(params["offset"]) + len(results)

    @staticmethod
    def _shared_content(results):
        """Return an iterable of shared deviations in 'results'"""
        for result in results:
            for item in result.get("items") or ():
                if "deviation" in item:
                    yield item["deviation"]

    def _pagination_list(self, endpoint, params, key="results"):
        result = []
        result.extend(self._pagination(endpoint, params, False, key=key))
        return result

    def _metadata(self, deviations):
        """Add extended metadata to each deviation object"""
        for deviation, metadata in zip(
                deviations, self.deviation_metadata(deviations)):
            deviation.update(metadata)
            deviation["tags"] = [t["tag_name"] for t in deviation["tags"]]

    def _folders(self, deviations):
        """Add a list of all containing folders to each deviation object"""
        for deviation in deviations:
            deviation["folders"] = self._folders_map(
                deviation["author"]["username"])[deviation["deviationid"]]

    @memcache(keyarg=1)
    def _folders_map(self, username):
        """Generate a deviation_id -> folders mapping for 'username'"""
        self.log.info("Collecting folder information for '%s'", username)
        folders = self.gallery_folders(username)

        # create 'folderid'-to-'folder' mapping
        fmap = {
            folder["folderid"]: folder
            for folder in folders
        }

        # add parent names to folders, but ignore "Featured" as parent
        featured = folders[0]["folderid"]
        done = False

        while not done:
            done = True
            for folder in folders:
                parent = folder["parent"]
                if not parent:
                    pass
                elif parent == featured:
                    folder["parent"] = None
                else:
                    parent = fmap[parent]
                    if parent["parent"]:
                        done = False
                    else:
                        folder["name"] = parent["name"] + "/" + folder["name"]
                        folder["parent"] = None

        # map deviationids to folder names
        dmap = collections.defaultdict(list)
        for folder in folders:
            for deviation in self.gallery(
                    username, folder["folderid"], 0, False):
                dmap[deviation["deviationid"]].append(folder["name"])
        return dmap


class DeviantartEclipseAPI():
    """Interface to the DeviantArt Eclipse API"""

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log
        self.request = self.extractor._limited_request
        self.csrf_token = None

    def deviation_extended_fetch(self, deviation_id, user=None, kind=None):
        endpoint = "/da-browse/shared_api/deviation/extended_fetch"
        params = {
            "deviationid"    : deviation_id,
            "username"       : user,
            "type"           : kind,
            "include_session": "false",
        }
        return self._call(endpoint, params)

    def gallery_scraps(self, user, offset=None):
        endpoint = "/da-user-profile/api/gallery/contents"
        params = {
            "username"     : user,
            "offset"       : offset,
            "limit"        : 24,
            "scraps_folder": "true",
        }
        return self._pagination(endpoint, params)

    def galleries_search(self, user_id, query,
                         offset=None, order="most-recent"):
        endpoint = "/shared_api/galleries/search"
        params = {
            "userid": user_id,
            "order" : order,
            "q"     : query,
            "offset": offset,
            "limit" : 24,
        }
        return self._pagination(endpoint, params)

    def search_deviations(self, params):
        endpoint = "/da-browse/api/networkbar/search/deviations"
        return self._pagination(endpoint, params, key="deviations")

    def user_info(self, user, expand=False):
        endpoint = "/shared_api/user/info"
        params = {"username": user}
        if expand:
            params["expand"] = "user.stats,user.profile,user.watch"
        return self._call(endpoint, params)

    def user_watching(self, user, offset=None):
        endpoint = "/da-user-profile/api/module/watching"
        params = {
            "username": user,
            "moduleid": self._module_id_watching(user),
            "offset"  : offset,
            "limit"   : 24,
        }
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params):
        url = "https://www.deviantart.com/_napi" + endpoint
        headers = {"Referer": "https://www.deviantart.com/"}
        params["csrf_token"] = self.csrf_token or self._fetch_csrf_token()

        response = self.request(
            url, params=params, headers=headers, fatal=None)

        if response.status_code == 404:
            raise exception.StopExtraction(
                "Your account must use the Eclipse interface.")
        try:
            return response.json()
        except Exception:
            return {"error": response.text}

    def _pagination(self, endpoint, params, key="results"):
        limit = params.get("limit", 24)
        warn = True

        while True:
            data = self._call(endpoint, params)

            results = data.get(key)
            if results is None:
                return
            if len(results) < limit and warn and data.get("hasMore"):
                warn = False
                self.log.warning(
                    "Private deviations detected! "
                    "Provide login credentials or session cookies "
                    "to be able to access them.")
            yield from results

            if not data.get("hasMore"):
                return

            if "nextCursor" in data:
                params["offset"] = None
                params["cursor"] = data["nextCursor"]
            elif "nextOffset" in data:
                params["offset"] = data["nextOffset"]
                params["cursor"] = None
            elif params.get("offset") is None:
                return
            else:
                params["offset"] = int(params["offset"]) + len(results)

    def _module_id_watching(self, user):
        url = "{}/{}/about".format(self.extractor.root, user)
        page = self.request(url).text
        pos = page.find('\\"type\\":\\"watching\\"')
        if pos < 0:
            raise exception.NotFoundError("module")
        self._fetch_csrf_token(page)
        return text.rextract(page, '\\"id\\":', ',', pos)[0].strip('" ')

    def _fetch_csrf_token(self, page=None):
        if page is None:
            page = self.request(self.extractor.root + "/").text
        self.csrf_token = token = text.extr(
            page, "window.__CSRF_TOKEN__ = '", "'")
        return token


@cache(maxage=100*365*86400, keyarg=0)
def _refresh_token_cache(token):
    if token and token[0] == "#":
        return None
    return token


@cache(maxage=28*86400, keyarg=1)
def _login_impl(extr, username, password):
    extr.log.info("Logging in as %s", username)

    url = "https://www.deviantart.com/users/login"
    page = extr.request(url).text

    data = {}
    for item in text.extract_iter(page, '<input type="hidden" name="', '"/>'):
        name, _, value = item.partition('" value="')
        data[name] = value

    challenge = data.get("challenge")
    if challenge and challenge != "0":
        extr.log.warning("Login requires solving a CAPTCHA")
        extr.log.debug(challenge)

    data["username"] = username
    data["password"] = password
    data["remember"] = "on"

    extr.sleep(2.0, "login")
    url = "https://www.deviantart.com/_sisu/do/signin"
    response = extr.request(url, method="POST", data=data)

    if not response.history:
        raise exception.AuthenticationError()

    return {
        cookie.name: cookie.value
        for cookie in extr.session.cookies
    }


def id_from_base36(base36):
    return util.bdecode(base36, _ALPHABET)


def base36_from_id(deviation_id):
    return util.bencode(int(deviation_id), _ALPHABET)


_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"


###############################################################################
# Journal Formats #############################################################

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

JOURNAL_TEMPLATE_HTML_EXTRA = """\
<div id="devskin0"><div class="negate-box-margin" style="">\
<div usr class="gr-box gr-genericbox"
        ><i usr class="gr1"><i></i></i
        ><i usr class="gr2"><i></i></i
        ><i usr class="gr3"><i></i></i
        ><div usr class="gr-top">
            <i usr class="tri"></i>
            {}
            </div>
    </div><div usr class="gr-body"><div usr class="gr">
            <div class="grf-indent">
            <div class="text">
                {}            </div>
        </div>
                </div></div>
        <i usr class="gr3 gb"></i>
        <i usr class="gr2 gb"></i>
        <i usr class="gr1 gb gb1"></i>    </div>
    </div></div>"""

JOURNAL_TEMPLATE_TEXT = """text:{title}
by {username}, {date}

{content}
"""
