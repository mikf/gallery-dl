# -*- coding: utf-8 -*-

# Copyright 2015-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.deviantart.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache, memcache
import collections
import itertools
import mimetypes
import math
import time
import re


BASE_PATTERN = (
    r"(?:https?://)?(?:"
    r"(?:www\.)?deviantart\.com/([\w-]+)|"
    r"(?!www\.)([\w-]+)\.deviantart\.com)"
)


class DeviantartExtractor(Extractor):
    """Base class for deviantart extractors using the OAuth API"""
    category = "deviantart"
    directory_fmt = ("{category}", "{username}")
    filename_fmt = "{category}_{index}_{title}.{extension}"
    cookiedomain = None
    root = "https://www.deviantart.com"

    def __init__(self, match=None):
        Extractor.__init__(self, match)
        self.offset = 0
        self.flat = self.config("flat", True)
        self.extra = self.config("extra", False)
        self.quality = self.config("quality", "100")
        self.original = self.config("original", True)
        self.user = match.group(1) or match.group(2)
        self.group = False
        self.api = DeviantartAPI(self)

        if self.quality:
            self.quality = "q_{}".format(self.quality)

        if self.original != "image":
            self._update_content = self._update_content_default
        else:
            self._update_content = self._update_content_image
            self.original = True

        self.commit_journal = {
            "html": self._commit_journal_html,
            "text": self._commit_journal_text,
        }.get(self.config("journals", "html"))

    def skip(self, num):
        self.offset += num
        return num

    def items(self):
        if self.user:
            profile = self.api.user_profile(self.user)
            self.group = not profile
            if self.group:
                self.subcategory = "group-" + self.subcategory
                self.user = self.user.lower()
            else:
                self.user = profile["user"]["username"]

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

                if content["src"].startswith("https://images-wixmp-"):
                    if deviation["index"] <= 790677560:
                        # https://github.com/r888888888/danbooru/issues/4069
                        intermediary, count = re.subn(
                            r"(/f/[^/]+/[^/]+)/v\d+/.*",
                            r"/intermediary\1", content["src"])
                        if count and self._check_url(intermediary):
                            content["src"] = intermediary
                    if self.quality:
                        content["src"] = re.sub(
                            r"q_\d+", self.quality, content["src"])

                yield self.commit(deviation, content)

            elif deviation["is_downloadable"]:
                content = self.api.deviation_download(deviation["deviationid"])
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

            if self.extra:
                for match in DeviantartStashExtractor.pattern.finditer(
                        deviation.get("description", "")):
                    deviation["_extractor"] = DeviantartStashExtractor
                    yield Message.Queue, match.group(0), deviation

    def deviations(self):
        """Return an iterable containing all relevant Deviation-objects"""

    def prepare(self, deviation):
        """Adjust the contents of a Deviation-object"""
        try:
            deviation["index"] = text.parse_int(
                deviation["url"].rpartition("-")[2])
        except KeyError:
            deviation["index"] = 0

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

        # filename metadata
        alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
        sub = re.compile(r"\W").sub
        deviation["filename"] = "".join((
            sub("_", deviation["title"].lower()), "_by_",
            sub("_", deviation["author"]["username"].lower()), "-d",
            util.bencode(deviation["index"], alphabet),
        ))

    @staticmethod
    def commit(deviation, target):
        url = target["src"]
        target = target.copy()
        target["filename"] = deviation["filename"]
        deviation["target"] = target
        deviation["extension"] = target["extension"] = text.ext_from_url(url)
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
        content = "\n".join(
            text.unescape(text.remove_html(txt))
            for txt in html.rpartition("<script")[0].split("<br />")
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
        pattern = re.compile(r"(?i)\W*" + name.replace("-", r"\W+") + r"\W*$")
        for folder in folders:
            if pattern.match(folder["name"]):
                return folder
        raise exception.NotFoundError("folder")

    def _folder_urls(self, folders, category):
        url = "{}/{}/{}/0/".format(self.root, self.user, category)
        return [(url + folder["name"], folder) for folder in folders]

    def _update_content_default(self, deviation, content):
        content.update(self.api.deviation_download(deviation["deviationid"]))

    def _update_content_image(self, deviation, content):
        data = self.api.deviation_download(deviation["deviationid"])
        url = data["src"].partition("?")[0]
        mtype = mimetypes.guess_type(url, False)[0]
        if mtype and mtype.startswith("image/"):
            content.update(data)

    def _check_url(self, url):
        return self.request(url, method="HEAD", fatal=False).status_code < 400


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
            "pattern": r"/shimoda7/(gallery(/scraps)?|posts|favourites)$",
            "count": 4,
        }),
        ("https://shimoda7.deviantart.com/"),
    )

    def items(self):
        base = "{}/{}/".format(self.root, self.user)
        return self._dispatch_extractors((
            (DeviantartGalleryExtractor , base + "gallery"),
            (DeviantartScrapsExtractor  , base + "gallery/scraps"),
            (DeviantartJournalExtractor , base + "posts"),
            (DeviantartFavoriteExtractor, base + "favourites"),
        ), ("gallery",))


class DeviantartGalleryExtractor(DeviantartExtractor):
    """Extractor for all deviations from an artist's gallery"""
    subcategory = "gallery"
    archive_fmt = "g_{_username}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/gallery(?:/all|/?\?catpath=)?/?$"
    test = (
        ("https://www.deviantart.com/shimoda7/gallery/", {
            "pattern": r"https://(api-da\.wixmp\.com/_api/download/file"
                       r"|images-wixmp-[^.]+.wixmp.com/f/.+/.+.jpg\?token=.+)",
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
            "pattern": r"https://www.deviantart.com/yakuzafc/gallery/0/",
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
        return self._folder_urls(folders, "gallery")


class DeviantartFolderExtractor(DeviantartExtractor):
    """Extractor for deviations inside an artist's gallery folder"""
    subcategory = "folder"
    directory_fmt = ("{category}", "{username}", "{folder[title]}")
    archive_fmt = "F_{folder[uuid]}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/gallery/(\d+)/([^/?&#]+)"
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
        folder = self._find_folder(folders, self.folder_name)
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
            "pattern": r"https://api-da\.wixmp\.com/_api/download/file",
            "content": "057eb2f2861f6c8a96876b13cca1a4b7a408c11f",
            "count": 1,
        }),
        # multiple stash items
        ("https://sta.sh/21jf51j7pzl2", {
            "pattern": pattern,
            "count": 4,
        }),
        # downloadable, but no "content" field (#307)
        ("https://sta.sh/024t4coz16mi", {
            "pattern": r"https://api-da\.wixmp\.com/_api/download/file",
            "count": 1,
        }),
        ("https://sta.sh/abcdefghijkl", {
            "exception": exception.HttpError,
        }),
    )

    skip = Extractor.skip

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.user = None
        self.stash_id = match.group(1)

    def deviations(self):
        url = "https://sta.sh/" + self.stash_id
        page = self.request(url).text
        deviation_id = text.extract(page, '//deviation/', '"')[0]

        if deviation_id:
            return (self.api.deviation(deviation_id),)

        else:
            data = {"_extractor": DeviantartStashExtractor}
            page = text.extract(page, 'id="stash-body"', 'class="footer"')[0]
            return [
                (url, data)
                for url in text.extract_iter(page, '<a href="', '"')
            ]


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
        folders = self.api.collections_folders(self.user)
        if self.flat:
            return itertools.chain.from_iterable(
                self.api.collections(self.user, folder["folderid"])
                for folder in folders
            )
        return self._folder_urls(folders, "favourites")


class DeviantartCollectionExtractor(DeviantartExtractor):
    """Extractor for a single favorite collection"""
    subcategory = "collection"
    directory_fmt = ("{category}", "{username}", "Favourites",
                     "{collection[title]}")
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
        self.collection = None
        self.collection_id = match.group(3)
        self.collection_name = match.group(4)

    def deviations(self):
        folders = self.api.collections_folders(self.user)
        folder = self._find_folder(folders, self.collection_name)
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


class DeviantartPopularExtractor(DeviantartExtractor):
    """Extractor for popular deviations"""
    subcategory = "popular"
    directory_fmt = ("{category}", "Popular",
                     "{popular[range]}", "{popular[search]}")
    archive_fmt = "P_{popular[range]}_{popular[search]}_{index}.{extension}"
    pattern = (r"(?:https?://)?www\.deviantart\.com/(?:"
               r"search(?:/deviations)?"
               r"|(?:deviations/?)?\?order=(popular-[^/?&#]+)"
               r"|((?:[\w-]+/)*)(popular-[^/?&#]+)"
               r")/?(?:\?([^#]*))?")
    test = (
        ("https://www.deviantart.com/?order=popular-all-time", {
            "options": (("original", False),),
            "range": "1-30",
            "count": 30,
        }),
        ("https://www.deviantart.com/popular-24-hours/?q=tree+house", {
            "options": (("original", False),),
        }),
        ("https://www.deviantart.com/search?q=tree"),
        ("https://www.deviantart.com/search/deviations?order=popular-1-week"),
        ("https://www.deviantart.com/artisan/popular-all-time/?q=tree"),
    )

    def __init__(self, match):
        DeviantartExtractor.__init__(self, match)
        self.search_term = self.time_range = self.category_path = None
        self.user = ""

        trange1, path, trange2, query = match.groups()
        trange = trange1 or trange2
        query = text.parse_query(query)

        if not trange:
            trange = query.get("order")

        if path:
            self.category_path = path.strip("/")
        if trange:
            trange = trange[8:] if trange.startswith("popular-") else ""
            self.time_range = trange.replace("-", "").replace("hours", "hr")
        if query:
            self.search_term = query.get("q")

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


class DeviantartExtractorV2(DeviantartExtractor):
    """Base class for deviantart extractors using the NAPI"""
    cookiedomain = ".deviantart.com"
    cookienames = ("auth", "auth_secure", "userinfo")
    _warning = True

    def items(self):
        if self.original and not self._check_cookies(self.cookienames):
            self.original = False
            if self._warning:
                DeviantartExtractorV2._warning = False
                self.log.warning("No session cookies set: "
                                 "Disabling original file downloads.")

        yield Message.Version, 1
        for deviation in self.deviations():
            data = self.api.deviation_extended_fetch(
                deviation["deviationId"],
                deviation["author"]["username"],
                "journal" if deviation["isJournal"] else "art",
            )

            if "deviation" not in data:
                self.log.warning("Unable to fetch deviation ID %s",
                                 deviation["deviationId"])
                self.log.debug("Server response: %s", data)
                continue

            deviation = self._extract(data)
            if not deviation:
                continue

            yield Message.Directory, deviation
            yield Message.Url, deviation["target"]["src"], deviation
            if self.extra:
                for match in DeviantartStashExtractor.pattern.finditer(
                        deviation["description"]):
                    deviation["_extractor"] = DeviantartStashExtractor
                    yield Message.Queue, match.group(0), deviation

    def _extract(self, data):
        deviation = data["deviation"]
        extended = deviation["extended"]
        media = deviation["media"]
        del deviation["extended"]
        del deviation["media"]

        # prepare deviation metadata
        deviation["description"] = extended.get("description", "")
        deviation["username"] = deviation["author"]["username"]
        deviation["_username"] = deviation["username"].lower()
        deviation["stats"] = extended["stats"]
        deviation["stats"]["comments"] = data["comments"]["total"]
        deviation["index"] = deviation["deviationId"]
        deviation["tags"] = [t["name"] for t in extended.get("tags") or ()]
        deviation["date"] = text.parse_datetime(
            deviation["publishedTime"])
        deviation["category_path"] = "/".join(
            extended[key]["displayNameEn"]
            for key in ("typeFacet", "contentFacet", "categoryFacet")
            if key in extended
        )

        # extract download target
        target = media["types"][-1]
        src = token = None

        if "textContent" in deviation:
            if not self.commit_journal:
                return None
            journal = deviation["textContent"]
            journal["html"] = journal["html"]["markup"]
            src = self.commit_journal(deviation, journal)[1]

        elif target["t"] == "gif":
            src = target["b"]
            token = media["token"][0]

        elif "download" in extended and self.original:
            target = extended["download"]
            src = target["url"]
            del target["url"]

        elif target["t"] == "video":
            # select largest video
            target = max(media["types"],
                         key=lambda x: text.parse_int(x.get("q", "")[:-1]))
            src = target["b"]

        elif target["t"] == "flash":
            src = target["s"]
            if src.startswith("https://sandbox.deviantart.com"):
                # extract SWF file from "sandbox"
                src = text.extract(
                    self.request(src).text, 'id="sandboxembed" src="', '"')[0]

        else:
            src = media["baseUri"]
            if "token" in media:
                token = media["token"][0]

            if "c" in target:
                src += "/" + target["c"].replace(
                    "<prettyName>", media["prettyName"])
            if src.startswith("https://images-wixmp-"):
                if deviation["index"] <= 790677560:
                    # https://github.com/r888888888/danbooru/issues/4069
                    intermediary, count = re.subn(
                        r"(/f/[^/]+/[^/]+)/v\d+/.*", r"/intermediary\1", src)
                    if count and self._check_url(intermediary):
                        src = intermediary
                if self.quality:
                    src = re.sub(r"q_\d+", self.quality, src)

        # filename and extension metadata
        alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
        sub = re.compile(r"\W").sub
        deviation["filename"] = "".join((
            sub("_", deviation["title"].lower()), "_by_",
            sub("_", deviation["author"]["username"].lower()), "-d",
            util.bencode(deviation["index"], alphabet),
        ))
        if "extension" not in deviation:
            deviation["extension"] = text.ext_from_url(src)

        if token:
            src = src + "?token=" + token
        target["src"] = src
        deviation["target"] = target
        return deviation

    def _pagination(self, url, params, headers=None):
        while True:
            data = self.request(url, params=params, headers=headers).json()
            yield from data["results"]

            if not data["hasMore"]:
                return
            params["offset"] = data["nextOffset"]


class DeviantartDeviationExtractor(DeviantartExtractorV2):
    """Extractor for single deviations"""
    subcategory = "deviation"
    archive_fmt = "{index}.{extension}"
    pattern = BASE_PATTERN + r"/(art|journal)/(?:[^/?&#]+-)?(\d+)"
    test = (
        (("https://www.deviantart.com/shimoda7/art/For-the-sake-10073852"), {
            "options": (("original", 0),),
            #  "content": "6a7c74dc823ebbd457bdd9b3c2838a6ee728091e",
        }),
        ("https://www.deviantart.com/zzz/art/zzz-1234567890", {
            "count": 0,
        }),
        (("https://www.deviantart.com/myria-moon/art/Aime-Moi-261986576"), {
            #  "pattern": (r"https://www.deviantart.com/download/261986576"
            #              r"/[\w-]+\.jpg\?token=\w+&ts=\d+"),
            "pattern": (r"https://images-wixmp-\w+\.wixmp\.com"
                        r"/intermediary/f/[^/]+/[^.]+\.jpg")
        }),
        # wixmp URL rewrite
        (("https://www.deviantart.com/citizenfresh/art/Hverarond-789295466"), {
            "pattern": (r"https://images-wixmp-\w+\.wixmp\.com"
                        r"/intermediary/f/[^/]+/[^.]+\.jpg")
        }),
        # wixmp URL rewrite v2 (#369)
        (("https://www.deviantart.com/josephbiwald/art/Destiny-2-804940104"), {
            "pattern": r"https://images-wixmp-\w+\.wixmp\.com/.*,q_100,"
        }),
        # non-download URL for GIFs (#242)
        (("https://www.deviantart.com/skatergators/art/COM-Moni-781571783"), {
            "pattern": (r"https://images-wixmp-\w+\.wixmp\.com"
                        r"/f/[^/]+/[^.]+\.gif\?token="),
        }),
        # external URLs from description (#302)
        (("https://www.deviantart.com/uotapo/art/INANAKI-Memo-590297498"), {
            "options": (("extra", 1), ("original", 0)),
            "pattern": r"https?://sta\.sh/\w+$",
            "range": "2-",
            "count": 4,
        }),
        # video
        ("https://www.deviantart.com/chi-u/art/-VIDEO-Brushes-330774593", {
            "pattern": r"https://wixmp-.+wixmp.com/v/mp4/.+\.720p\.\w+.mp4",
            "keyword": {
                "filename": r"re:_video____brushes_\w+_by_chi_u-d5gxnb5",
                "extension": "mp4",
                "target": {
                    "d": 306,
                    "f": 19367585,
                    "h": 720,
                    "q": "720p",
                    "t": "video",
                    "w": 1364,
                    "src": str,
                },
            }
        }),
        # archive
        ("https://www.deviantart.com/itsvenue/art/-brush-pngs-14-763300948", {
            #  "pattern": r"https://.+deviantart.com/download/763300948/.*rar",
            "pattern": r"https://images-wixmp-\w+\.wixmp\.com/i/.*\.png"
        }),
        # swf
        ("https://www.deviantart.com/ikatxfruti/art/Bang-Bang-528130222", {
            "pattern": r"https://images-wixmp-.*wixmp.com/f/.*\.swf",
        }),
        # journal
        ("https://www.deviantart.com/shimoda7/journal/ARTility-583755752", {
            "url": "f33f8127ab71819be7de849175b6d5f8b37bb629",
            "pattern": "text:<!DOCTYPE html>\n",
        }),
        # journal-like post with isJournal == False (#419)
        ("https://www.deviantart.com/gliitchlord/art/brashstrokes-812942668", {
            "url": "1534d6ea0561247ab921d07505e57a9d663a833b",
            "pattern": "text:<!DOCTYPE html>\n",
        }),
        # old-style URLs
        ("https://shimoda7.deviantart.com"
         "/art/For-the-sake-of-a-memory-10073852"),
        ("https://myria-moon.deviantart.com"
         "/art/Aime-Moi-part-en-vadrouille-261986576"),
        ("https://zzz.deviantart.com/art/zzz-1234567890"),
    )

    skip = Extractor.skip

    def __init__(self, match):
        DeviantartExtractorV2.__init__(self, match)
        self.type = match.group(3)
        self.deviation_id = match.group(4)

    def deviations(self):
        return ({
            "deviationId": self.deviation_id,
            "author"     : {"username": self.user},
            "isJournal"  : self.type == "journal",
        },)


class DeviantartScrapsExtractor(DeviantartExtractorV2):
    """Extractor for an artist's scraps"""
    subcategory = "scraps"
    directory_fmt = ("{category}", "{username}", "Scraps")
    archive_fmt = "s_{_username}_{index}.{extension}"
    pattern = BASE_PATTERN + r"/gallery/(?:\?catpath=)?scraps\b"
    test = (
        ("https://www.deviantart.com/shimoda7/gallery/scraps", {
            "count": 12,
        }),
        ("https://www.deviantart.com/shimoda7/gallery/?catpath=scraps"),
        ("https://shimoda7.deviantart.com/gallery/?catpath=scraps"),
    )

    def deviations(self):
        url = self.root + "/_napi/da-user-profile/api/gallery/contents"
        params = {
            "username"     : self.user,
            "offset"       : self.offset,
            "limit"        : "24",
            "scraps_folder": "true",
        }
        headers = {
            "Referer": "{}/{}/gallery/scraps".format(self.root, self.user),
        }

        for obj in self._pagination(url, params, headers):
            yield obj["deviation"]


class DeviantartFollowingExtractor(DeviantartExtractorV2):
    subcategory = "following"
    pattern = BASE_PATTERN + "/about#watching$"
    test = ("https://www.deviantart.com/shimoda7/about#watching", {
        "pattern": DeviantartUserExtractor.pattern,
        "range": "1-50",
        "count": 50,
    })

    def items(self):
        url = "{}/_napi/da-user-profile/api/module/watching".format(self.root)
        params = {
            "username": self.user,
            "moduleid": self._module_id(self.user),
            "offset"  : "0",
            "limit"   : "24",
        }

        yield Message.Version, 1
        for user in self._pagination(url, params):
            url = "{}/{}".format(self.root, user["username"])
            yield Message.Queue, url, user

    def _module_id(self, username):
        url = "{}/{}/about".format(self.root, username)
        page = self.request(url).text
        pos = page.find('\\"type\\":\\"watching\\"')
        if pos < 0:
            raise exception.NotFoundError("module")
        return text.rextract(page, '\\"id\\":', ',', pos)[0].strip('" ')


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

        self.folders = extractor.config("folders", False)
        self.metadata = extractor.extra or extractor.config("metadata", False)

        self.client_id = extractor.config(
            "client-id", self.CLIENT_ID)
        self.client_secret = extractor.config(
            "client-secret", self.CLIENT_SECRET)

        self.refresh_token = extractor.config("refresh-token")
        if self.refresh_token == "cache":
            self.refresh_token = "#" + str(self.client_id)

        self.log.debug(
            "Using %s API credentials (client-id %s)",
            "default" if self.client_id == self.CLIENT_ID else "custom",
            self.client_id,
        )

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
        return self._pagination_folders(endpoint, params)

    def deviation(self, deviation_id):
        """Query and return info about a single Deviation"""
        endpoint = "deviation/" + deviation_id
        deviation = self._call(endpoint)
        if self.metadata:
            self._metadata((deviation,))
        if self.folders:
            self._folders((deviation,))
        return deviation

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

    def deviation_extended_fetch(self, deviation_id, user, kind):
        url = ("https://www.deviantart.com/_napi/da-browse/shared_api"
               "/deviation/extended_fetch")
        headers = {"Referer": "https://www.deviantart.com/"}
        params = {
            "deviationid"    : deviation_id,
            "username"       : user,
            "type"           : kind,
            "include_session": "false",
        }
        response = self.extractor.request(
            url, headers=headers, params=params, fatal=None)
        code = response.status_code

        if code == 404:
            raise exception.StopExtraction(
                "Your account must use the Eclipse interface.")
        elif code == 403 and b"Request blocked." in response.content:
            raise exception.StopExtraction(
                "Requests to deviantart.com blocked due to too much traffic.")
        try:
            return response.json()
        except Exception:
            return {"error": response.text}

    def deviation_metadata(self, deviations):
        """ Fetch deviation metadata for a set of deviations"""
        if not deviations:
            return []
        endpoint = "deviation/metadata?" + "&".join(
            "deviationids[{}]={}".format(num, deviation["deviationid"])
            for num, deviation in enumerate(deviations)
        )
        params = {"mature_content": self.mature}
        return self._call(endpoint, params)["metadata"]

    def gallery(self, username, folder_id="", offset=0, extend=True):
        """Yield all Deviation-objects contained in a gallery folder"""
        endpoint = "gallery/" + folder_id
        params = {"username": username, "offset": offset, "limit": 24,
                  "mature_content": self.mature, "mode": "newest"}
        return self._pagination(endpoint, params, extend)

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
        return self._pagination_folders(endpoint, params)

    @memcache(keyarg=1)
    def user_profile(self, username):
        """Get user profile information"""
        endpoint = "user/profile/" + username
        return self._call(endpoint, fatal=False)

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
            url, method="POST", data=data, auth=auth, fatal=False)
        data = response.json()

        if response.status_code != 200:
            self.log.debug("Server response: %s", data)
            raise exception.AuthenticationError('"{}" ({})'.format(
                data.get("error_description"), data.get("error")))
        if refresh_token:
            _refresh_token_cache.update(refresh_token, data["refresh_token"])
        return "Bearer " + data["access_token"]

    def _call(self, endpoint, params=None, fatal=True, public=True):
        """Call an API endpoint"""
        url = "https://www.deviantart.com/api/v1/oauth2/" + endpoint
        while True:
            if self.delay >= 0:
                time.sleep(2 ** self.delay)

            self.authenticate(None if public else self.refresh_token)
            response = self.extractor.request(
                url, headers=self.headers, params=params, fatal=None)
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
                self.delay += 1
                self.log.warning("%s. Using %ds delay.", msg, 2 ** self.delay)
            else:
                self.log.error(msg)
                return data

    def _pagination(self, endpoint, params, extend=True):
        public = warn = True
        while True:
            data = self._call(endpoint, params, public=public)
            if "results" not in data:
                self.log.error("Unexpected API response: %s", data)
                return

            if extend:
                if public and len(data["results"]) < params["limit"]:
                    if self.refresh_token:
                        self.log.debug("Switching to private access token")
                        public = False
                        continue
                    elif data["has_more"] and warn:
                        warn = False
                        self.log.warning(
                            "Private deviations detected! Run 'gallery-dl "
                            "oauth:deviantart' and follow the instructions to "
                            "be able to access them.")
                if self.metadata:
                    self._metadata(data["results"])
                if self.folders:
                    self._folders(data["results"])
            yield from data["results"]

            if not data["has_more"]:
                return
            params["offset"] = data["next_offset"]

    def _pagination_folders(self, endpoint, params):
        result = []
        result.extend(self._pagination(endpoint, params, False))
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

        # add parent names to folders, but ignore "Featured" as parent
        fmap = {}
        featured = folders[0]["folderid"]
        for folder in folders:
            if folder["parent"] and folder["parent"] != featured:
                folder["name"] = fmap[folder["parent"]] + "/" + folder["name"]
            fmap[folder["folderid"]] = folder["name"]

        # map deviationids to folder names
        dmap = collections.defaultdict(list)
        for folder in folders:
            for deviation in self.gallery(
                    username, folder["folderid"], 0, False):
                dmap[deviation["deviationid"]].append(folder["name"])
        return dmap


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
