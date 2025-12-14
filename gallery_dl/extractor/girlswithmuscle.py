# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache

BASE_PATTERN = r"(?:https?://)?(?:www\.)?girlswithmuscle\.com"


class GirlswithmuscleExtractor(Extractor):
    """Base class for girlswithmuscle extractors"""
    category = "girlswithmuscle"
    root = "https://www.girlswithmuscle.com"
    directory_fmt = ("{category}", "{model}")
    filename_fmt = "{model}_{id}.{extension}"
    archive_fmt = "{type}_{model}_{id}"

    def login(self):
        username, password = self._get_auth_info()
        if username:
            self.cookies_update(self._login_impl(username, password))

    @cache(maxage=14*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = self.root + "/login/"
        page = self.request(url).text
        csrf_token = text.extr(page, 'name="csrfmiddlewaretoken" value="', '"')

        headers = {
            "Origin" : self.root,
            "Referer": url,
        }
        data = {
            "csrfmiddlewaretoken": csrf_token,
            "username": username,
            "password": password,
            "next": "/",
        }
        response = self.request(
            url, method="POST", headers=headers, data=data)

        if not response.history:
            raise exception.AuthenticationError()

        page = response.text
        if ">Wrong username or password" in page:
            raise exception.AuthenticationError()
        if ">Log in<" in page:
            raise exception.AuthenticationError("Account data is missing")

        return {c.name: c.value for c in response.history[0].cookies}


class GirlswithmusclePostExtractor(GirlswithmuscleExtractor):
    """Extractor for individual posts on girlswithmuscle.com"""
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/(\d+)"
    example = "https://www.girlswithmuscle.com/12345/"

    def items(self):
        self.login()

        url = f"{self.root}/{self.groups[0]}/"
        page = self.request(url).text
        if not page:
            raise exception.NotFoundError("post")

        metadata = self.metadata(page)

        if url := text.extr(page, 'class="main-image" src="', '"'):
            metadata["type"] = "picture"
        else:
            url = text.extr(page, '<source src="', '"')
            metadata["type"] = "video"

        text.nameext_from_url(url, metadata)
        yield Message.Directory, "", metadata
        yield Message.Url, url, metadata

    def metadata(self, page):
        source = text.remove_html(text.extr(
            page, '<div id="info-source" style="display: none">', "</div>"))
        image_info = text.extr(
            page, '<div class="image-info">', "</div>")
        uploader = text.remove_html(text.extr(
            image_info, '<span class="username-html">', "</a>"))

        tags = text.extr(page, 'id="tags-text">', "</div>")
        score = text.parse_int(text.remove_html(text.extr(
            page, "Score: <b>", "</span")))
        model = self._extract_model(page)

        return {
            "id": self.groups[0],
            "model": model,
            "model_list": self._parse_model_list(model),
            "tags": text.split_html(tags)[1::2],
            "date": self.parse_datetime_iso(text.extr(
                page, 'class="hover-time"  title="', '"')[:19]),
            "is_favorite": self._parse_is_favorite(page),
            "source_filename": source,
            "uploader": uploader,
            "score": score,
            "comments": self._extract_comments(page),
        }

    def _extract_model(self, page):
        model = text.extr(page, "<title>", "</title>")
        return "unknown" if model.startswith("Picture #") else model

    def _parse_model_list(self, model):
        if model == "unknown":
            return []
        else:
            return [name.strip() for name in model.split(",")]

    def _parse_is_favorite(self, page):
        fav_button = text.extr(
            page, 'id="favorite-button">', "</span>")
        unfav_button = text.extr(
            page, 'class="actionbutton unfavorite-button">', "</span>")

        is_favorite = None
        if unfav_button == "Unfavorite":
            is_favorite = True
        if fav_button == "Favorite":
            is_favorite = False

        return is_favorite

    def _extract_comments(self, page):
        comments = text.extract_iter(
            page, '<div class="comment-body-inner">', "</div>")
        return [comment.strip() for comment in comments]


class GirlswithmuscleSearchExtractor(GirlswithmuscleExtractor):
    """Extractor for search results on girlswithmuscle.com"""
    subcategory = "search"
    pattern = rf"{BASE_PATTERN}/images/(.*)"
    example = "https://www.girlswithmuscle.com/images/?name=MODEL"

    def pages(self):
        query = self.groups[0]
        url = f"{self.root}/images/{query}"
        response = self.request(url)
        if response.history:
            msg = f'Request was redirected to "{response.url}", try logging in'
            raise exception.AuthorizationError(msg)
        page = response.text

        match = text.re(r"Page (\d+) of (\d+)").search(page)
        current, total = match.groups()
        current, total = text.parse_int(current), text.parse_int(total)

        yield page
        for i in range(current + 1, total + 1):
            url = f"{self.root}/images/{i}/{query}"
            yield self.request(url).text

    def items(self):
        self.login()
        for page in self.pages():
            data = {
                "_extractor"  : GirlswithmusclePostExtractor,
                "gallery_name": text.unescape(text.extr(page, "<title>", "<")),
            }
            for imgid in text.extract_iter(page, 'id="imgid-', '"'):
                url = f"{self.root}/{imgid}/"
                yield Message.Queue, url, data
