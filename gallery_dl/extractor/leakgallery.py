# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://leakgallery.com"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?leakgallery\.com"


class LeakgalleryExtractor(Extractor):
    category = "leakgallery"
    directory_fmt = ("{category}", "{creator}")
    filename_fmt = "{id}_{filename}.{extension}"
    archive_fmt = "{creator}_{id}"

    def _yield_media_items(self, medias, creator=None):
        seen = set()
        for media in medias:
            path = media["file_path"]
            if path in seen:
                continue
            seen.add(path)

            if creator is None:
                try:
                    media["creator"] = \
                        media["profile"]["username"] or "unknown"
                except Exception:
                    media["creator"] = "unknown"
            else:
                media["creator"] = creator

            media["url"] = url = f"https://cdn.leakgallery.com/{path}"
            text.nameext_from_url(url, media)
            yield Message.Directory, "", media
            yield Message.Url, url, media

    def _pagination(self, type, base, params=None, creator=None, pnum=1):
        while True:
            try:
                data = self.request_json(f"{base}{pnum}", params=params)

                if not data:
                    return
                if "medias" in data:
                    data = data["medias"]
                    if not data or not isinstance(data, list):
                        return

                yield from self._yield_media_items(data, creator)
                pnum += 1
            except Exception as exc:
                self.log.error("Failed to retrieve %s page %s: %s",
                               type, pnum, exc)
                return


class LeakgalleryUserExtractor(LeakgalleryExtractor):
    """Extractor for profile posts on leakgallery.com"""
    subcategory = "user"
    pattern = (
        BASE_PATTERN +
        r"/(?!trending-medias|most-liked|random/medias)([^/?#]+)"
        r"(?:/(Photos|Videos|All))?"
        r"(?:/(MostRecent|MostViewed|MostLiked))?/?$"
    )
    example = "https://leakgallery.com/creator"

    def items(self):
        creator, mtype, msort = self.groups
        base = f"https://api.leakgallery.com/profile/{creator}/"
        params = {"type": mtype or "All", "sort": msort or "MostRecent"}
        return self._pagination(creator, base, params, creator)


class LeakgalleryTrendingExtractor(LeakgalleryExtractor):
    """Extractor for trending posts on leakgallery.com"""
    subcategory = "trending"
    pattern = rf"{BASE_PATTERN}/trending-medias(?:/([\w-]+))?"
    example = "https://leakgallery.com/trending-medias/Week"

    def items(self):
        period = self.groups[0] or "Last-Hour"
        base = f"https://api.leakgallery.com/popular/media/{period}/"
        return self._pagination("trending", base)


class LeakgalleryMostlikedExtractor(LeakgalleryExtractor):
    """Extractor for most liked posts on leakgallery.com"""
    subcategory = "mostliked"
    pattern = rf"{BASE_PATTERN}/most-liked"
    example = "https://leakgallery.com/most-liked"

    def items(self):
        base = "https://api.leakgallery.com/most-liked/"
        return self._pagination("most-liked", base)


class LeakgalleryPostExtractor(LeakgalleryExtractor):
    """Extractor for individual posts on leakgallery.com"""
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/([^/?#]+)/(\d+)"
    example = "https://leakgallery.com/CREATOR/12345"

    def items(self):
        creator, post_id = self.groups
        url = f"https://leakgallery.com/{creator}/{post_id}"

        try:
            page = self.request(url).text
            video_urls = text.re(
                r"https://cdn\.leakgallery\.com/content[^/?#]*/"
                r"(?:compressed_)?watermark_[^\"]+\."
                r"(?:mp4|mov|m4a|webm)"
            ).findall(page)
            image_urls = text.re(
                r"https://cdn\.leakgallery\.com/content[^/?#]*/"
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
                    "url": url,
                }
                text.nameext_from_url(url, data)
                yield Message.Directory, "", data
                yield Message.Url, url, data
        except Exception as exc:
            self.log.error("Failed to extract post page %s/%s: %s",
                           creator, post_id, exc)
