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
    category = "hentaifoundry"
    directory_fmt = ["{category}", "{artist}"]
    filename_fmt = "{category}_{index}_{title}.{extension}"
    archive_fmt = "{index}"
    root = "https://www.hentai-foundry.com"
    per_page = 25

    def __init__(self, artist):
        Extractor.__init__(self)
        self.artist = artist
        self.artist_url = "{}/pictures/user/{}".format(self.root, self.artist)
        self.start_post = 0

    def items(self):
        data = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, data

        for page_url in util.advance(self.get_image_pages(), self.start_post):
            url, image = self.get_image_metadata(page_url)
            image.update(data)
            if not image["extension"]:
                image["extension"] = "jpg"
            yield Message.Url, url, image

    def get_image_pages(self):
        """Yield urls all image pages of one artist"""

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""

    def get_image_metadata(self, url):
        """Collect metadata for an image"""
        page = self.request(text.urljoin(self.root, url)).text
        index = url.rsplit("/", 2)[1]
        title, pos = text.extract(
            page, 'Pictures</a> &raquo; <span>', '<')
        part, pos = text.extract(
            page, '//pictures.hentai-foundry.com', '"', pos)
        data = {"index": text.parse_int(index), "title": text.unescape(title)}
        text.nameext_from_url(part, data)
        return "https://pictures.hentai-foundry.com" + part, data


class HentaifoundryUserExtractor(HentaifoundryExtractor):
    """Extractor for all images of a hentai-foundry-user"""
    subcategory = "user"
    pattern = [r"(?:https?://)?(?:www\.)?hentai-foundry\.com/"
               r"(?:pictures/user/([^/]+)(?:/(?:page/(\d+))?)?$"
               r"|user/([^/]+)/profile)"]
    test = [
        ("https://www.hentai-foundry.com/pictures/user/Tenpura", {
            "url": "ebbc981a85073745e3ca64a0f2ab31fab967fc28",
            "keyword": "f8fecc8aa89978ecf402ec221243978fe791bd54",
        }),
        ("http://www.hentai-foundry.com/user/asdq/profile", {
            "exception": exception.NotFoundError,
        }),
        ("https://www.hentai-foundry.com/pictures/user/Tenpura/page/3", None),
    ]

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match.group(1) or match.group(3))
        self.start_page = text.parse_int(match.group(2), 1)
        self._skipped = (self.start_page - 1) * self.per_page

    def skip(self, num):
        pages, posts = divmod(num, self.per_page)
        self.start_page += pages
        self.start_post += posts
        self._skipped += num
        return num

    def get_image_pages(self):
        num = self.start_page

        while True:
            url = "{}/page/{}".format(self.artist_url, num)
            page = self.request(url).text
            yield from text.extract_iter(page, 'thumbTitle"><a href="', '"')

            if 'class="pager"' not in page or 'class="last hidden"' in page:
                return
            num += 1

    def get_job_metadata(self):
        url = self.artist_url + "?enterAgree=1"
        response = self.request(url, expect=(404,))

        if response.status_code == 404:
            raise exception.NotFoundError("user")
        count = text.parse_int(text.extract(
            response.text, 'class="active" >Pictures (', ')')[0])
        if self._skipped >= count:
            raise exception.StopExtraction()

        self.set_filters()
        return {"artist": self.artist, "count": count}

    def set_filters(self):
        """Set site-internal filters to show all images"""
        token = text.extract(
            self.session.cookies["YII_CSRF_TOKEN"], "%22", "%22")[0]
        formdata = {
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
        self.request("https://www.hentai-foundry.com/site/filters",
                     method="post", data=formdata)


class HentaifoundryImageExtractor(HentaifoundryExtractor):
    """Extractor for a single image from hentaifoundry.com"""
    subcategory = "image"
    pattern = [(r"(?:https?://)?(?:www\.|pictures\.)?hentai-foundry\.com/"
                r"(?:pictures/user/([^/]+)/(\d+)"
                r"|[^/]/([^/]+)/(\d+))")]
    test = [
        (("http://www.hentai-foundry.com"
          "/pictures/user/Tenpura/407501/shimakaze"), {
            "url": "fbf2fd74906738094e2575d2728e8dc3de18a8a3",
            "keyword": "2956321893e9187edde4aeac6bed889449692e6a",
            "content": "91bf01497c39254b6dfb234a18e8f01629c77fd1",
        }),
        ("http://www.hentai-foundry.com/pictures/user/Tenpura/340853/", {
            "exception": exception.HttpError,
        }),
    ]

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match.group(1) or match.group(3))
        self.index = match.group(2) or match.group(4)

    def get_image_pages(self):
        return ("{}/{}?enterAgree=1".format(self.artist_url, self.index),)

    def get_job_metadata(self):
        return {"artist": self.artist, "index": text.parse_int(self.index)}
