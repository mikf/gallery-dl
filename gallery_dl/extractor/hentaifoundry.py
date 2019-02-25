# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.hentai-foundry.com/"""

from .common import Extractor, Message
from .. import text, util, exception
import requests.packages.urllib3.util.connection as u3_conn
import socket


class HentaifoundryExtractor(Extractor):
    """Base class for hentaifoundry extractors"""
    category = "hentaifoundry"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{category}_{index}_{title}.{extension}"
    archive_fmt = "{index}"
    root = "https://www.hentai-foundry.com"
    per_page = 25

    def __init__(self, match, user="", page=1):
        Extractor.__init__(self, match)
        self.page_url = ""
        self.user = user
        self.start_post = 0
        self.start_page = text.parse_int(page, 1)

    def request(*args, **kwargs):
        with disable_ipv6():
            return Extractor.request(*args, **kwargs)

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
        self.request(self.root + "/?enterAgree=1")
        return {"user": self.user}

    def get_image_pages(self):
        """Yield urls of all relevant image pages"""
        num = self.start_page

        while True:
            page = self.request("{}/page/{}".format(self.page_url, num)).text
            yield from text.extract_iter(page, 'thumbTitle"><a href="', '"')

            if 'class="pager"' not in page or 'class="last hidden"' in page:
                return
            num += 1

    def get_image_metadata(self, page_url):
        """Collect url and metadata from an image page"""
        page = self.request(text.urljoin(self.root, page_url)).text
        index = page_url.rsplit("/", 2)[1]
        title , pos = text.extract(page, '<title>', '</title>')
        _     , pos = text.extract(page, 'id="picBox"', '', pos)
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
        token = text.unquote(text.extract(
            self.session.cookies["YII_CSRF_TOKEN"], "%22", "%22")[0])
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


class HentaifoundryUserExtractor(HentaifoundryExtractor):
    """Extractor for all images of a hentai-foundry-user"""
    subcategory = "user"
    pattern = (r"(?:https?://)?(?:www\.)?hentai-foundry\.com"
               r"/(?:pictures/user/([^/]+)(?:/page/(\d+))?/?$"
               r"|user/([^/]+)/profile)")
    test = (
        ("https://www.hentai-foundry.com/pictures/user/Tenpura", {
            "url": "ebbc981a85073745e3ca64a0f2ab31fab967fc28",
            "keyword": "63ad576f87f82fa166ca4676761762f7f8496cf5",
        }),
        ("https://www.hentai-foundry.com/pictures/user/Tenpura/page/3"),
        ("https://www.hentai-foundry.com/user/Tenpura/profile"),
    )

    def __init__(self, match):
        HentaifoundryExtractor.__init__(
            self, match, match.group(1) or match.group(3), match.group(2))
        self.page_url = "{}/pictures/user/{}".format(self.root, self.user)

    def get_job_metadata(self):
        page = self.request(self.page_url + "?enterAgree=1").text
        count = text.extract(page, ">Pictures (", ")")[0]
        return {"user": self.user, "count": text.parse_int(count)}


class HentaifoundryScrapsExtractor(HentaifoundryExtractor):
    """Extractor for scrap images of a hentai-foundry-user"""
    subcategory = "scraps"
    directory_fmt = ("{category}", "{user}", "Scraps")
    pattern = (r"(?:https?://)?(?:www\.)?hentai-foundry\.com"
               r"/pictures/user/([^/]+)/scraps(?:/page/(\d+))?")
    test = (
        ("https://www.hentai-foundry.com/pictures/user/Evulchibi/scraps", {
            "url": "00a11e30b73ff2b00a1fba0014f08d49da0a68ec",
            "keyword": "410c6c900cfd23a8dd1e53dfcc97a79ea68c3359",
        }),
        ("https://www.hentai-foundry.com"
         "/pictures/user/Evulchibi/scraps/page/3"),
    )

    def __init__(self, match):
        HentaifoundryExtractor.__init__(
            self, match, match.group(1), match.group(2))
        self.page_url = "{}/pictures/user/{}/scraps".format(
            self.root, self.user)

    def get_job_metadata(self):
        page = self.request(self.page_url + "?enterAgree=1").text
        count = text.extract(page, ">Scraps (", ")")[0]
        return {"user": self.user, "count": text.parse_int(count)}


class HentaifoundryFavoriteExtractor(HentaifoundryExtractor):
    """Extractor for favorite images of a hentai-foundry-user"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "{user}", "Favorites")
    archive_fmt = "f_{user}_{index}"
    pattern = (r"(?:https?://)?(?:www\.)?hentai-foundry\.com"
               r"/user/([^/]+)/faves/pictures(?:/page/(\d+))?")
    test = (
        ("https://www.hentai-foundry.com/user/Tenpura/faves/pictures", {
            "url": "56f9ae2e89fe855e9fe1da9b81e5ec6212b0320b",
            "keyword": "2b9478725e66d46ea043fa87476bbd28546958e7",
        }),
        ("https://www.hentai-foundry.com"
         "/user/Tenpura/faves/pictures/page/3"),
    )

    def __init__(self, match):
        HentaifoundryExtractor.__init__(
            self, match, match.group(1), match.group(2))
        self.page_url = "{}/user/{}/faves/pictures".format(
            self.root, self.user)


class HentaifoundryRecentExtractor(HentaifoundryExtractor):
    """Extractor for 'Recent Pictures' on hentaifoundry.com"""
    subcategory = "recent"
    directory_fmt = ("{category}", "Recent Pictures", "{date}")
    archive_fmt = "r_{index}"
    pattern = (r"(?:https?://)?(?:www\.)?hentai-foundry\.com"
               r"/pictures/recent/(\d+-\d+-\d+)(?:/page/(\d+))?")
    test = ("http://www.hentai-foundry.com/pictures/recent/2018-09-20",)

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match, "", match.group(2))
        self.date = match.group(1)
        self.page_url = "{}/pictures/recent/{}".format(self.root, self.date)

    def get_job_metadata(self):
        self.request(self.root + "/?enterAgree=1")
        return {"date": self.date}


class HentaifoundryPopularExtractor(HentaifoundryExtractor):
    """Extractor for popular images on hentaifoundry.com"""
    subcategory = "popular"
    directory_fmt = ("{category}", "Popular Pictures")
    archive_fmt = "p_{index}"
    pattern = (r"(?:https?://)?(?:www\.)?hentai-foundry\.com"
               r"/pictures/popular(?:/page/(\d+))?")
    test = ("http://www.hentai-foundry.com/pictures/popular",)

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match, "", match.group(1))
        self.page_url = self.root + "/pictures/popular"


class HentaifoundryImageExtractor(HentaifoundryExtractor):
    """Extractor for a single image from hentaifoundry.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:www\.|pictures\.)?hentai-foundry\.com"
               r"/(?:pictures/user|[^/])/([^/]+)/(\d+)")
    test = (
        (("https://www.hentai-foundry.com"
          "/pictures/user/Tenpura/407501/shimakaze"), {
            "url": "fbf2fd74906738094e2575d2728e8dc3de18a8a3",
            "keyword": "cbb9381e6c2acce58db4adf4efc0ad7d138bddc4",
            "content": "91bf01497c39254b6dfb234a18e8f01629c77fd1",
        }),
        ("https://www.hentai-foundry.com/pictures/user/Tenpura/340853/", {
            "exception": exception.HttpError,
        }),
        ("https://pictures.hentai-foundry.com"
         "/t/Tenpura/407501/Tenpura-407501-shimakaze.png"),
    )

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match, match.group(1))
        self.index = match.group(2)

    def items(self):
        post_url = "{}/pictures/user/{}/{}/?enterAgree=1".format(
            self.root, self.user, self.index)
        url, data = self.get_image_metadata(post_url)
        data["user"] = self.user

        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data

    def skip(self, _):
        return 0


class disable_ipv6():
    """Context Manager: Reject IPv6 addresses during DNS lookup"""
    _allowed_gai_family = u3_conn.allowed_gai_family

    def __enter__(self):
        u3_conn.allowed_gai_family = lambda: socket.AF_INET

    def __exit__(self, etype, value, traceback):
        u3_conn.allowed_gai_family = disable_ipv6._allowed_gai_family
