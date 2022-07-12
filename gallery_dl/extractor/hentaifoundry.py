# -*- coding: utf-8 -*-

# Copyright 2015-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.hentai-foundry.com/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(https?://)?(?:www\.)?hentai-foundry\.com"


class HentaifoundryExtractor(Extractor):
    """Base class for hentaifoundry extractors"""
    category = "hentaifoundry"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{category}_{index}_{title}.{extension}"
    archive_fmt = "{index}"
    cookiedomain = "www.hentai-foundry.com"
    root = "https://www.hentai-foundry.com"
    per_page = 25

    def __init__(self, match):
        self.root = (match.group(1) or "https://") + "www.hentai-foundry.com"
        self.user = match.group(2)
        Extractor.__init__(self, match)
        self.page_url = ""
        self.start_post = 0
        self.start_page = 1

    def items(self):
        self._init_site_filters()
        data = self.metadata()

        for post_url in util.advance(self.posts(), self.start_post):
            image = self._parse_post(post_url)
            image.update(data)
            yield Message.Directory, image
            yield Message.Url, image["src"], image

    def skip(self, num):
        pages, posts = divmod(num, self.per_page)
        self.start_page += pages
        self.start_post += posts
        return num

    def metadata(self):
        return {"user": self.user}

    def posts(self):
        return self._pagination(self.page_url)

    def _pagination(self, url, begin='thumbTitle"><a href="', end='"'):
        num = self.start_page

        while True:
            page = self.request("{}/page/{}".format(url, num)).text
            yield from text.extract_iter(page, begin, end)

            if 'class="pager"' not in page or 'class="last hidden"' in page:
                return
            num += 1

    def _parse_post(self, path):
        """Collect url and metadata from an image post"""
        url = text.urljoin(self.root, path)
        page = self.request(url).text
        extr = text.extract_from(page, page.index('id="picBox"'))

        data = {
            "title"      : text.unescape(extr('class="imageTitle">', '<')),
            "artist"     : text.unescape(extr('/profile">', '<')),
            "width"      : text.parse_int(extr('width="', '"')),
            "height"     : text.parse_int(extr('height="', '"')),
            "index"      : text.parse_int(path.rsplit("/", 2)[1]),
            "src"        : text.urljoin(self.root, text.unescape(extr(
                'src="', '"'))),
            "description": text.unescape(text.remove_html(extr(
                '>Description</div>', '</section>')
                .replace("\r\n", "\n"), "", "")),
            "ratings"    : [text.unescape(r) for r in text.extract_iter(extr(
                "class='ratings_box'", "</div>"), "title='", "'")],
            "date"       : text.parse_datetime(extr("datetime='", "'")),
            "views"      : text.parse_int(extr(">Views</span>", "<")),
            "score"      : text.parse_int(extr(">Vote Score</span>", "<")),
            "media"      : text.unescape(extr(">Media</span>", "<").strip()),
            "tags"       : text.split_html(extr(
                ">Tags </span>", "</div>")),
        }

        return text.nameext_from_url(data["src"], data)

    def _parse_story(self, html):
        """Collect url and metadata for a story"""
        extr = text.extract_from(html)
        data = {
            "user"    : self.user,
            "title"   : text.unescape(extr(
                "<div class='titlebar'>", "</a>").rpartition(">")[2]),
            "author"  : text.unescape(extr('alt="', '"')),
            "date"    : text.parse_datetime(extr(
                ">Updated<", "</span>").rpartition(">")[2], "%B %d, %Y"),
            "status"  : extr("class='indent'>", "<"),
        }

        for c in ("Chapters", "Words", "Comments", "Views", "Rating"):
            data[c.lower()] = text.parse_int(extr(
                ">" + c + ":</span>", "<").replace(",", ""))

        data["description"] = text.unescape(extr(
            "class='storyDescript'>", "<div"))
        path = extr('href="', '"')
        data["src"] = self.root + path
        data["index"] = text.parse_int(path.rsplit("/", 2)[1])
        data["ratings"] = [text.unescape(r) for r in text.extract_iter(extr(
            "class='ratings_box'", "</div>"), "title='", "'")]

        return text.nameext_from_url(data["src"], data)

    def _init_site_filters(self):
        """Set site-internal filters to show all images"""
        url = self.root + "/?enterAgree=1"
        self.request(url, method="HEAD")

        csrf_token = self.session.cookies.get(
            "YII_CSRF_TOKEN", domain=self.cookiedomain)
        if not csrf_token:
            self.log.warning("Unable to update site content filters")
            return

        url = self.root + "/site/filters"
        data = {
            "rating_nudity"   : "3",
            "rating_violence" : "3",
            "rating_profanity": "3",
            "rating_racism"   : "3",
            "rating_sex"      : "3",
            "rating_spoilers" : "3",
            "rating_yaoi"     : "1",
            "rating_yuri"     : "1",
            "rating_teen"     : "1",
            "rating_guro"     : "1",
            "rating_furry"    : "1",
            "rating_beast"    : "1",
            "rating_male"     : "1",
            "rating_female"   : "1",
            "rating_futa"     : "1",
            "rating_other"    : "1",
            "rating_scat"     : "1",
            "rating_incest"   : "1",
            "rating_rape"     : "1",
            "filter_media"    : "A",
            "filter_order"    : "date_new",
            "filter_type"     : "0",
            "YII_CSRF_TOKEN"  : text.unquote(text.extract(
                csrf_token, "%22", "%22")[0]),
        }
        self.request(url, method="POST", data=data)


class HentaifoundryUserExtractor(HentaifoundryExtractor):
    """Extractor for a hentaifoundry user profile"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/user/([^/?#]+)/profile"
    test = ("https://www.hentai-foundry.com/user/Tenpura/profile",)

    def items(self):
        root = self.root
        user = "/user/" + self.user
        return self._dispatch_extractors((
            (HentaifoundryPicturesExtractor ,
                root + "/pictures" + user),
            (HentaifoundryScrapsExtractor,
                root + "/pictures" + user + "/scraps"),
            (HentaifoundryStoriesExtractor,
                root + "/stories" + user),
            (HentaifoundryFavoriteExtractor,
                root + user + "/faves/pictures"),
        ), ("pictures",))


class HentaifoundryPicturesExtractor(HentaifoundryExtractor):
    """Extractor for all pictures of a hentaifoundry user"""
    subcategory = "pictures"
    pattern = BASE_PATTERN + r"/pictures/user/([^/?#]+)(?:/page/(\d+))?/?$"
    test = (
        ("https://www.hentai-foundry.com/pictures/user/Tenpura", {
            "url": "ebbc981a85073745e3ca64a0f2ab31fab967fc28",
        }),
        ("https://www.hentai-foundry.com/pictures/user/Tenpura/page/3"),
    )

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match)
        self.page_url = "{}/pictures/user/{}".format(self.root, self.user)


class HentaifoundryScrapsExtractor(HentaifoundryExtractor):
    """Extractor for scraps of a hentaifoundry user"""
    subcategory = "scraps"
    directory_fmt = ("{category}", "{user}", "Scraps")
    pattern = BASE_PATTERN + r"/pictures/user/([^/?#]+)/scraps"
    test = (
        ("https://www.hentai-foundry.com/pictures/user/Evulchibi/scraps", {
            "url": "7cd9c6ec6258c4ab8c44991f7731be82337492a7",
        }),
        ("https://www.hentai-foundry.com"
         "/pictures/user/Evulchibi/scraps/page/3"),
    )

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match)
        self.page_url = "{}/pictures/user/{}/scraps".format(
            self.root, self.user)


class HentaifoundryFavoriteExtractor(HentaifoundryExtractor):
    """Extractor for favorite images of a hentaifoundry user"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "{user}", "Favorites")
    archive_fmt = "f_{user}_{index}"
    pattern = BASE_PATTERN + r"/user/([^/?#]+)/faves/pictures"
    test = (
        ("https://www.hentai-foundry.com/user/Tenpura/faves/pictures", {
            "url": "56f9ae2e89fe855e9fe1da9b81e5ec6212b0320b",
        }),
        ("https://www.hentai-foundry.com"
         "/user/Tenpura/faves/pictures/page/3"),
    )

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match)
        self.page_url = "{}/user/{}/faves/pictures".format(
            self.root, self.user)


class HentaifoundryRecentExtractor(HentaifoundryExtractor):
    """Extractor for 'Recent Pictures' on hentaifoundry.com"""
    subcategory = "recent"
    directory_fmt = ("{category}", "Recent Pictures", "{date}")
    archive_fmt = "r_{index}"
    pattern = BASE_PATTERN + r"/pictures/recent/(\d\d\d\d-\d\d-\d\d)"
    test = ("https://www.hentai-foundry.com/pictures/recent/2018-09-20", {
        "pattern": r"https://pictures.hentai-foundry.com/[^/]/[^/?#]+/\d+/",
        "range": "20-30",
    })

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match)
        self.page_url = "{}/pictures/recent/{}".format(self.root, self.user)

    def metadata(self):
        return {"date": self.user}


class HentaifoundryPopularExtractor(HentaifoundryExtractor):
    """Extractor for popular images on hentaifoundry.com"""
    subcategory = "popular"
    directory_fmt = ("{category}", "Popular Pictures")
    archive_fmt = "p_{index}"
    pattern = BASE_PATTERN + r"/pictures/popular()"
    test = ("https://www.hentai-foundry.com/pictures/popular", {
        "pattern": r"https://pictures.hentai-foundry.com/[^/]/[^/?#]+/\d+/",
        "range": "20-30",
    })

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match)
        self.page_url = self.root + "/pictures/popular"


class HentaifoundryImageExtractor(HentaifoundryExtractor):
    """Extractor for a single image from hentaifoundry.com"""
    subcategory = "image"
    pattern = (r"(https?://)?(?:www\.|pictures\.)?hentai-foundry\.com"
               r"/(?:pictures/user|[^/?#])/([^/?#]+)/(\d+)")
    test = (
        (("https://www.hentai-foundry.com"
          "/pictures/user/Tenpura/407501/shimakaze"), {
            "url": "fbf2fd74906738094e2575d2728e8dc3de18a8a3",
            "content": "91bf01497c39254b6dfb234a18e8f01629c77fd1",
            "keyword": {
                "artist" : "Tenpura",
                "date"   : "dt:2016-02-22 14:41:19",
                "description": "Thank you!",
                "height" : 700,
                "index"  : 407501,
                "media"  : "Other digital art",
                "ratings": ["Sexual content", "Contains female nudity"],
                "score"  : int,
                "tags"   : ["collection", "kancolle", "kantai", "shimakaze"],
                "title"  : "shimakaze",
                "user"   : "Tenpura",
                "views"  : int,
                "width"  : 495,
            },
        }),
        ("http://www.hentai-foundry.com/pictures/user/Tenpura/407501/", {
            "pattern": "http://pictures.hentai-foundry.com/t/Tenpura/407501/",
        }),
        ("https://www.hentai-foundry.com/pictures/user/Tenpura/407501/"),
        ("https://pictures.hentai-foundry.com"
         "/t/Tenpura/407501/Tenpura-407501-shimakaze.png"),
    )
    skip = Extractor.skip

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match)
        self.index = match.group(3)

    def items(self):
        post_url = "{}/pictures/user/{}/{}/?enterAgree=1".format(
            self.root, self.user, self.index)
        image = self._parse_post(post_url)
        image["user"] = self.user
        yield Message.Directory, image
        yield Message.Url, image["src"], image


class HentaifoundryStoriesExtractor(HentaifoundryExtractor):
    """Extractor for stories of a hentaifoundry user"""
    subcategory = "stories"
    archive_fmt = "s_{index}"
    pattern = BASE_PATTERN + r"/stories/user/([^/?#]+)(?:/page/(\d+))?/?$"
    test = ("https://www.hentai-foundry.com/stories/user/SnowWolf35", {
        "count": ">= 35",
        "keyword": {
            "author"     : "SnowWolf35",
            "chapters"   : int,
            "comments"   : int,
            "date"       : "type:datetime",
            "description": str,
            "index"      : int,
            "rating"     : int,
            "ratings"    : list,
            "status"     : "re:(Inc|C)omplete",
            "title"      : str,
            "user"       : "SnowWolf35",
            "views"      : int,
            "words"      : int,
        },
    })

    def items(self):
        self._init_site_filters()
        for story_html in util.advance(self.stories(), self.start_post):
            story = self._parse_story(story_html)
            yield Message.Directory, story
            yield Message.Url, story["src"], story

    def stories(self):
        url = "{}/stories/user/{}".format(self.root, self.user)
        return self._pagination(url, '<div class="storyRow">', '</tr></table>')


class HentaifoundryStoryExtractor(HentaifoundryExtractor):
    """Extractor for a hentaifoundry story"""
    subcategory = "story"
    archive_fmt = "s_{index}"
    pattern = BASE_PATTERN + r"/stories/user/([^/?#]+)/(\d+)"
    test = (("https://www.hentai-foundry.com/stories/user/SnowWolf35"
             "/26416/Overwatch-High-Chapter-Voting-Location"), {
        "url": "5a67cfa8c3bf7634c8af8485dd07c1ea74ee0ae8",
        "keyword": {"title": "Overwatch High Chapter Voting Location"},
    })
    skip = Extractor.skip

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match)
        self.index = match.group(3)

    def items(self):
        story_url = "{}/stories/user/{}/{}/x?enterAgree=1".format(
            self.root, self.user, self.index)
        story = self._parse_story(self.request(story_url).text)
        yield Message.Directory, story
        yield Message.Url, story["src"], story
