# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://ci-en.net/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?ci-en\.(?:net|dlsite\.com)"


class CienExtractor(Extractor):
    category = "cien"
    root = "https://ci-en.net"
    request_interval = (1.0, 2.0)

    def __init__(self, match):
        self.root = text.root_from_url(match.group(0))
        Extractor.__init__(self, match)

    def _init(self):
        self.cookies.set("accepted_rating", "r18g", domain="ci-en.dlsite.com")

    def _pagination_articles(self, url, params):
        data = {"_extractor": CienArticleExtractor}
        params["page"] = text.parse_int(params.get("page"), 1)

        while True:
            page = self.request(url, params=params).text

            for card in text.extract_iter(
                    page, ' class="c-cardCase-item', '</div>'):
                article_url = text.extr(card, ' href="', '"')
                yield Message.Queue, article_url, data

            if ' rel="next"' not in page:
                return
            params["page"] += 1


class CienArticleExtractor(CienExtractor):
    subcategory = "article"
    filename_fmt = "{num:>02} {filename}.{extension}"
    directory_fmt = ("{category}", "{author[name]}", "{post_id} {name}")
    archive_fmt = "{post_id}_{num}"
    pattern = BASE_PATTERN + r"/creator/(\d+)/article/(\d+)"
    example = "https://ci-en.net/creator/123/article/12345"

    def items(self):
        url = "{}/creator/{}/article/{}".format(
            self.root, self.groups[0], self.groups[1])
        page = self.request(url, notfound="article").text

        files = self._extract_files(page)
        post = self._extract_jsonld(page)[0]
        post["post_url"] = url
        post["post_id"] = text.parse_int(self.groups[1])
        post["count"] = len(files)
        post["date"] = text.parse_datetime(post["datePublished"])

        try:
            del post["publisher"]
            del post["sameAs"]
        except Exception:
            pass

        yield Message.Directory, post
        for post["num"], file in enumerate(files, 1):
            post.update(file)
            if "extension" not in file:
                text.nameext_from_url(file["url"], post)
            yield Message.Url, file["url"], post

    def _extract_files(self, page):
        files = []

        filetypes = self.config("files")
        if filetypes is None:
            self._extract_files_image(page, files)
            self._extract_files_video(page, files)
            self._extract_files_download(page, files)
            self._extract_files_gallery(page, files)
        else:
            generators = {
                "image"   : self._extract_files_image,
                "video"   : self._extract_files_video,
                "download": self._extract_files_download,
                "gallery" : self._extract_files_gallery,
                "gallerie": self._extract_files_gallery,
            }
            if isinstance(filetypes, str):
                filetypes = filetypes.split(",")
            for ft in filetypes:
                generators[ft.rstrip("s")](page, files)

        return files

    def _extract_files_image(self, page, files):
        for image in text.extract_iter(
                page, 'class="file-player-image"', "</figure>"):
            size = text.extr(image, ' data-size="', '"')
            w, _, h = size.partition("x")

            files.append({
                "url"   : text.extr(image, ' data-raw="', '"'),
                "width" : text.parse_int(w),
                "height": text.parse_int(h),
                "type"  : "image",
            })

    def _extract_files_video(self, page, files):
        for video in text.extract_iter(
                page, "<vue-file-player", "</vue-file-player>"):
            path = text.extr(video, ' base-path="', '"')
            name = text.extr(video, ' file-name="', '"')
            auth = text.extr(video, ' auth-key="', '"')

            file = text.nameext_from_url(name)
            file["url"] = "{}video-web.mp4?{}".format(path, auth)
            file["type"] = "video"
            files.append(file)

    def _extract_files_download(self, page, files):
        for download in text.extract_iter(
                page, 'class="downloadBlock', "</div>"):
            name = text.extr(download, "<p>", "<")

            file = text.nameext_from_url(name.rpartition(" ")[0])
            file["url"] = text.extr(download, ' href="', '"')
            file["type"] = "download"
            files.append(file)

    def _extract_files_gallery(self, page, files):
        for gallery in text.extract_iter(
                page, "<vue-image-gallery", "</vue-image-gallery>"):

            url = self.root + "/api/creator/gallery/images"
            params = {
                "hash"      : text.extr(gallery, ' hash="', '"'),
                "gallery_id": text.extr(gallery, ' gallery-id="', '"'),
                "time"      : text.extr(gallery, ' time="', '"'),
            }
            data = self.request(url, params=params).json()
            url = self.root + "/api/creator/gallery/imagePath"

            for params["page"], params["file_id"] in enumerate(
                    data["imgList"]):
                path = self.request(url, params=params).json()["path"]

                file = params.copy()
                file["url"] = path
                files.append(file)


class CienCreatorExtractor(CienExtractor):
    subcategory = "creator"
    pattern = BASE_PATTERN + r"/creator/(\d+)(?:/article(?:\?([^#]+))?)?/?$"
    example = "https://ci-en.net/creator/123"

    def items(self):
        url = "{}/creator/{}/article".format(self.root, self.groups[0])
        params = text.parse_query(self.groups[1])
        params["mode"] = "list"
        return self._pagination_articles(url, params)


class CienRecentExtractor(CienExtractor):
    subcategory = "recent"
    pattern = BASE_PATTERN + r"/mypage/recent(?:\?([^#]+))?"
    example = "https://ci-en.net/mypage/recent"

    def items(self):
        url = self.root + "/mypage/recent"
        params = text.parse_query(self.groups[0])
        return self._pagination_articles(url, params)


class CienFollowingExtractor(CienExtractor):
    subcategory = "following"
    pattern = BASE_PATTERN + r"/mypage/subscription(/following)?"
    example = "https://ci-en.net/mypage/subscription"

    def items(self):
        url = self.root + "/mypage/subscription" + (self.groups[0] or "")
        page = self.request(url).text
        data = {"_extractor": CienCreatorExtractor}

        for subscription in text.extract_iter(
                page, 'class="c-grid-subscriptionInfo', '</figure>'):
            url = text.extr(subscription, ' href="', '"')
            yield Message.Queue, url, data
