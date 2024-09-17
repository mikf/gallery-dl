# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://motherless.com/"""

from .common import Extractor, Message
from .. import text
import re
from datetime import datetime, timedelta, timezone

ROOT_URL_PATTERN = r"(?:https?://)?motherless\.com"


class MotherlessExtractor(Extractor):
    """Base class for motherless extractors"""

    category = "motherless"
    root = "https://motherless.com"
    filename_fmt = "{id} {title}.{extension}"


class MotherlessMediaExtractor(MotherlessExtractor):
    """Extractor for a single image/video from motherless.com"""

    pattern = ROOT_URL_PATTERN + "/([A-Z0-9]+)$"
    example = "https://motherless.com/ABC123"
    directory_fmt = ("{category}",)

    def items(self):
        image_url, data = self.get_image()
        yield Message.Directory, data
        yield Message.Url, image_url, data

    def get_image(self):
        self.page_data = self.request(self.url).text

        try:
            # Find image source url.
            self.subcategory = "image"

            image_url_search = re.search(f'<link rel="image_src" type="image/([a-z]+)" href="(.+)">', self.page_data)
            extension = image_url_search.group(1)
            media_url = image_url_search.group(2)
            id = self.get_image_id(media_url)

        except AttributeError:
            # No image, find video url.
            self.subcategory = "video"

            video_url_search = re.search("__fileurl = '(.+)'", self.page_data)
            extension = "mp4"
            media_url = video_url_search.group(1)
            id = self.get_video_id(media_url)

        data = {
            "url": self.url,
            "title": self.get_title(self.page_data),
            "id": id,
            "filename": id,
            "extension": extension,
            "date": self.get_date(self.page_data),
            "uploader": self.get_uploader(self.page_data),
            "tags": self.get_tags(self.page_data)}

        return media_url, data

    def get_tags(self, page_html):
        try:
            tags_html = re.search('<div class="media-meta-tags">([\S\s]+?)</div>', page_html).group(1)
        except AttributeError:
            # No tags found.
            return []

        tags = text.split_html(tags_html)
        for i, tag in enumerate(tags):
            tags[i] = tag.replace('#', '')

        return tags

    def get_title(self, page_html):
        title = re.search('<div class="media-meta-title">([\S\s]+?)</div>', page_html).group(1)
        return text.remove_html(title)

    def get_date(self, page_html):
        # Find date uploaded and convert to ISO 8601.

        try:
            # Find 'DD Mon YYYY' format.
            date = re.search('<span class="count">(\d{1,2}\s+\w+\s+\d{4})<\/span>', page_html).group(1)
            return text.parse_datetime(date, "%d  %b  %Y").isoformat()

        except AttributeError:
            # Find 'nd ago' format.
            days_ago = int(re.search('<span class="count">(\d+)\s*d\s*ago<\/span>', page_html).group(1))
            return (datetime.now(timezone.utc) - timedelta(days=days_ago)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    def get_uploader(self, page_html):
        username_html = re.search('class="username">\s+(.+[^\s])\s+<\/span>', page_html).group(1)
        return text.remove_html(username_html)
    
    def get_image_id(self, image_url):
        return text.extract(image_url, 'images/', '.')[0]
    
    def get_video_id(self, video_url):
        video_id = text.extract(video_url, 'videos/', '.')[0]

        if '-' in video_id:
            return text.extract(video_id, '', '-')[0]
        return video_id

class MotherlessMediaInGalleryExtractor(MotherlessMediaExtractor):
    """Extractor for a single image/video from a gallery from motherless.com"""

    directory_fmt = ("{category}", "{gallery_id} {gallery_title}")
    pattern = ROOT_URL_PATTERN + "/(?:GI?)([A-Z0-9]+)/([A-Z0-9]+)"
    example = "https://motherless.com/GABC123/DEF456"

    def get_image(self):
        media_url, data =  super().get_image()
        data['gallery_id'] = re.match(self.pattern, self.url).group(1)
        data['gallery_title'] = self.get_gallery_name(self.page_data, data['gallery_id'])
        return media_url, data
    
    def get_gallery_name(self, page_data, gallery_id):
        try:
            # 'From the gallery: ...' does not always appear in the page.
            return re.search('From the gallery: (.+?)</a>', page_data).group(1).strip()

        except AttributeError:
            # Get gallery name from gallery home page.
            gallery_page_data = self.request(self.root + '/G' + gallery_id).text
            return re.search('id="view-upload-title">([\s\S]+?)<', gallery_page_data).group(1).strip()
