# -*- coding: utf-8 -*-

# Copyright 2026 gallery-dl contributors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bodytorium.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?bodytorium\.com"
MEDIA_STORAGE = "bodytorium.ams3.digitaloceanspaces.com"


class BodytoriumExtractor(Extractor):
    """Base class for Bodytorium extractors"""
    category = "bodytorium"
    root = "https://bodytorium.com"
    cookies_domain = ".bodytorium.com"
    cookies_names = ("wordpress_logged_in", "wordpress_sec")
    directory_fmt = ("{category}", "{model_id}", "{album_id|video_id}")
    archive_fmt = "_{model_id}_{id}_{num:>03}_{filename}_{offset}"


class BodytoriumModelPageExtractor(BodytoriumExtractor):
    """Extractor for model pages"""
    subcategory = "model-page"
    pattern = BASE_PATTERN + r"/model/(mx?\d+)/?(?:$|[?#])"
    example = "https://bodytorium.com/model/m069/"

    def __init__(self, match):
        BodytoriumExtractor.__init__(self, match)
        self.model_id = match.group(1)

    def items(self):
        url = "{}/model/{}/".format(self.root, self.model_id)
        page = self.request(url).text

        model_name = text.extr(page, "<h1>", "</h1>")
        if model_name:
            model_name = model_name.strip()

        for album_id in text.extract_iter(
                page, 'href="{}/album/'.format(self.root), '"'):
            album_id = album_id.split("/")[0]
            yield Message.Queue, "{}/album/{}/".format(
                self.root, album_id), {
                "_extractor": BodytoriumAlbumExtractor,
                "model_id"  : self.model_id,
                "model_name": model_name,
                "album_id"  : album_id,
            }

        for video_id in text.extract_iter(
                page, 'href="{}/video/'.format(self.root), '"'):
            video_id = video_id.split("/")[0]
            yield Message.Queue, "{}/video/{}/".format(
                self.root, video_id), {
                "_extractor": BodytoriumVideoExtractor,
                "model_id"  : self.model_id,
                "model_name": model_name,
                "video_id"  : video_id,
            }


class BodytoriumAlbumExtractor(BodytoriumExtractor):
    """Extractor for albums"""
    subcategory = "album"
    directory_fmt = ("{category}", "{model_id}", "{album_id}")
    filename_fmt = "{album_id}_{num}.{extension}"
    pattern = BASE_PATTERN + r"/album/(ax?\d+-\d+)/?(?:$|[?#])"
    example = "https://bodytorium.com/album/a069-1/"

    def __init__(self, match):
        BodytoriumExtractor.__init__(self, match)
        self.album_id = match.group(1)

    def items(self):
        url = "{}/album/{}/".format(self.root, self.album_id)
        page = self.request(url).text

        model_url = text.extr(
            page, 'href="{}/model/'.format(self.root), '"')
        model_id = (model_url.rstrip("/").split("/")[-1] if model_url else
                    self.album_id.split("-")[0].replace("a", "m"))

        album_title = text.extr(page, "<h1>", "</h1>")
        album_title = album_title.strip() if album_title else self.album_id

        date = text.extr(page, "<h2>", "</h2>")
        if date:
            date = date.strip()

        data = {
            "album_id"   : self.album_id,
            "album_title": album_title,
            "model_id"   : model_id,
            "date"       : date,
        }
        yield Message.Directory, "", data

        num = 0
        for img_url in text.extract_iter(page, MEDIA_STORAGE + "/", '"'):
            if "/full/" not in img_url:
                continue

            img_url = text.unescape(img_url)
            url = "https://{}/{}".format(MEDIA_STORAGE, img_url)
            filename = img_url.split("/full/")[-1].split("?")[0]

            num += 1
            data["num"] = num
            text.nameext_from_name(filename, data)

            yield Message.Url, url, data


class BodytoriumVideoExtractor(BodytoriumExtractor):
    """Extractor for videos"""
    subcategory = "video"
    directory_fmt = ("{category}", "{model_id}", "{video_id}")
    filename_fmt = "{video_id}.{extension}"
    pattern = BASE_PATTERN + r"/video/(vx?\d+-\d+)/?(?:$|[?#])"
    example = "https://bodytorium.com/video/v069-1/"

    def __init__(self, match):
        BodytoriumExtractor.__init__(self, match)
        self.video_id = match.group(1)

    def items(self):
        url = "{}/video/{}/".format(self.root, self.video_id)
        page = self.request(url).text

        model_url = text.extr(
            page, 'href="{}/model/'.format(self.root), '"')
        model_id = (model_url.rstrip("/").split("/")[-1] if model_url else
                    self.video_id.split("-")[0].replace("v", "m"))

        video_title = text.extr(page, "<h2>", "</h2>")
        video_title = video_title.strip() if video_title else self.video_id

        date = text.extr(page, "<h5>", "</h5>")
        if date:
            date = date.strip()

        data = {
            "video_id"   : self.video_id,
            "video_title": video_title,
            "model_id"   : model_id,
            "date"       : date,
        }
        yield Message.Directory, "", data

        for video_url in text.extract_iter(page,
                                           MEDIA_STORAGE + "/",
                                           '"'):
            if ".mp4" not in video_url:
                continue

            video_url = text.unescape(video_url)

            url = "https://{}/{}".format(MEDIA_STORAGE, video_url)
            filename = video_url.split("/")[-1].split("?")[0]

            text.nameext_from_name(filename, data)
            yield Message.Url, url, data


class BodytoriumModelsExtractor(BodytoriumExtractor):
    """Extractor for the models listing page"""
    subcategory = "models"
    pattern = BASE_PATTERN + r"/models/?(?:$|[?#])"
    example = "https://bodytorium.com/models/"

    def items(self):
        url = self.root + "/models/"
        page = self.request(url).text

        for model_url in text.extract_iter(
                page, 'href="{}/model/'.format(self.root), '"'):
            model_id = model_url.rstrip("/").split("/")[-1]
            yield Message.Queue, "{}/model/{}/".format(
                self.root, model_id), {
                "_extractor": BodytoriumModelPageExtractor,
            }
