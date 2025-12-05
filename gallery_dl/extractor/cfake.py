# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://cfake.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?cfake\.com"


class CfakeExtractor(Extractor):
    """Base class for cfake extractors"""
    category = "cfake"
    root = "https://cfake.com"
    directory_fmt = ("{category}", "{type}", "{type_name} ({type_id})")
    filename_fmt = "{category}_{type_name}_{id}.{extension}"
    archive_fmt = "{id}"

    def items(self):
        type, type_name, type_id, sub_id, pnum = self.groups

        if type.endswith("ies"):
            type = type[:-3] + "y"

        kwdict = self.kwdict
        kwdict["type"] = type
        kwdict["type_id"] = text.parse_int(type_id)
        kwdict["type_name"] = text.unquote(type_name).replace("_", " ")
        kwdict["sub_id"] = text.parse_int(sub_id)
        kwdict["page"] = pnum = text.parse_int(pnum, 1)
        yield Message.Directory, "", {}

        base = f"{self.root}/images/{type}/{type_name}/{type_id}"
        if sub_id:
            base = f"{base}/{sub_id}"

        while True:
            url = base if pnum < 2 else f"{base}/p{pnum}"
            page = self.request(url).text

            # Extract and yield images
            num = 0
            for image in self._extract_images(page):
                num += 1
                image["num"] = num + (pnum - 1) * 50
                url = image["url"]
                yield Message.Url, url, text.nameext_from_url(url, image)

            # Check for next page
            if not num or not (pnum := self._check_pagination(page)):
                return
            kwdict["page"] = pnum

    def _extract_images(self, page):
        """Extract image URLs and metadata from a gallery page"""
        for item in text.extract_iter(
                page, '<a href="javascript:showimage(', '</div></div>'):

            # Extract image path from showimage call
            # Format: 'big.php?show=2025/filename.jpg&id_picture=...
            show_param = text.extr(item, "show=", "&")
            if not show_param:
                continue

            # Extract metadata
            picture_id = text.extr(item, "id_picture=", "&")
            name_param = text.extr(item, "p_name=", "'")

            # Extract date
            date = text.extr(item, 'id="date_vignette">', '</div>')

            # Extract rating
            rating_text = text.extr(item, 'class="current-rating"', '</li>')
            rating = text.extr(rating_text, 'width:', 'px')

            # Convert thumbnail path to full image path
            # show_param is like "2025/filename.jpg"
            image_url = f"{self.root}/medias/photos/{show_param}"

            yield {
                "url": image_url,
                "id": text.parse_int(picture_id) if picture_id else 0,
                "name": text.unescape(name_param) if name_param else "",
                "date": date,
                "rating": rating,
            }

    def _check_pagination(self, page):
        """Check if there are more pages and return next page number"""
        # Look for current page indicator
        # Format: id="num_page_current" ><a href=".../ p1">1</a>
        current_section = text.extr(
            page, 'id="num_page_current"', '</div>')
        if not current_section:
            return None

        # Extract current page number from the link text
        current_page_str = text.extr(current_section, '">', '</a>')
        if not current_page_str:
            return None

        current_page = text.parse_int(current_page_str)
        if not current_page:
            return None

        next_page = current_page + 1

        # Check if next page link exists anywhere in the page
        # Look for href="/images/.../pN" pattern
        if f'/p{next_page}"' in page or f'/p{next_page} ' in page:
            return next_page

        return None


class CfakeCelebrityExtractor(CfakeExtractor):
    """Extractor for celebrity image galleries from cfake.com"""
    subcategory = "celebrity"
    pattern = (BASE_PATTERN + r"/images/(celebrity)"
               r"/([^/?#]+)/(\d+)()(?:/p(\d+))?")
    example = "https://cfake.com/images/celebrity/NAME/123"


class CfakeCategoryExtractor(CfakeExtractor):
    """Extractor for category image galleries from cfake.com"""
    subcategory = "category"
    pattern = (BASE_PATTERN + r"/images/(categories)"
               r"/([^/?#]+)/(\d+)()(?:/p(\d+))?")
    example = "https://cfake.com/images/categories/NAME/123"


class CfakeCreatedExtractor(CfakeExtractor):
    """Extractor for 'created' image galleries from cfake.com"""
    subcategory = "created"
    pattern = (BASE_PATTERN + r"/images/(created)"
               r"/([^/?#]+)/(\d+)/(\d+)(?:/p(\d+))?")
    example = "https://cfake.com/images/created/NAME/12345/123"


class CfakeCountryExtractor(CfakeExtractor):
    """Extractor for country image galleries from cfake.com"""
    subcategory = "country"
    pattern = (BASE_PATTERN + r"/images/(country)"
               r"/([^/?#]+)/(\d+)/(\d+)(?:/p(\d+))?")
    example = "https://cfake.com/images/country/NAME/12345/123"
