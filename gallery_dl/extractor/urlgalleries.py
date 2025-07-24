# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://urlgalleries.net/"""

from .common import GalleryExtractor, Message
from .. import text, exception
import re


class UrlgalleriesGalleryExtractor(GalleryExtractor):
    """Base class for Urlgalleries extractors"""
    category = "urlgalleries"
    root = "https://urlgalleries.net"
    request_interval = (0.5, 1.5)
    pattern = (r"(?:https?://)()(?:(\w+)\.)?urlgalleries\.net"
               r"/(?:b/([^/?#]+)/)?(?:[\w-]+-)?(\d+)")
    example = "https://urlgalleries.net/b/BLOG/gallery-12345/TITLE"

    def _process_image_url(self, img_url):
        """Process image URL to handle both old and new formats"""
        # New CDN format (direct image URL)
        if "cdno-data.imagevenue.com" in img_url:
            return img_url
            
        # Old thumbnail format that needs conversion
        if "imagevenue.com" in img_url:
            patterns = [
                r'/(?:loc\d+/)?th?_(\d+_.*\.(?:jpg|png|gif|webp))',
                r'/(?:loc\d+/)?img_(\d+_.*\.(?:jpg|png|gif|webp))',
                r'/(\d+_.*\.(?:jpg|png|gif|webp))'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, img_url)
                if match:
                    server = img_url.split('/')[2].split('.')[0]
                    return f"https://{server}.imagevenue.com/img.php?image={match.group(1)}"
        
        return img_url.partition("?")[0]  # Return original URL without parameters

    def items(self):
        _, blog_alt, blog, self.gallery_id = self.groups
        if not blog:
            blog = blog_alt
        url = f"{self.root}/b/{blog}/porn-gallery-{self.gallery_id}/?a=10000"

        with self.request(url, allow_redirects=False, fatal=...) as response:
            if 300 <= response.status_code < 500:
                if response.headers.get("location", "").endswith(
                        "/not_found_adult.php"):
                    raise exception.NotFoundError("gallery")
                raise exception.HttpError(None, response)
            page = response.text

        imgs = self.images(page)
        data = self.metadata(page)
        data["count"] = len(imgs)

        # First try new direct CDN image URLs
        cdn_urls = list(text.extract_iter(page, 'src="https://cdno-data.imagevenue.com/', '"'))
        if cdn_urls:
            for data["num"], img_url in enumerate(cdn_urls, 1):
                full_url = f"https://cdno-data.imagevenue.com/{img_url.split('"')[0]}"
                yield Message.Queue, full_url, data
            return

        # Fall back to original processing if no CDN URLs found
        root = self.root
        yield Message.Directory, data
        for data["num"], img in enumerate(imgs, 1):
            try:
                # Check if this is already a direct image URL
                processed_url = self._process_image_url(img)
                if processed_url and processed_url.startswith(('http://', 'https://')):
                    yield Message.Queue, processed_url, data
                    continue
                    
                # Original processing flow
                page = self.request(root + img).text
                url = text.extr(page, "window.location.href = '", "'")
                yield Message.Queue, url.partition("?")[0], data
            except Exception as e:
                self.log.warning("Failed to process image %s: %s", img, str(e))

    def metadata(self, page):
        extr = text.extract_from(page)
        return {
            "gallery_id": self.gallery_id,
            "_site": extr(' title="', '"'),  # site name
            "blog": text.unescape(extr(' title="', '"')),
            "_rprt": extr(' title="', '"'),  # report button
            "title": text.unescape(extr(' title="', '"').strip()),
            "date": text.parse_datetime(
                extr(" images in gallery | ", "<"), "%B %d, %Y"),
        }

    def images(self, page):
        """Extract image URLs from page with fallback to original method"""
        # First try to find CDN images in the full page
        wtf_section = text.extr(page, 'id="wtf"', "</div>")
        if not wtf_section:
            return []
            
        return list(text.extract_iter(wtf_section, " href='", "'"))
