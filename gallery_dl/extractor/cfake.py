# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://cfake.com/"""

from .common import Extractor, Message
from .. import text
from urllib.parse import unquote


BASE_PATTERN = r"(?:https?://)?(?:www\.)?cfake\.com"


class CfakeExtractor(Extractor):
    """Base class for cfake extractors"""
    category = "cfake"
    root = "https://cfake.com"
    directory_fmt = ("{category}", "{type}", "{name}")
    filename_fmt = "{category}_{name}_{id}_{num}.{extension}"
    archive_fmt = "{id}"

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
    pattern = BASE_PATTERN + r"/images/celebrity/([^/]+)/(\d+)(?:/p(\d+))?"
    example = "https://cfake.com/images/celebrity/Kaley_Cuoco/631/"

    def __init__(self, match):
        CfakeExtractor.__init__(self, match)
        self.celebrity_name = match.group(1)
        self.celebrity_id = match.group(2)
        self.page_num = text.parse_int(match.group(3), 1)

    def items(self):
        page_num = self.page_num

        while True:
            if page_num == 1:
                url = (f"{self.root}/images/celebrity/"
                       f"{self.celebrity_name}/{self.celebrity_id}/")
            else:
                url = (f"{self.root}/images/celebrity/"
                       f"{self.celebrity_name}/{self.celebrity_id}/"
                       f"p{page_num}")

            page = self.request(url).text

            data = {
                "type": "celebrity",
                "name": unquote(self.celebrity_name).replace("_", " "),
                "celebrity_id": text.parse_int(self.celebrity_id),
                "page": page_num,
            }

            # Yield directory on first page
            if page_num == self.page_num:
                yield Message.Directory, data

            # Extract and yield images
            num = 0
            for image_data in self._extract_images(page):
                num += 1
                image_data.update(data)
                image_data["num"] = num + (page_num - 1) * 50
                url = image_data.pop("url")
                yield Message.Url, url, text.nameext_from_url(
                    url, image_data)

            # Check for next page
            next_page = self._check_pagination(page)
            if not next_page or num == 0:
                break

            page_num = next_page


class CfakeCategoryExtractor(CfakeExtractor):
    """Extractor for category image galleries from cfake.com"""
    subcategory = "category"
    pattern = (BASE_PATTERN +
               r"/images/categories/([^/]+)/(\d+)(?:/p(\d+))?")
    example = "https://cfake.com/images/categories/Facial/25/"

    def __init__(self, match):
        CfakeExtractor.__init__(self, match)
        self.category_name = match.group(1)
        self.category_id = match.group(2)
        self.page_num = text.parse_int(match.group(3), 1)

    def items(self):
        page_num = self.page_num

        while True:
            if page_num == 1:
                url = (f"{self.root}/images/categories/"
                       f"{self.category_name}/{self.category_id}/")
            else:
                url = (f"{self.root}/images/categories/"
                       f"{self.category_name}/{self.category_id}/"
                       f"p{page_num}")

            page = self.request(url).text

            data = {
                "type": "category",
                "name": unquote(self.category_name).replace("_", " "),
                "category_id": text.parse_int(self.category_id),
                "page": page_num,
            }

            # Yield directory on first page
            if page_num == self.page_num:
                yield Message.Directory, data

            # Extract and yield images
            num = 0
            for image_data in self._extract_images(page):
                num += 1
                image_data.update(data)
                image_data["num"] = num + (page_num - 1) * 50
                url = image_data.pop("url")
                yield Message.Url, url, text.nameext_from_url(
                    url, image_data)

            # Check for next page
            next_page = self._check_pagination(page)
            if not next_page or num == 0:
                break

            page_num = next_page


class CfakeCreatedExtractor(CfakeExtractor):
    """Extractor for 'created' image galleries from cfake.com"""
    subcategory = "created"
    pattern = (BASE_PATTERN +
               r"/images/created/([^/]+)/(\d+)/(\d+)(?:/p(\d+))?")
    example = "https://cfake.com/images/created/Spice_Girls_%28band%29/72/4"

    def __init__(self, match):
        CfakeExtractor.__init__(self, match)
        self.created_name = match.group(1)
        self.created_id = match.group(2)
        self.sub_id = match.group(3)
        self.page_num = text.parse_int(match.group(4), 1)

    def items(self):
        page_num = self.page_num

        while True:
            if page_num == 1:
                url = (f"{self.root}/images/created/"
                       f"{self.created_name}/{self.created_id}/"
                       f"{self.sub_id}")
            else:
                url = (f"{self.root}/images/created/"
                       f"{self.created_name}/{self.created_id}/"
                       f"{self.sub_id}/p{page_num}")

            page = self.request(url).text

            data = {
                "type": "created",
                "name": unquote(self.created_name).replace("_", " "),
                "created_id": text.parse_int(self.created_id),
                "sub_id": text.parse_int(self.sub_id),
                "page": page_num,
            }

            # Yield directory on first page
            if page_num == self.page_num:
                yield Message.Directory, data

            # Extract and yield images
            num = 0
            for image_data in self._extract_images(page):
                num += 1
                image_data.update(data)
                image_data["num"] = num + (page_num - 1) * 50
                url = image_data.pop("url")
                yield Message.Url, url, text.nameext_from_url(
                    url, image_data)

            # Check for next page
            next_page = self._check_pagination(page)
            if not next_page or num == 0:
                break

            page_num = next_page


class CfakeCountryExtractor(CfakeExtractor):
    """Extractor for country image galleries from cfake.com"""
    subcategory = "country"
    pattern = (BASE_PATTERN +
               r"/images/country/([^/]+)/(\d+)/(\d+)(?:/p(\d+))?")
    example = "https://cfake.com/images/country/Australia/12/5"

    def __init__(self, match):
        CfakeExtractor.__init__(self, match)
        self.country_name = match.group(1)
        self.country_id = match.group(2)
        self.sub_id = match.group(3)
        self.page_num = text.parse_int(match.group(4), 1)

    def items(self):
        page_num = self.page_num

        while True:
            if page_num == 1:
                url = (f"{self.root}/images/country/"
                       f"{self.country_name}/{self.country_id}/"
                       f"{self.sub_id}")
            else:
                url = (f"{self.root}/images/country/"
                       f"{self.country_name}/{self.country_id}/"
                       f"{self.sub_id}/p{page_num}")

            page = self.request(url).text

            data = {
                "type": "country",
                "name": unquote(self.country_name).replace("_", " "),
                "country_id": text.parse_int(self.country_id),
                "sub_id": text.parse_int(self.sub_id),
                "page": page_num,
            }

            # Yield directory on first page
            if page_num == self.page_num:
                yield Message.Directory, data

            # Extract and yield images
            num = 0
            for image_data in self._extract_images(page):
                num += 1
                image_data.update(data)
                image_data["num"] = num + (page_num - 1) * 50
                url = image_data.pop("url")
                yield Message.Url, url, text.nameext_from_url(
                    url, image_data)

            # Check for next page
            next_page = self._check_pagination(page)
            if not next_page or num == 0:
                break

            page_num = next_page
