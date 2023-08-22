# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import re

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache


class GirlswithmuscleExtractor(Extractor):
    def login(self):
        username, password = self._get_auth_info()
        if username:
            self.cookies_update(self._login_impl(username, password))

    @staticmethod
    def _is_logged_in(page_text: str) -> bool:
        return 'Log in' not in page_text

    @staticmethod
    def _get_csrfmiddlewaretoken(page: str) -> str:
        return text.extract(
            page,
            'name="csrfmiddlewaretoken" value="',
            '"'
        )[0]

    def _open_login_page(self):
        """We need it to get second CSRF token"""
        url = "https://www.girlswithmuscle.com/login/?next=/"
        response = self.request(url)
        return self._get_csrfmiddlewaretoken(response.text)

    def _send_login_request(self, username, password, csrf_mw):
        """Actual login action"""
        data = {
            "csrfmiddlewaretoken": csrf_mw,
            "username": username,
            "password": password,
            "next": "/"
        }

        # Otherwise will be 403 Forbidden
        self.session.headers['Origin'] = 'https://www.girlswithmuscle.com'
        self.session.headers['Referer'] = \
            'https://www.girlswithmuscle.com/login/?next=/'

        # if successful, will update cookies
        url = "https://www.girlswithmuscle.com/login/"
        response = self.request(url, method="post", data=data)

        if "Wrong username or password" in response.text:
            raise exception.AuthenticationError()
        elif not self._is_logged_in(response.text):
            raise exception.AuthenticationError("Account data is missing")

    @cache(maxage=28 * 86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        csrf_mw = self._open_login_page()
        self._send_login_request(username, password, csrf_mw)
        return {c.name: c.value for c in self.session.cookies}


class GirlswithmusclePostExtractor(GirlswithmuscleExtractor):
    """Extractor for individual posts on girlswithmuscle.com"""
    category = "girlswithmuscle"
    subcategory = "post"
    directory_fmt = ("{category}", "{model}")
    filename_fmt = "{model}_{id}.{extension}"
    archive_fmt = "{type}_{model}_{id}"
    pattern = (r"(?:https?://)?(?:www\.)?girlswithmuscle\.com"
               r"/(\d+)/")
    example = "https://www.girlswithmuscle.com/1841638/"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.id = match.groups()[0]

    def items(self):
        self.login()
        url = "https://girlswithmuscle.com/{}/".format(self.id)
        page = self.request(url).text

        if page is None:
            raise exception.NotFoundError("post")

        url = text.extr(page, 'class="main-image" src="', '"')
        if url:
            metadata = self.metadata(page, url, 'picture')
        else:
            url = text.extr(page, '<source src="', '"')
            metadata = self.metadata(page, url, 'video')

        yield Message.Directory, metadata
        yield Message.Url, url, metadata

    def metadata(self, page, url, content_type):
        info_source_begin = \
            '<div class="image-info" id="info-source" style="display: none">'
        info_source_end = "</div>"
        source = text.remove_html(
            text.extr(page, info_source_begin, info_source_end))

        info_uploader_begin = '<div class="image-info" id="info-uploader">'
        info_uploader_end = "</div>"
        uploader = text.remove_html(
            text.extr(page, info_uploader_begin, info_uploader_end))

        tags = text.extr(
            page, 'class="selected-tags">', "</span>", ''
        ).split(', ')
        tags = [tag for tag in tags if tag]

        score = text.parse_int(text.remove_html(
            text.extr(page, 'Score: <b>', '</span', '0')))

        model = self._parse_model(page)

        return {
            'id': self.id,
            'model': model,
            'model_list': self._parse_model_list(model),
            'tags': tags,
            'posted_dt': text.extr(
                page, 'class="hover-time"  title="', '"', ''
            ),
            'is_favorite': self._parse_is_favorite(page),
            'source_filename': source,
            'uploader': uploader,
            'score': score,
            'comments': self._parse_comments(page),
            'extension': text.ext_from_url(url),
            'type': content_type,
        }

    @staticmethod
    def _parse_model(page):
        model = text.extr(page, '<title>', "</title>", None)
        return 'unknown' if model.startswith('Picture #') else model

    @staticmethod
    def _parse_model_list(model):
        if model == 'unknown':
            return []
        else:
            return [name.strip() for name in model.split(',')]

    @staticmethod
    def _parse_is_favorite(page):
        fav_button = text.extr(page, 'id="favorite-button">', "</span>", '')
        unfav_button = text.extr(page,
                                 'class="actionbutton unfavorite-button">',
                                 "</span>", '')

        is_favorite = None
        if unfav_button == 'Unfavorite':
            is_favorite = True
        if fav_button == 'Favorite':
            is_favorite = False

        return is_favorite

    @staticmethod
    def _parse_comments(page):
        comments = text.extract_iter(page, '<div class="comment-body-inner">',
                                     '</div>')
        return [comment.strip() for comment in comments]


class GirlswithmuscleGalleryExtractor(GirlswithmuscleExtractor):
    """Extractor for galleries on girlswithmuscle.com"""
    category = "girlswithmuscle"
    subcategory = "gallery"
    pattern = r"(?:https?://)?(?:www\.)?girlswithmuscle\.com/images/(.*)"
    example = "https://www.girlswithmuscle.com/images/?name=Samantha%20Jerring"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.query = match.groups()[0]

    def pages(self):
        url = "https://www.girlswithmuscle.com/images/{}".format(self.query)
        response = self.request(url)
        if url != response.url:
            msg = ('Request was redirected to "{}", try logging in'.
                   format(response.url))
            raise exception.AuthorizationError(msg)
        page = response.text

        match = re.search(r"Page (\d+) of (\d+)", page)
        current, total = match.groups()
        current, total = text.parse_int(current), text.parse_int(total)

        yield page
        for i in range(current + 1, total + 1):
            url = ("https://www.girlswithmuscle.com/images/{}/{}".
                   format(i, self.query))
            yield self.request(url).text

    def items(self):
        self.login()
        for page in self.pages():
            for imgid in text.extract_iter(page, 'id="imgid-', '"'):
                url = "https://www.girlswithmuscle.com/{}/".format(imgid)
                yield Message.Queue, url, {
                    "gallery_name": self._parse_gallery_name(page),
                    "_extractor": GirlswithmusclePostExtractor
                }

    @staticmethod
    def _parse_gallery_name(page):
        return text.extr(page, "<title>", "</title>")
