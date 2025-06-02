# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://xfolio.jp/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?xfolio\.jp(?:/[^/?#]+)?"


class XfolioExtractor(Extractor):
    """Base class for xfolio extractors"""
    category = "xfolio"
    root = "https://xfolio.jp"
    cookies_domain = ".xfolio.jp"
    directory_fmt = ("{category}", "{creator_slug}", "{work_id}")
    filename_fmt = "{work_id}_{image_id}.{extension}"
    archive_fmt = "{work_id}_{image_id}"
    request_interval = (0.5, 1.5)

    def _init(self):
        XfolioExtractor._init = Extractor._init
        if not self.cookies_check(("xfolio_session",)):
            self.log.error("'xfolio_session' cookie required")

    def items(self):
        data = {"_extractor": XfolioWorkExtractor}
        for work in self.works():
            yield Message.Queue, work, data

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)

        if "/system/recaptcha" in response.url:
            raise exception.StopExtraction("Bot check / CAPTCHA page")

        return response


class XfolioWorkExtractor(XfolioExtractor):
    subcategory = "work"
    pattern = BASE_PATTERN + r"/portfolio/([^/?#]+)/works/(\d+)"
    example = "https://xfolio.jp/portfolio/USER/works/12345"
    ref_fmt = ("{}/fullscale_image?image_id={}&work_id={}")
    url_fmt = ("{}/user_asset.php?id={}&work_id={}"
               "&work_image_id={}&type=work_image")

    def items(self):
        creator, work_id = self.groups
        url = "{}/portfolio/{}/works/{}".format(self.root, creator, work_id)
        html = self.request(url).text

        work = self._extract_data(html)
        files = self._extract_files(html, work)
        work["count"] = len(files)

        yield Message.Directory, work
        for work["num"], file in enumerate(files, 1):
            file.update(work)
            yield Message.Url, file["url"], file

    def _extract_data(self, html):
        creator, work_id = self.groups
        extr = text.extract_from(html)
        return {
            "title"          : text.unescape(extr(
                'property="og:title" content="', '"').rpartition(" - ")[0]),
            "description"    : text.unescape(extr(
                'property="og:description" content="', '"')),
            "creator_id"     : extr(' data-creator-id="', '"'),
            "creator_userid" : extr(' data-creator-user-id="', '"'),
            "creator_name"   : extr(' data-creator-name="', '"'),
            "creator_profile": text.unescape(extr(
                ' data-creator-profile="', '"')),
            "series_id"      : extr("/series/", '"'),
            "creator_slug"   : creator,
            "work_id"        : work_id,
        }

    def _extract_files(self, html, work):
        files = []

        work_id = work["work_id"]
        for img in text.extract_iter(
                html, 'class="article__wrap_img', "</div>"):
            image_id = text.extr(img, "/fullscale_image?image_id=", "&")
            if not image_id:
                self.log.warning(
                    "%s: 'fullscale_image' not available", work_id)
                continue

            files.append({
                "image_id" : image_id,
                "extension": "jpg",
                "url": self.url_fmt.format(
                    self.root, image_id, work_id, image_id),
                "_http_headers": {"Referer": self.ref_fmt.format(
                    self.root, image_id, work_id)},
            })

        return files


class XfolioUserExtractor(XfolioExtractor):
    subcategory = "user"
    pattern = BASE_PATTERN + r"/portfolio/([^/?#]+)(?:/works)?/?(?:$|\?|#)"
    example = "https://xfolio.jp/portfolio/USER"

    def works(self):
        url = "{}/portfolio/{}/works".format(self.root, self.groups[0])

        while True:
            html = self.request(url).text

            for item in text.extract_iter(
                    html, '<div class="postItem', "</div>"):
                yield text.extr(item, ' href="', '"')

            pager = text.extr(html, ' class="pager__list_next', "</li>")
            url = text.extr(pager, ' href="', '"')
            if not url:
                return
            url = text.unescape(url)


class XfolioSeriesExtractor(XfolioExtractor):
    subcategory = "series"
    pattern = BASE_PATTERN + r"/portfolio/([^/?#]+)/series/(\d+)"
    example = "https://xfolio.jp/portfolio/USER/series/12345"

    def works(self):
        creator, series_id = self.groups
        url = "{}/portfolio/{}/series/{}".format(self.root, creator, series_id)
        html = self.request(url).text

        return [
            text.extr(item, ' href="', '"')
            for item in text.extract_iter(
                html, 'class="listWrap--title">', "</a>")
        ]
