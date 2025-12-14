# -*- coding: utf-8 -*-

# Copyright 2022-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bunkr.si/"""

from .common import Extractor
from .lolisafe import LolisafeAlbumExtractor
from .. import text, util, config, exception
from ..cache import memcache
import random

if config.get(("extractor", "bunkr"), "tlds"):
    BASE_PATTERN = (
        r"(?:bunkr:(?:https?://)?([^/?#]+)|"
        r"(?:https?://)?(?:app\.)?(bunkr+\.\w+))"
    )
else:
    BASE_PATTERN = (
        r"(?:bunkr:(?:https?://)?([^/?#]+)|"
        r"(?:https?://)?(?:app\.)?(bunkr+"
        r"\.(?:s[kiu]|c[ir]|fi|p[hks]|ru|la|is|to|a[cx]"
        r"|black|cat|media|red|site|ws|org)))"
    )

DOMAINS = [
    "bunkr.ac",
    "bunkr.ci",
    "bunkr.cr",
    "bunkr.fi",
    "bunkr.ph",
    "bunkr.pk",
    "bunkr.ps",
    "bunkr.si",
    "bunkr.sk",
    "bunkr.ws",
    "bunkr.black",
    "bunkr.red",
    "bunkr.media",
    "bunkr.site",
]
LEGACY_DOMAINS = {
    "bunkr.ax",
    "bunkr.cat",
    "bunkr.ru",
    "bunkrr.ru",
    "bunkr.su",
    "bunkrr.su",
    "bunkr.la",
    "bunkr.is",
    "bunkr.to",
}
CF_DOMAINS = set()


class BunkrAlbumExtractor(LolisafeAlbumExtractor):
    """Extractor for bunkr.si albums"""
    category = "bunkr"
    root = "https://bunkr.si"
    root_dl = "https://get.bunkrr.su"
    root_api = "https://apidl.bunkr.ru"
    archive_fmt = "{album_id}_{id|id_url|slug}"
    pattern = rf"{BASE_PATTERN}/a/([^/?#]+)"
    example = "https://bunkr.si/a/ID"

    def __init__(self, match):
        LolisafeAlbumExtractor.__init__(self, match)
        domain = self.groups[0] or self.groups[1]
        if domain not in LEGACY_DOMAINS:
            self.root = "https://" + domain

    def _init(self):
        LolisafeAlbumExtractor._init(self)

        endpoint = self.config("endpoint")
        if not endpoint:
            endpoint = self.root_api + "/api/_001_v2"
        elif endpoint[0] == "/":
            endpoint = self.root_api + endpoint

        self.endpoint = endpoint
        self.offset = 0

    def skip(self, num):
        self.offset = num
        return num

    def request(self, url, **kwargs):
        kwargs["encoding"] = "utf-8"
        kwargs["allow_redirects"] = False

        while True:
            try:
                response = Extractor.request(self, url, **kwargs)
                if response.status_code < 300:
                    return response

                # redirect
                url = response.headers["Location"]
                if url[0] == "/":
                    url = self.root + url
                    continue
                root, path = self._split(url)
                if root not in CF_DOMAINS:
                    continue
                self.log.debug("Redirect to known CF challenge domain '%s'",
                               root)

            except exception.HttpError as exc:
                if exc.status != 403:
                    raise

                # CF challenge
                root, path = self._split(url)
                CF_DOMAINS.add(root)
                self.log.debug("Added '%s' to CF challenge domains", root)

                try:
                    DOMAINS.remove(root.rpartition("/")[2])
                except ValueError:
                    pass
                else:
                    if not DOMAINS:
                        raise exception.AbortExtraction(
                            "All Bunkr domains require solving a CF challenge")

            # select alternative domain
            self.root = root = "https://" + random.choice(DOMAINS)
            self.log.debug("Trying '%s' as fallback", root)
            url = root + path

    def fetch_album(self, album_id):
        # album metadata
        page = self.request(f"{self.root}/a/{album_id}?advanced=1").text
        title = text.unescape(text.unescape(text.extr(
            page, 'property="og:title" content="', '"')))

        # files
        items = text.extr(
            page, "window.albumFiles = [", "</script>").split("\n},\n")

        return self._extract_files(items), {
            "album_id"   : album_id,
            "album_name" : title,
            "album_size" : text.extr(
                page, '<span class="font-semibold">(', ')'),
            "count"      : len(items),
        }

    def _extract_files(self, items):
        if self.offset:
            items = util.advance(items, self.offset)

        for item in items:
            try:
                data_id = text.extr(item, " id: ", ",").strip()
                file = self._extract_file(data_id)

                file["name"] = util.json_loads(text.extr(
                    item, 'original:', ',\n').replace("\\'", "'"))
                file["slug"] = util.json_loads(text.extr(
                    item, 'slug: ', ',\n').replace("\\'", "'"))
                file["uuid"] = text.extr(
                    item, 'name: "', ".")
                file["size"] = text.parse_int(text.extr(
                    item, "size:  ", " ,\n"))
                file["date"] = self.parse_datetime(text.extr(
                    item, 'timestamp: "', '"'), "%H:%M:%S %d/%m/%Y")

                yield file
            except exception.ControlException:
                raise
            except Exception as exc:
                self.log.error("%s: %s", exc.__class__.__name__, exc)
                self.log.debug("%s", item, exc_info=exc)
                if isinstance(exc, exception.HttpError) and \
                        exc.status == 400 and \
                        exc.response.url.startswith(self.root_api):
                    raise exception.AbortExtraction("Album deleted")

    def _extract_file(self, data_id):
        referer = f"{self.root_dl}/file/{data_id}"
        headers = {"Referer": referer, "Origin": self.root_dl}
        data = self.request_json(self.endpoint, method="POST", headers=headers,
                                 json={"id": data_id})

        if data.get("encrypted"):
            key = f"SECRET_KEY_{data['timestamp'] // 3600}"
            file_url = util.decrypt_xor(data["url"], key.encode())
        else:
            file_url = data["url"]

        return {
            "file"          : file_url,
            "id_url"        : data_id,
            "_http_headers" : {"Referer": referer},
            "_http_validate": self._validate,
        }

    def _validate(self, response):
        if response.history and response.url.endswith("/maintenance-vid.mp4"):
            self.log.warning("File server in maintenance mode")
            return False
        return True

    def _split(self, url):
        pos = url.index("/", 8)
        return url[:pos], url[pos:]


class BunkrMediaExtractor(BunkrAlbumExtractor):
    """Extractor for bunkr.si media links"""
    subcategory = "media"
    directory_fmt = ("{category}",)
    pattern = rf"{BASE_PATTERN}(/[fvid]/[^/?#]+)"
    example = "https://bunkr.si/f/FILENAME"

    def fetch_album(self, album_id):
        try:
            page = self.request(f"{self.root}{album_id}").text
            data_id = text.extr(page, 'data-file-id="', '"')
            file = self._extract_file(data_id)
            file["name"] = text.unquote(text.unescape(text.extr(
                page, "<h1", "<").rpartition(">")[2]))
            file["slug"] = album_id.rpartition("/")[2]
            file["uuid"] = text.extr(page, "/thumbs/", ".")
        except Exception as exc:
            self.log.error("%s: %s", exc.__class__.__name__, exc)
            return (), {}

        album_id, album_name, album_size = self._album_info(text.extr(
            page, ' href="../a/', '"'))
        return (file,), {
            "album_id"  : album_id,
            "album_name": album_name,
            "album_size": album_size,
            "count"     : 1,
        }

    @memcache(keyarg=1)
    def _album_info(self, album_id):
        if album_id:
            try:
                page = self.request(f"{self.root}/a/{album_id}").text
                return (
                    album_id,
                    text.unescape(text.unescape(text.extr(
                        page, 'property="og:title" content="', '"'))),
                    text.extr(page, '<span class="font-semibold">(', ')'),
                )
            except Exception:
                pass
        return album_id, "", -1
