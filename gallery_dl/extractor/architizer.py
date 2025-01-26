# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://architizer.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text


class ArchitizerProjectExtractor(GalleryExtractor):
    """Extractor for project pages on architizer.com"""
    category = "architizer"
    subcategory = "project"
    root = "https://architizer.com"
    directory_fmt = ("{category}", "{firm}", "{title}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{gid}_{num}"
    pattern = r"(?:https?://)?architizer\.com/projects/([^/?#]+)"
    example = "https://architizer.com/projects/NAME/"

    def __init__(self, match):
        url = "{}/projects/{}/".format(self.root, match.group(1))
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)
        extr('id="Pages"', "")

        return {
            "title"      : extr("data-name='", "'"),
            "slug"       : extr("data-slug='", "'"),
            "gid"        : extr("data-gid='", "'").rpartition(".")[2],
            "firm"       : extr("data-firm-leaders-str='", "'"),
            "location"   : extr("<h2>", "<").strip(),
            "type"       : text.unescape(text.remove_html(extr(
                '<div class="title">Type</div>', '<br'))),
            "status"     : text.remove_html(extr(
                '<div class="title">STATUS</div>', '</')),
            "year"       : text.remove_html(extr(
                '<div class="title">YEAR</div>', '</')),
            "size"       : text.remove_html(extr(
                '<div class="title">SIZE</div>', '</')),
            "description": text.unescape(extr(
                '<span class="copy js-copy">', '</span></div>')
                .replace("<br />", "\n")),
        }

    def images(self, page):
        return [
            (url, None)
            for url in text.extract_iter(
                page, "property='og:image:secure_url' content='", "?")
        ]


class ArchitizerFirmExtractor(Extractor):
    """Extractor for all projects of a firm"""
    category = "architizer"
    subcategory = "firm"
    root = "https://architizer.com"
    pattern = r"(?:https?://)?architizer\.com/firms/([^/?#]+)"
    example = "https://architizer.com/firms/NAME/"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.firm = match.group(1)

    def items(self):
        url = url = "{}/firms/{}/?requesting_merlin=pages".format(
            self.root, self.firm)
        page = self.request(url).text
        data = {"_extractor": ArchitizerProjectExtractor}

        for project in text.extract_iter(page, '<a href="/projects/', '"'):
            if not project.startswith("q/"):
                url = "{}/projects/{}".format(self.root, project)
                yield Message.Queue, url, data
