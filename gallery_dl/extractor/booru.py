# -*- coding: utf-8 -*-

# Copyright 2015-2022 Mike Fährmann
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

        for post in self.posts():
            try:
                url = self._file_url(post)
                if url[0] == "/":
                    url = self.root + url
            except (KeyError, TypeError):
                self.log.debug("Unable to fetch download URL for post %s "
                               "(md5: %s)", post.get("id"), post.get("md5"))
                continue

            page_html = None
            if tags:
                page_html = self._extended_tags(post)
            if notes:
                self._notes(post, page_html)
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

    def _prepare(self, post):
        """Prepare the 'post's metadata"""

    def _extended_tags(self, post, page=None):
        """Generate extended tag information

        The return value of this function will be
        passed to the _notes function as the page parameter.
        This makes it possible to reuse the same HTML both for
        extracting tags and notes.
        """

    def _notes(self, post, page=None):
        """Generate information about notes"""
