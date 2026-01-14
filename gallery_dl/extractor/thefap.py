# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://thefap.net/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?thefap\.net"


class ThefapExtractor(Extractor):
    """Base class for thefap extractors"""
    category = "thefap"
    root = "https://thefap.net"
    directory_fmt = ("{category}", "{model_name} ({model_id})")
    filename_fmt = "{model}_{num:>03}.{extension}"
    archive_fmt = "{model_id}_{filename}"

    def _normalize_url(self, url):
        if not url:
            return ""
        url = url.strip()
        if "?w=" in url:
            url = url[:url.rfind("?")]
        elif url.endswith(":small"):
            url = url[:-6] + ":orig"
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = self.root + url
        return url


class ThefapPostExtractor(ThefapExtractor):
    """Extractor for individual thefap.net posts"""
    subcategory = "post"
    pattern = (BASE_PATTERN +
               r"(/([^/?#]+)-(\d+)/([^/?#]+)/i(\d+))")
    example = "https://thefap.net/MODEL-12345/KIND/i12345"

    def items(self):
        path, model, model_id, kind, post_id = self.groups

        page = self.request(self.root + path).text
        if "Not Found" in page:
            raise exception.NotFoundError("post")

        if model_name := text.extr(page, "<title>", " / "):
            model_name = text.unescape(model_name)
        else:
            model_name = text.unquote(model).replace(".", " ")

        data = {
            "model"     : model,
            "model_id"  : text.parse_int(model_id),
            "model_name": model_name,
            "kind"      : kind,
            "post_id"   : text.parse_int(post_id),
            "_http_headers": {"Referer": None},
        }
        yield Message.Directory, "", data

        data["num"] = 0
        page = text.extract(
            page, "\n</div>", "\n<!---->", page.index("</header>"))[0]
        for url in text.extract_iter(page, '<img src="', '"'):
            if url := self._normalize_url(url):
                data["num"] += 1
                yield Message.Url, url, text.nameext_from_url(url, data)


class ThefapModelExtractor(ThefapExtractor):
    """Extractor for thefap.net model pages"""
    subcategory = "model"
    pattern = BASE_PATTERN + r"/([^/?#]+)-(\d+)"
    example = "https://thefap.net/MODEL-12345/"

    def items(self):
        model, model_id = self.groups

        url = f"{self.root}/{model}-{model_id}/"
        page = self.request(url).text

        if 'id="content"' not in page:
            raise exception.NotFoundError("model")

        if model_name := text.extr(page, "<h2", "</h2>"):
            model_name = text.unescape(model_name[model_name.find(">")+1:])
        else:
            model_name = text.unquote(model).replace(".", " ")

        data = {
            "model"     : model,
            "model_id"  : text.parse_int(model_id),
            "model_name": model_name,
            "_http_headers": {"Referer": None},
        }
        yield Message.Directory, "", data

        base = f"{self.root}/ajax/model/{model_id}/page-"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest"  : "empty",
            "Sec-Fetch-Mode"  : "cors",
            "Sec-Fetch-Site"  : "same-origin",
        }

        page = text.extr(page, '<div id="content"', '<div id="showmore"')
        imgs = text.extract_iter(page, 'data-src="', '"')
        pnum = 1
        data["num"] = 0

        while True:
            for url in imgs:
                if url := self._normalize_url(url):
                    data["num"] += 1
                    yield Message.Url, url, text.nameext_from_url(url, data)

            pnum += 1
            page = self.request(base + str(pnum), headers=headers).text
            if not page:
                break
            imgs = text.extract_iter(page, '<img src="', '"')
