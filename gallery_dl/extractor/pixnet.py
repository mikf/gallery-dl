# -*- coding: utf-8 -*-

# Copyright 2016-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.pixnet.net/"""

from .common import Extractor, Message
from .. import text, exception


BASE_PATTERN = r"(?:https?://)?(?!www\.)([^.]+)\.pixnet.net"


class PixnetExtractor(Extractor):
    """Base class for pixnet extractors"""
    category = "pixnet"
    filename_fmt = "{num:>03}_{id}.{extension}"
    archive_fmt = "{id}"
    url_fmt = ""

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.blog, self.item_id = match.groups()
        self.root = "https://{}.pixnet.net".format(self.blog)

    def items(self):
        url = self.url_fmt.format(self.root, self.item_id)
        page = self.request(url, encoding="utf-8").text
        user = text.extract(page, '<meta name="author" content="', '";')[0]
        data = {
            "blog": self.blog,
            "user": user.rpartition(" (")[0],
        }

        for info in self._pagination(page):
            url, pos = text.extract(info, ' href="', '"')
            alt, pos = text.extract(info, ' alt="', '"', pos)
            item = {
                "id"        : text.parse_int(url.rpartition("/")[2]),
                "title"     : text.unescape(alt),
                "_extractor": (PixnetFolderExtractor if "/folder/" in url else
                               PixnetSetExtractor),
            }
            item.update(data)
            yield Message.Queue, url, item

    def _pagination(self, page):
        while True:
            yield from text.extract_iter(page, '<li id="', '</li>')

            pnext = text.extract(page, 'class="nextBtn"', '>')[0]
            if pnext is None and 'name="albumpass">' in page:
                raise exception.StopExtraction(
                    "Album %s is password-protected.", self.item_id)
            if "href" not in pnext:
                return
            url = self.root + text.extract(pnext, 'href="', '"')[0]
            page = self.request(url, encoding="utf-8").text


class PixnetImageExtractor(PixnetExtractor):
    """Extractor for a single photo from pixnet.net"""
    subcategory = "image"
    filename_fmt = "{id}.{extension}"
    directory_fmt = ("{category}", "{blog}")
    pattern = BASE_PATTERN + r"/album/photo/(\d+)"
    test = ("https://albertayu773.pixnet.net/album/photo/159443828", {
        "url": "156564c422138914c9fa5b42191677b45c414af4",
        "keyword": "19971bcd056dfef5593f4328a723a9602be0f087",
        "content": "0e097bdf49e76dd9b9d57a016b08b16fa6a33280",
    })

    def items(self):
        url = "https://api.pixnet.cc/oembed"
        params = {
            "url": "https://{}.pixnet.net/album/photo/{}".format(
                self.blog, self.item_id),
            "format": "json",
        }

        data = self.request(url, params=params).json()
        data["id"] = text.parse_int(
            data["url"].rpartition("/")[2].partition("-")[0])
        data["filename"], _, data["extension"] = data["title"].rpartition(".")
        data["blog"] = self.blog
        data["user"] = data.pop("author_name")

        yield Message.Directory, data
        yield Message.Url, data["url"], data


class PixnetSetExtractor(PixnetExtractor):
    """Extractor for images from a pixnet set"""
    subcategory = "set"
    url_fmt = "{}/album/set/{}"
    directory_fmt = ("{category}", "{blog}",
                     "{folder_id} {folder_title}", "{set_id} {set_title}")
    pattern = BASE_PATTERN + r"/album/set/(\d+)"
    test = (
        ("https://albertayu773.pixnet.net/album/set/15078995", {
            "url": "6535712801af47af51110542f4938a7cef44557f",
            "keyword": "bf25d59e5b0959cb1f53e7fd2e2a25f2f67e5925",
        }),
        ("https://anrine910070.pixnet.net/album/set/5917493", {
            "url": "b3eb6431aea0bcf5003432a4a0f3a3232084fc13",
            "keyword": "bf7004faa1cea18cf9bd856f0955a69be51b1ec6",
        }),
        ("https://sky92100.pixnet.net/album/set/17492544", {
            "count": 0,  # password-protected
        }),
    )

    def items(self):
        url = self.url_fmt.format(self.root, self.item_id)
        page = self.request(url, encoding="utf-8").text
        data = self.metadata(page)

        yield Message.Directory, data
        for num, info in enumerate(self._pagination(page), 1):
            url, pos = text.extract(info, ' href="', '"')
            src, pos = text.extract(info, ' src="', '"', pos)
            alt, pos = text.extract(info, ' alt="', '"', pos)

            photo = {
                "id": text.parse_int(url.rpartition("/")[2].partition("#")[0]),
                "url": src.replace("_s.", "."),
                "num": num,
                "filename": alt,
                "extension": src.rpartition(".")[2],
            }
            photo.update(data)
            yield Message.Url, photo["url"], photo

    def metadata(self, page):
        user , pos = text.extract(page, '<meta name="author" content="', '";')
        _    , pos = text.extract(page, 'id="breadcrumb"', '', pos)
        fid  , pos = text.extract(page, '/folder/', '"', pos)
        fname, pos = text.extract(page, '>', '<', pos)
        sid  , pos = text.extract(page, '/set/', '"', pos)
        sname, pos = text.extract(page, '>', '<', pos)
        return {
            "blog": self.blog,
            "user": user.rpartition(" (")[0],
            "folder_id"   : text.parse_int(fid, ""),
            "folder_title": text.unescape(fname).strip(),
            "set_id"      : text.parse_int(sid),
            "set_title"   : text.unescape(sname),
        }


class PixnetFolderExtractor(PixnetExtractor):
    """Extractor for all sets in a pixnet folder"""
    subcategory = "folder"
    url_fmt = "{}/album/folder/{}"
    pattern = BASE_PATTERN + r"/album/folder/(\d+)"
    test = ("https://albertayu773.pixnet.net/album/folder/1405768", {
        "pattern": PixnetSetExtractor.pattern,
        "count": ">= 15",
    })


class PixnetUserExtractor(PixnetExtractor):
    """Extractor for all sets and folders of a pixnet user"""
    subcategory = "user"
    url_fmt = "{}{}/album/list"
    pattern = BASE_PATTERN + r"()(?:/blog|/album(?:/list)?)?/?(?:$|[?#])"
    test = (
        ("https://albertayu773.pixnet.net/"),
        ("https://albertayu773.pixnet.net/blog"),
        ("https://albertayu773.pixnet.net/album"),
        ("https://albertayu773.pixnet.net/album/list", {
            "pattern": PixnetFolderExtractor.pattern,
            "count": ">= 30",
        }),
        ("https://anrine910070.pixnet.net/album/list", {
            "pattern": PixnetSetExtractor.pattern,
            "count": ">= 14",
        }),
    )
