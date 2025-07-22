# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://leakgallery.com"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?leakgallery\.com"


class LeakGalleryExtractorBase(Extractor):
    category = "leakgallery"
    directory_fmt = ("{category}", "{creator}")
    filename_fmt = "{id}_{filename}.{extension}"
    archive_fmt = "{creator}_{id}"

    def _yield_media_items(self, medias, creator=None):
        seen = set()
        for media in medias:
            cdn_url = "https://cdn.leakgallery.com/" + media["file_path"]
            if cdn_url in seen:
                continue
            seen.add(cdn_url)
            media_creator = (
                media.get("profile", {}).get("username")
                or creator
                or "unknown"
            )
            data = {
                "id": media["id"],
                "creator": media_creator,
                "category": self.category,
                "url": cdn_url,
                "_extractor": self,
            }
            text.nameext_from_url(cdn_url, data)
            yield Message.Directory, data
            yield Message.Url, cdn_url, data


class LeakGalleryUserExtractor(LeakGalleryExtractorBase):
    """Extractor for profile posts on leakgallery.com"""
    subcategory = "user"
    pattern = (
        BASE_PATTERN
        + r"/(?!trending-medias|most-liked|random/medias)([^/?#]+)"
        + r"(?:/(Photos|Videos|All))?(?:/(MostRecent|MostViewed|MostLiked))?/?$"
    )
    example = "https://leakgallery.com/creator"

    def items(self):
        creator = self.groups[0]
        mtype = self.groups[1] or "All"
        msort = self.groups[2] or "MostRecent"

        base = f"https://api.leakgallery.com/profile/{creator}/"
        params = {"type": mtype, "sort": msort}

        page = 1
        while True:
            try:
                response = self.request(base + str(page), params=params).json()
                medias = response.get("medias")
                if not isinstance(medias, list) or not medias:
                    return
                yield from self._yield_media_items(medias, creator=creator)
                page += 1
            except Exception as e:
                self.log("error", f"Failed to retrieve page {page}: {e}")
                return


class LeakGalleryTrendingExtractor(LeakGalleryExtractorBase):
    """Extractor for trending posts on leakgallery.com"""
    subcategory = "trending"
    pattern = BASE_PATTERN + r"/trending-medias(?:/([A-Za-z0-9\-]+))?"
    example = "https://leakgallery.com/trending-medias/Week"

    def items(self):
        period = self.groups[0] or "Last-Hour"
        page = 1
        while True:
            try:
                url = (
                    f"https://api.leakgallery.com/popular/media/{period}/{page}"
                )
                response = self.request(url).json()
                if not response:
                    return
                yield from self._yield_media_items(response)
                page += 1
            except Exception as e:
                self.log(
                    "error",
                    f"Failed to retrieve trending page {page}: {e}"
                )
                return


class LeakGalleryMostLikedExtractor(LeakGalleryExtractorBase):
    """Extractor for most liked posts on leakgallery.com"""
    subcategory = "mostliked"
    pattern = BASE_PATTERN + r"/most-liked"
    example = "https://leakgallery.com/most-liked"

    def items(self):
        page = 1
        while True:
            try:
                url = f"https://api.leakgallery.com/most-liked/{page}"
                response = self.request(url).json()
                if not response:
                    return
                yield from self._yield_media_items(response)
                page += 1
            except Exception as e:
                self.log(
                    "error",
                    f"Failed to retrieve most-liked page {page}: {e}"
                )
                return


class LeakGalleryPostExtractor(LeakGalleryExtractorBase):
    """Extractor for individual posts on leakgallery.com"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/([^/?#]+)/([0-9]+)"
    example = "https://leakgallery.com/creator/post_id"

    def items(self):
        creator, post_id = self.groups
        self.url = f"https://leakgallery.com/{creator}/{post_id}"
        try:
            page = self.request(self.url).text
            video_urls = text.re(
                r"https://cdn\.leakgallery\.com/content[^/]*/"
                r"(?:compressed_)?watermark_[^\"]+\.(?:mp4|mov|m4a|webm)"
            ).findall(page)
            image_urls = text.re(
                r"https://cdn\.leakgallery\.com/content[^/]*/"
                r"watermark_[^\"]+\.(?:jpe?g|png)"
            ).findall(page)

            seen = set()
            for url in video_urls + image_urls:
                if url in seen:
                    continue
                seen.add(url)
                data = {
                    "id": post_id,
                    "creator": creator,
                    "category": self.category,
                    "url": url,
                }
                text.nameext_from_url(url, data)
                yield Message.Directory, data
                yield Message.Url, url, data

            if not seen:
                self.log("info", f"No downloadable media found for {self.url}")
        except Exception as e:
            self.log("error", f"Failed to extract post page: {e}")
