# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bunkrr.su/"""

import re

from .lolisafe import LolisafeAlbumExtractor
from .. import text
from urllib.parse import urlparse, urlsplit, urlunsplit

MEDIA_DOMAIN_OVERRIDES = {
    "cdn9.bunkr.ru" : "c9.bunkr.ru",
    "cdn12.bunkr.ru": "media-files12.bunkr.la",
    "cdn-pizza.bunkr.ru": "pizza.bunkr.ru",
}

CDN_HOSTED_EXTENSIONS = (
    ".mp4", ".m4v", ".mov", ".webm", ".mkv", ".ts", ".wmv",
    ".zip", ".rar", ".7z",
)


class BunkrAlbumExtractor(LolisafeAlbumExtractor):
    """Extractor for bunkrr.su albums"""
    category = "bunkr"
    root = "https://bunkrr.su"
    pattern = r"(?:https?://)?(?:app\.)?bunkr+\.(?:la|[sr]u|is|to)/a/([^/?#]+)"
    example = "https://bunkrr.su/a/PoXwD1oA"

    def _get_download_url(self, media_url):
        if media_url.startswith("/"):
            media_url = self.root + media_url
        # The download URL is in the first <a> after the last <h1>.
        # Media preview pages only have one <h1> but other pages have two.
        html = self.request(media_url).text
        header_pos = html.rindex("<h1")
        download_url = text.extr(html[header_pos:], 'href="', '"')
        return download_url

    def fetch_album(self, album_id):
        # album metadata
        page = self.request(self.root + "/a/" + self.album_id).text
        info = text.split_html(text.extr(
            page, "<h1", "</div>").partition(">")[2])
        count, _, size = info[1].split(None, 2)

        # files
        cdn = None
        files = []
        append = files.append
        headers = {"Referer": self.root + "/"}

        # NOTE: we must use `finditer` instead of `findall` because we need
        # the original Match object, not just the first capture group.
        grid_tiles = re.finditer(
            # A <div> containing the class "grid-images_box"
            r"^ (\s*) <div[^>]+ \bgrid-images_box\b"
            # The contents of the <div>, ungreedy
            r".*?"
            # A closing </div> at the same indentation as the opening <div>
            r"^ \1 </div>",
            page,
            re.DOTALL | re.MULTILINE | re.VERBOSE
        )
        for match in grid_tiles:
            html = match.group()
            url = None

            # The whole URL and path for viewing a single media.
            media_url = text.extr(html, 'href="', '"')

            # Only get the CDN hostname once as it causes extra HTTP requests.
            # We could get each media's download URL this way but doing so
            # results in getting rate-limited, blocked, or a CAPTCHA page.
            if cdn is None:
                url = self._get_download_url(media_url)
                cdn = text.root_from_url(url)
                self.log.debug("Using CDN URL: {}".format(cdn))

            # We can assemble the correct download URL for media files using:
            #   1. The CDN hostname (e.g. "https://nugget.bunkr.ru")
            #   2. The thumbnail file name (e.g. "File-1--rIrVIhmb.png")
            #   3. The original file name (e.g. "File (1).mp4")
            # The thumbnail file name has the sanitized file name and file ID
            # but we need the file extension from the original file name.
            thumbnail_url = text.extr(html, 'src="', '"')
            if "no-image.svg" not in thumbnail_url:
                thumbnail_url = None

            details = re.findall(r"<p[^>]+> (.*?) </p>", html, re.VERBOSE)
            try:
                original_name = details[0].strip()
            except IndexError:
                original_name = None

            media_path = urlparse(media_url).path
            if media_path.startswith("/d/"):
                # Download pages already have the file name and ID in the URL.
                # However, their album tiles usually have a placeholder
                # thumbnail because the file has no preview.
                #   e.g. "/d/Resources-iwizfcKl.url"
                download_path = text.filename_from_url(media_path)
                url = "{}/{}".format(cdn, download_path)

            elif media_path.startswith("/i/") or media_path.startswith("/v/"):
                # For media preview pages, derive the download URL.
                if thumbnail_url and original_name:
                    thumb_name = text.filename_from_url(thumbnail_url)
                    thumb_base, _, thumb_ext = thumb_name.rpartition(".")
                    orig_base, _, orig_ext = original_name.rpartition(".")
                    url = "{}/{}.{}".format(cdn, thumb_base, orig_ext)

            # If we still don't have a download URL, use the slow method.
            # This is always required for MP3 files as they use a `/v/` media
            # path like videos but don't have a preview thumbnail.
            if not url:
                url = self._get_download_url(media_url)

            url = text.unescape(url)
            if url.lower().endswith(CDN_HOSTED_EXTENSIONS):
                scheme, domain, path, query, fragment = urlsplit(url)
                if domain in MEDIA_DOMAIN_OVERRIDES:
                    domain = MEDIA_DOMAIN_OVERRIDES[domain]
                else:
                    domain = domain.replace("cdn", "media-files", 1)
                url = urlunsplit((scheme, domain, path, query, fragment))
            append({"file": url, "_http_headers": headers})

        return files, {
            "album_id"   : self.album_id,
            "album_name" : text.unescape(info[0]),
            "album_size" : size[1:-1],
            "description": text.unescape(info[2]) if len(info) > 2 else "",
            "count"      : len(files),
        }
