# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.hentai-foundry.com/"""

from .common import Extractor, Message
from .. import text, util, exception


class HentaifoundryExtractor(Extractor):
    """Base class for hentaifoundry extractors"""
    category = "hentaifoundry"
    directory_fmt = ["{category}", "{artist}"]
    filename_fmt = "{category}_{index}_{title}.{extension}"
    archive_fmt = "{index}"
    root = "https://www.hentai-foundry.com"
    per_page = 25

    def __init__(self, artist, needle=""):
        Extractor.__init__(self)
        self.artist = artist
        self.needle = needle
        self.artist_url = "{}/pictures/user/{}".format(self.root, artist)
        self.start_page = 1
        self.start_post = 0

    def items(self):
        data = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, data

        self.set_filters()
        for page_url in util.advance(self.get_image_pages(), self.start_post):
            url, image = self.get_image_metadata(page_url)
            image.update(data)
            yield Message.Url, url, image

    def skip(self, num):
        pages, posts = divmod(num, self.per_page)
        self.start_page += pages
        self.start_post += posts
        return num

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        page = self.request(self.artist_url + "?enterAgree=1").text
        needle = ' >{} ('.format(self.needle)
        count = text.parse_int(text.extract(page, needle, ')')[0])
        return {"artist": self.artist, "count": count}

    def get_image_pages(self):
        """Yield urls all image pages of one artist"""

    def get_image_metadata(self, url):
        """Collect metadata for an image"""
        page = self.request(text.urljoin(self.root, url)).text
        index = url.rsplit("/", 2)[1]
        title , pos = text.extract(page, '<title>', '</title>')
        width , pos = text.extract(page, 'width="', '"', pos)
        height, pos = text.extract(page, 'height="', '"', pos)
        url   , pos = text.extract(page, 'src="', '"', pos)

        title, _, artist = title.rpartition(" - ")[0].rpartition(" by ")

        data = text.nameext_from_url(url, {
            "title": text.unescape(title),
            "artist": text.unescape(artist),
            "index": text.parse_int(index),
            "width": text.parse_int(width),
            "height": text.parse_int(height),
        })
        if not data["extension"]:
            data["extension"] = "jpg"
        return text.urljoin(self.root, url), data

    def set_filters(self):
        """Set site-internal filters to show all images"""
        token = text.extract(
            self.session.cookies["YII_CSRF_TOKEN"], "%22", "%22")[0]
        data = {
            "YII_CSRF_TOKEN": token,
            "rating_nudity": 3,
            "rating_violence": 3,
            "rating_profanity": 3,
            "rating_racism": 3,
            "rating_sex": 3,
            "rating_spoilers": 3,
            "rating_yaoi": 1,
            "rating_yuri": 1,
            "rating_teen": 1,
            "rating_guro": 1,
            "rating_furry": 1,
            "rating_beast": 1,
            "rating_male": 1,
            "rating_female": 1,
            "rating_futa": 1,
            "rating_other": 1,
            "rating_scat": 1,
            "rating_incest": 1,
            "rating_rape": 1,
            "filter_media": "A",
            "filter_order": "date_new",
            "filter_type": 0,
        }
        url = self.root + "/site/filters"
        self.request(url, method="POST", data=data)

    def _pagination(self, url):
        num = self.start_page

        while True:
            page = self.request("{}/page/{}".format(url, num)).text
            yield from text.extract_iter(page, 'thumbTitle"><a href="', '"')

            if 'class="pager"' not in page or 'class="last hidden"' in page:
                return
            num += 1


class HentaifoundryUserExtractor(HentaifoundryExtractor):
    """Extractor for all images of a hentai-foundry-user"""
    subcategory = "user"
    pattern = [r"(?:https?://)?(?:www\.)?hentai-foundry\.com"
               r"/(?:pictures/user/([^/]+)(?:/(?:page/(\d+))?)?$"
               r"|user/([^/]+)/profile)"]
    test = [
        ("https://www.hentai-foundry.com/pictures/user/Tenpura", {
            "url": "ebbc981a85073745e3ca64a0f2ab31fab967fc28",
            "keyword": "98dc5e3856a38243ad4be3e428dc6a069243bc13",
        }),
        ("https://www.hentai-foundry.com/pictures/user/Tenpura/page/3", None),
        ("https://www.hentai-foundry.com/user/Tenpura/profile", None),
    ]

    def __init__(self, match):
        HentaifoundryExtractor.__init__(
            self, match.group(1) or match.group(3), "Pictures")
        self.start_page = text.parse_int(match.group(2), 1)

    def get_image_pages(self):
        return self._pagination(self.artist_url)


class HentaifoundryScrapsExtractor(HentaifoundryExtractor):
    """Extractor for scrap images of a hentai-foundry-user"""
    subcategory = "scraps"
    directory_fmt = ["{category}", "{artist}", "Scraps"]
    pattern = [r"(?:https?://)?(?:www\.)?hentai-foundry\.com"
               r"/pictures/user/([^/]+)/scraps(?:/(?:page/(\d+))?)?$"]
    test = [
        ("https://www.hentai-foundry.com/pictures/user/Evulchibi/scraps", {
            "url": "00a11e30b73ff2b00a1fba0014f08d49da0a68ec",
            "keyword": "e294a72ab7be53a716eab92d8c97f82d6e76693c",
        }),
        (("https://www.hentai-foundry.com"
          "/pictures/user/Evulchibi/scraps/page/3"), None),
    ]

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match.group(1), "Scraps")
        self.start_page = text.parse_int(match.group(2), 1)

    def get_image_pages(self):
        return self._pagination(self.artist_url + "/scraps")


class HentaifoundryImageExtractor(HentaifoundryExtractor):
    """Extractor for a single image from hentaifoundry.com"""
    subcategory = "image"
    pattern = [r"(?:https?://)?(?:www\.|pictures\.)?hentai-foundry\.com"
               r"/(?:pictures/user|[^/])/([^/]+)/(\d+)"]
    test = [
        (("https://www.hentai-foundry.com"
          "/pictures/user/Tenpura/407501/shimakaze"), {
            "url": "fbf2fd74906738094e2575d2728e8dc3de18a8a3",
            "keyword": "e6ae60151ae3c17a22b3d61574ff5a883e577573",
            "content": "91bf01497c39254b6dfb234a18e8f01629c77fd1",
        }),
        ("https://www.hentai-foundry.com/pictures/user/Tenpura/340853/", {
            "exception": exception.HttpError,
        }),
        (("https://pictures.hentai-foundry.com"
          "/t/Tenpura/407501/Tenpura-407501-shimakaze.png"), None),
    ]

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match.group(1))
        self.index = match.group(2)

    def items(self):
        url, data = self.get_image_metadata(
            "{}/{}/?enterAgree=1".format(self.artist_url, self.index))
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data

    def skip(self, _):
        return 0
