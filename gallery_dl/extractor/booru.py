# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for *booru sites"""

from .common import BaseExtractor, Message
from .. import text
import operator


class BooruExtractor(BaseExtractor):
    """Base class for *booru extractors"""
    basecategory = "booru"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    page_start = 0
    per_page = 100

    def items(self):
        self.login()
        data = self.metadata()
        tags = self.config("tags", False)
        notes = self.config("notes", False)
        fetch_html = tags or notes

        url_key = self.config("url")
        if url_key:
            if isinstance(url_key, (list, tuple)):
                self._file_url = self._file_url_list
                self._file_url_keys = url_key
            else:
                self._file_url = operator.itemgetter(url_key)

        for post in self.posts():
            try:
                url = self._file_url(post)
                if url[0] == "/":
                    url = self.root + url
            except Exception as exc:
                self.log.debug("%s: %s", exc.__class__.__name__, exc)
                self.log.warning("Unable to fetch download URL for post %s "
                                 "(md5: %s)", post.get("id"), post.get("md5"))
                continue

            if fetch_html:
                html = self._html(post)
                if tags:
                    self._tags(post, html)
                if notes:
                    self._notes(post, html)

            text.nameext_from_url(url, post)
            post.update(data)
            self._prepare(post)

            yield Message.Directory, post
            yield Message.Url, url, post

    def skip(self, num):
        pages = num // self.per_page
        self.page_start += pages
        return pages * self.per_page

    def login(self):
        """Login and set necessary cookies"""

    def metadata(self):
        """Return a dict with general metadata"""
        return ()

    def posts(self):
        """Return an iterable with post objects"""
        return ()

    _file_url = operator.itemgetter("file_url")

    def _file_url_list(self, post):
        urls = (post[key] for key in self._file_url_keys if post.get(key))
        post["_fallback"] = it = iter(urls)
        return next(it)

    def _prepare(self, post):
        """Prepare a 'post's metadata"""

    def _html(self, post):
        """Return HTML content of a post"""

    def _tags(self, post, page):
        """Extract extended tag metadata"""

    def _notes(self, post, page):
        """Extract notes metadata"""
