# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://motherless.com/"""

from .common import Extractor, Message
from .. import text
import re
from datetime import datetime, timedelta, timezone
from html import unescape

ROOT_URL_PATTERN = r"(?:https?://)?motherless\.com"


class MotherlessExtractor(Extractor):
    """Base class for motherless extractors"""

    category = "motherless"
    root = "https://motherless.com"
    filename_fmt = "{id} {title}.{extension}"


class MotherlessMediaExtractor(MotherlessExtractor):
    """Extractor for a single image/video from motherless.com"""

    pattern = ROOT_URL_PATTERN + "/((?!GV|GI|G)[A-Z0-9]+)$"
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
            id = get_image_id(media_url)

        except AttributeError:
            # No image, find video url.
            self.subcategory = "video"

            video_url_search = re.search("__fileurl = '(.+)'", self.page_data)
            extension = "mp4"
            media_url = video_url_search.group(1)
            id = get_video_id(media_url)

        data = {
            "url": self.url,
            "title": get_media_title(self.page_data),
            "id": id,
            "filename": id,
            "extension": extension,
            "date": get_media_date(self.page_data),
            "uploader": get_media_uploader(self.page_data),
            "tags": get_media_tags(self.page_data)}

        return media_url, data


class MotherlessMediaInGalleryExtractor(MotherlessMediaExtractor):
    """Extractor for a single image/video from a gallery from motherless.com"""

    directory_fmt = ("{category}", "{gallery_id} {gallery_title}")
    pattern = ROOT_URL_PATTERN + "/(?:GI?)([A-Z0-9]+)/([A-Z0-9]+)"
    example = "https://motherless.com/GABC123/DEF456"

    def get_image(self):
        media_url, data =  super().get_image()
        data['gallery_id'] = re.match(self.pattern, self.url).group(1)
        data['gallery_title'] = self.get_gallery_name(data['gallery_id'])
        data['title'] = get_media_title(self.page_data)
        return media_url, data

    def get_gallery_name(self, gallery_id):
        try:
            # 'From the gallery: ...' does not always appear in the page.
            return unescape(
                re.search('From the gallery: (.+?)</a>', self.page_data).group(1).strip())
        except AttributeError:
            # Get gallery name from gallery home page.
            gallery_page_data = self.request(f"{self.root}/G{gallery_id}").text
            return get_gallery_name_from_homepage(gallery_page_data)


class MotherlessGalleryImagesExtractor(MotherlessExtractor):
    """Extractor for all images in a gallery from motherless.com"""

    subcategory = "image gallery"
    directory_fmt = ("{category}", "{gallery_id} {gallery_title}")
    pattern = ROOT_URL_PATTERN + "/GI([A-Z0-9]+)$"
    example = "https://motherless.com/GIABC123"

    def items(self):
        self.gallery_id = re.match(self.pattern, self.url).group(1)

        page = self.request(f"{self.root}/G{self.gallery_id}").text
        data = {
            "gallery_id" : self.gallery_id, 
            "gallery_title": get_gallery_name_from_homepage(page), 
            "uploader": get_gallery_uploader(page),
            "count": get_gallery_image_count(page)}

        yield Message.Directory, data

        for id, url, extension, title, num in get_images(self):
            data |= {
                "id": id,
                "filename": id,
                "extension": extension,
                "title": title,
                "num": num}

            yield Message.Url, url, data


class MotherlessGalleryVideosExtractor(MotherlessExtractor):
    """Extractor for all videos in a gallery from motherless.com"""

    subcategory = "video gallery"
    directory_fmt = ("{category}", "{gallery_id} {gallery_title}")
    pattern = ROOT_URL_PATTERN + "/GV([A-Z0-9]+)$"
    example = "https://motherless.com/GVABC123"

    def items(self):
        self.gallery_id = re.match(self.pattern, self.url).group(1)
        page = self.request(f"{self.root}/G{self.gallery_id}").text
        data = {
            "gallery_id" : self.gallery_id, 
            "gallery_title": get_gallery_name_from_homepage(page),
            "uploader": get_gallery_uploader(page),
            "count": get_gallery_video_count(page)}

        yield Message.Directory, data

        for id, url, title, num in get_videos(self):
            data |= {
                "id": id,
                "filename": id,
                "extension": "mp4",
                "title": title,
                "num": num}

            yield Message.Url, url, data


class MotherlessGalleryExtractor(MotherlessExtractor):
    """Extractor for all images and videos in a gallery from motherless.com"""

    subcategory = "gallery"
    directory_fmt = ("{category}", "{gallery_id} {gallery_title}")
    pattern = ROOT_URL_PATTERN + "/G([A-Z0-9]+)$"
    example = "https://motherless.com/GABC123"

    def items(self):
        self.gallery_id = re.match(self.pattern, self.url).group(1)
        page = self.request(f"{self.root}/G{self.gallery_id}").text
        data = {
            "gallery_id" : self.gallery_id, 
            "gallery_title": get_gallery_name_from_homepage(page), 
            "uploader": get_gallery_uploader(page),
            "count": get_gallery_image_count(page) + get_gallery_video_count(page)}
        
        yield Message.Directory, data

        for id, url, extension, title, num in get_images(self):
            data |= {
                "id": id,
                "filename": id,
                "extension": extension,
                "title": title,
                "num": num}

            yield Message.Url, url, data

        for id, url, title, num in get_videos(self):
            data |= {
                "id": id,
                "filename": id,
                "extension": "mp4",
                "title": title,
                "num": num}

            yield Message.Url, url, data


# Url extractors.

def get_images(extractor):
    n = 1
    total_count = 0

    while True:
        page = extractor.request(f"{extractor.root}/GI{extractor.gallery_id}?page={n}").text
        page_count = 0

        for result in re.finditer(f' src="https:\/\/cdn5-thumbs\.motherlessmedia\.com\/thumbs\/([A-Z0-9]+?)\.(jpg|gif)"[\s\S]+?alt="(.+)"', page):
            id = result.group(1)
            url = f"https://cdn5-images.motherlessmedia.com/images/{id}.jpg"
            extension = result.group(2)
            title = result.group(3)
            page_count += 1

            yield id, url, extension, title, total_count + page_count

        if page_count == 0:
            return

        total_count += page_count
        n += 1

def get_videos(extractor):
    n = 1
    total_count = 0

    while True:
        page = extractor.request(f"{extractor.root}/GV{extractor.gallery_id}?page={n}").text
        page_count = 0

        for result in re.finditer(f'thumbs\/([A-Z0-9]+?)-strip\.jpg" alt="(.+)"', page):
            id = result.group(1)
            url = f"https://cdn5-videos.motherlessmedia.com/videos/{id}.mp4"
            title = result.group(2)
            page_count += 1

            yield id, url, title, total_count + page_count

        if page_count == 0:
            return

        total_count += page_count
        n += 1

# Metadata extractors.

def get_media_tags(page_data):
    try:
        tags_html = re.search('<div class="media-meta-tags">([\S\s]+?)</div>', page_data).group(1)
    except AttributeError:
        # No tags found.
        return []

    tags = text.split_html(tags_html)
    for i, tag in enumerate(tags):
        tags[i] = tag.replace('#', '')

    return tags

def get_media_title(page_data):
    title = re.search('<div class="media-meta-title">([\S\s]+?)</div>', page_data).group(1)
    return unescape(text.remove_html(title))

def get_media_date(page_data):
    # Find date uploaded and convert to ISO 8601.
    try:
        # Find 'DD Mon YYYY' format.
        date = re.search('<span class="count">(\d{1,2}\s+\w+\s+\d{4})</span>', page_data).group(1)
        return text.parse_datetime(date, "%d  %b  %Y").isoformat()

    except AttributeError:
        # Find 'nd ago' format.
        days_ago = int(re.search('<span class="count">(\d+)\s*d\s*ago</span>', page_data).group(1))
        return (datetime.now(timezone.utc) - timedelta(days=days_ago)).replace(hour=0, minute=0, second=0, microsecond=0)

def get_media_uploader(page_data):
    username_html = re.search('class="username">\s+(.+[^\s])\s+<\/span>', page_data).group(1)
    return text.remove_html(username_html)

def get_image_id(image_url):
    return text.extract(image_url, 'images/', '.')[0]

def get_video_id(video_url):
    video_id = text.extract(video_url, 'videos/', '.')[0]

    if '-' in video_id:
        return text.extract(video_id, '', '-')[0]
    return video_id

def get_gallery_name_from_homepage(page_data):
    return unescape(re.search('<title>(.+) \|', page_data).group(1))

def get_gallery_uploader(page_data):
        return re.search('gallery-member-username">[\s\S]+?<a href="/m/(.+?)"', page_data).group(1)

def get_gallery_image_count(page_data):
    try:
        return int(re.search('Images \(([0-9,]+)\)', page_data).group(1).replace(',', ''))
    except AttributeError:
        # No images found.
        return 0

def get_gallery_video_count(page_data):
    try:
        return int(re.search('Videos \(([0-9,]+)\)', page_data).group(1).replace(',', ''))
    except AttributeError:
        # No images found.
        return 0
