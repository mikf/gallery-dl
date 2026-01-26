# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://listal.com"""
import re

from .common import Extractor, Message
from .. import text
from datetime import datetime

BASE_PATTERN = r"(?:https?://)?(?:www\.)?listal\.com"


class ListalExtractor(Extractor):
    """Base class for Listal extractor"""
    category = "listal"
    root = "https://www.listal.com"
    directory_fmt = ("{category}", "{title}")
    filename_fmt = "{id}_{url_filename}.{extension}"
    archive_fmt = "{id}/{url_filename}"

    def _pagination(self, base_url, pnum=None):
        page_pattern = text.re(r"^(.*)/(\d+)$")
        match = re.search(page_pattern, base_url)
        if match:
            pnum = int(match.group(2))
            url = base_url
            base_url = match.group(1)
        elif pnum is None:
            url = base_url
            pnum = 1
        else:
            url = f"{base_url}/{pnum}"

        while True:
            page = self.request(url).text

            yield page

            if pnum is None or "<span class='nextprev'>Next" in page:
                return
            pnum += 1
            url = f"{base_url}/{pnum}"

    def _hires_viewer_url(self, url):
        """This adds h after the url
        to get the largest size available picture"""
        if not url.endswith("h"):
            url += "h"
        return url

    def _extract_date(self, page):
        date_text = text.extract(page, " ago on ", "</span>")[0]
        date = datetime.strptime(date_text, "%d %B %Y %H:%M")
        return date

    def _extract_metadata_from_viewimage(self, page):
        id = text.extract(page, "data-id='", "'>")[0]
        metadata = {"id": id}
        author_link = text.extract(page, "Added by <a href='", "</a>")[0]
        metadata["author_url"] = author_link.replace("'>", "")
        author_name = text.extract(author_link, "'>", "")[0]
        metadata["author"] = author_name
        title = text.extract(page, 'title="', '"')[0]
        metadata["title"] = title
        date = self._extract_date(page)
        metadata["date"] = date
        width = text.extract(page, 'width="', '"')[0]
        metadata["width"] = width
        height = text.extract(page, 'height="', '"')[0]
        metadata["height"] = height
        img_url = text.extract(page, "<div><center><img src='https://", "'")[0]
        img_url = "https://" + img_url
        metadata["url"] = img_url
        url_filename, extension = img_url.split("/")[-1].rsplit(".", 1)
        metadata["url_filename"] = url_filename
        metadata["extension"] = extension
        return metadata

    def _extract_picture(self, view_image_url):
        """This extracts photo from the viewimage url scheme"""
        page = self.request(view_image_url).text
        metadata = self._extract_metadata_from_viewimage(page)
        return metadata


class ListalImageExtractor(ListalExtractor):
    """Extractor for listal pictures"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/viewimage/\d+h?"
    example = "https://www.listal.com/viewimage/12345678"

    def items(self):
        url = self._hires_viewer_url(self.url)
        page = self.request(url).text
        metadata = self._extract_metadata_from_viewimage(page)
        yield Message.Directory, "", metadata
        yield Message.Url, metadata["url"], metadata


class ListalPeopleExtractor(ListalExtractor):
    """Extractor for listal people"""
    subcategory = "people"
    pattern = BASE_PATTERN + r"/[^/?#]+/pictures"
    example = "https://www.listal.com/NAME/pictures"

    def items(self):
        for page in self._pagination(self.url):
            for image_id in text.extract_iter(
                    page, "listal.com/viewimage/", ">"):
                image_id = image_id.replace("'", "").replace('"', "")
                image_viewer_url = ("https://www.listal.com/viewimage/" +
                                    self._hires_viewer_url(image_id))
                metadata = self._extract_picture(image_viewer_url)
                yield Message.Directory, "", metadata
                yield Message.Url, metadata["url"], metadata
