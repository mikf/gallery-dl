# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://foriio.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?fori(?:io\.com|\.io)"


class ForiioExtractor(Extractor):
    """Base class for foriio extractors"""
    category = "foriio"
    root = "https://foriio.com"
    root_api = "https://api.foriio.com/api"


class ForiioWorkExtractor(ForiioExtractor):
    subcategory = "work"
    directory_fmt = ("{category}", "{author[screen_name]} ({author[id]})",
                     "{date:%Y-%m-%d} {title[b:230]} ({work_id})")
    filename_fmt = "{num:>02} {file_id}.{extension}"
    archive_fmt = "{work_id}/{file_id}/{num}"
    pattern = BASE_PATTERN + r"/works/(\d+)"
    example = "https://www.foriio.com/works/12345"

    def items(self):
        url = f"{self.root_api}/v1/works/{self.groups[0]}"
        work = self.request_json(url, notfound=True)["work"]

        work.pop("related_works", None)
        work.pop("single_work_og", None)
        work.pop("og_image_url_for_instagram", None)
        work["work_id"] = work.pop("id")
        work["date"] = self.parse_datetime_iso(work["published_at"])

        if "images" in work:
            files = work.pop("images")
            work["count"] = len(files)
            yield Message.Directory, "", work
            for work["num"], file in enumerate(files, 1):
                url = file["urls"]["list"].partition("?")[0]

                work["width"] = file["width"]
                work["height"] = file["height"]
                work["file_id"] = file["id"]

                url = _orig(name := url[url.rfind("/")+1:])
                yield Message.Url, url, text.nameext_from_url(name, work)
            return

        previews = self.config("previews", False)
        if "videos" in work:
            files = work.pop("videos")
            work["count"] = len(files)
            yield Message.Directory, "", work

            video = self.config("videos", True)
            for work["num"], file in enumerate(files, 1):
                work["file_id"] = file.get("video_id") or file["title"]
                work.update(file)
                if video:
                    work["extension"] = "mp4"
                    yield Message.Url, "ytdl:" + file["url"], work
                if previews:
                    url = file["picture_url"]
                    url = _orig(name := url[url.rfind("/")+1:])
                    yield Message.Url, url, text.nameext_from_url(name, work)
            return

        if "sounds" in work:
            files = work.pop("sounds")
            work["count"] = len(files)
            yield Message.Directory, "", work

            audio = self.config("audio", True)
            for work["num"], file in enumerate(files, 1):
                work["file_id"] = file["title"]
                work.update(file)
                if audio:
                    work["extension"] = "mp3"
                    yield Message.Url, "ytdl:" + file["url"], work
                if previews:
                    url = file["picture_url"]
                    url = _orig(name := url[url.rfind("/")+1:])
                    yield Message.Url, url, text.nameext_from_url(name, work)
            return

        if "web_articles" in work:
            files = work.pop("web_articles")
            work["count"] = len(files)
            yield Message.Directory, "", work

            external = self.config("external", True)
            for work["num"], file in enumerate(files, 1):
                work["file_id"] = file["title"]
                work.update(file)
                if external:
                    yield Message.Queue, file["url"], work
                if previews:
                    url = file["image"]
                    url = _orig(name := url[url.rfind("/")+1:])
                    yield Message.Url, url, text.nameext_from_url(name, work)
            return

        if "copy_writing" in work:
            file = work["copy_writing"]
            work["count"] = work["num"] = 1
            work["file_id"] = file["id"]
            url = file["image"]
            url = _orig(name := url[url.rfind("/")+1:])
            yield Message.Directory, "", work
            yield Message.Url, url, text.nameext_from_url(name, work)

        else:
            return self.log.error("%s: Unsupported type %r",
                                  work["id"], work["type"])


class ForiioUserExtractor(ForiioExtractor):
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!works/)([^/?#]+)"
    example = "https://foriio.com/USER"

    def items(self):
        if posts := self.config("posts"):
            if isinstance(posts, str):
                posts = posts.split(",")
            posts = set(posts)

        url = f"{self.root_api}/v1/users/{self.groups[0]}/works"
        params = {
            "page"    : 1,
            "per_page": "20",
        }
        headers = {
            "Referer": self.root + "/",
            "Origin" : self.root,
        }

        base = self.root + "/works/"
        while True:
            data = self.request_json(url, params=params, headers=headers)

            for work in data["works"]:
                if posts and work.get("type") not in posts:
                    self.log.debug("%s: Skipping work of type %r",
                                   work["id"], work["type"])
                    continue
                work["_extractor"] = ForiioWorkExtractor
                yield Message.Queue, base + str(work["id"]), work

            try:
                meta = data["meta"]
                if meta["current_page"] >= meta["total_pages"]:
                    break
            except Exception as exc:
                self.log.traceback(exc)
                break

            params["page"] += 1


def _orig(name):
    return "https://foriio.imgix.net/store/" + name
