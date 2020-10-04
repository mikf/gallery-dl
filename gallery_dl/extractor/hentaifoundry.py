# -*- coding: utf-8 -*-

# Copyright 2015-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.hentai-foundry.com/"""

from .common import Extractor, Message
from .. import text, util, exception


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

    def items(self):
        data = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, data

        self.set_filters()
        for page_url in util.advance(self._pagination(), self.start_post):
            image = self.get_image_metadata(page_url)
            image.update(data)
            yield Message.Url, image["src"], image

    def skip(self, num):
        pages, posts = divmod(num, self.per_page)
        self.start_page += pages
        self.start_post += posts
        return num

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        self.request(self.root + "/?enterAgree=1")
        return {"user": self.user}

    def _pagination(self, begin='thumbTitle"><a href="', end='"'):
        num = self.start_page

        while True:
            page = self.request("{}/page/{}".format(self.page_url, num)).text
            yield from text.extract_iter(page, begin, end)

            if 'class="pager"' not in page or 'class="last hidden"' in page:
                return
            num += 1

    def get_image_metadata(self, path):
        """Collect url and metadata from an image page"""
        url = text.urljoin(self.root, path)
        page = self.request(url).text
        extr = text.extract_from(page, page.index('id="picBox"'))

        data = {
            "title"      : text.unescape(extr('class="imageTitle">', '<')),
            "artist"     : text.unescape(extr('/profile">', '<')),
            "width"      : text.parse_int(extr('width="', '"')),
            "height"     : text.parse_int(extr('height="', '"')),
            "index"      : text.parse_int(path.rsplit("/", 2)[1]),
            "src"        : "https:" + text.unescape(extr('src="', '"')),
            "description": text.unescape(text.remove_html(extr(
                '>Description</div>', '</section>')
                .replace("\r\n", "\n"), "", "")),
            "ratings"    : [text.unescape(r) for r in text.extract_iter(extr(
                "class='ratings_box'", "</div>"), "title='", "'")],
            "media"      : text.unescape(extr("Media</b></td>\t\t<td>", "<")),
            "date"       : text.parse_datetime(extr("datetime='", "'")),
            "views"      : text.parse_int(extr("Views</b></td>\t\t<td>", "<")),
            "tags"       : text.split_html(extr(
                "<td><b>Keywords</b></td>", "</tr>"))[::2],
            "score"      : text.parse_int(extr('Score</b></td>\t\t<td>', '<')),
        }

        return text.nameext_from_url(data["src"], data)

    def get_story_metadata(self, html):
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
               r"/user/([^/]+)/profile")
    test = ("https://www.hentai-foundry.com/user/Tenpura/profile",)

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match, match.group(1))

    def items(self):
        user = "/user/" + self.user
        return self._dispatch_extractors((
            (HentaifoundryPicturesExtractor ,
                self.root + "/pictures" + user),
            (HentaifoundryScrapsExtractor,
                self.root + "/pictures" + user + "/scraps"),
            (HentaifoundryStoriesExtractor,
                self.root + "/stories" + user),
            (HentaifoundryFavoriteExtractor,
                self.root + user + "/faves/pictures"),
        ), ("pictures",))


class HentaifoundryPicturesExtractor(HentaifoundryExtractor):
    """Extractor for all pictures of a hentaifoundry user"""
    subcategory = "pictures"
    pattern = (r"(?:https?://)?(?:www\.)?hentai-foundry\.com"
               r"/pictures/user/([^/]+)(?:/page/(\d+))?/?$")
    test = (
        ("https://www.hentai-foundry.com/pictures/user/Tenpura", {
            "url": "ebbc981a85073745e3ca64a0f2ab31fab967fc28",
        }),
        ("https://www.hentai-foundry.com/pictures/user/Tenpura/page/3"),
    )

    def __init__(self, match):
        HentaifoundryExtractor.__init__(
            self, match, match.group(1), match.group(2))
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
            "url": "7cd9c6ec6258c4ab8c44991f7731be82337492a7",
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
    test = ("http://www.hentai-foundry.com/pictures/recent/2018-09-20", {
        "pattern": r"https://pictures.hentai-foundry.com/[^/]/[^/]+/\d+/",
        "range": "20-30",
    })

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
    test = ("http://www.hentai-foundry.com/pictures/popular", {
        "pattern": r"https://pictures.hentai-foundry.com/[^/]/[^/]+/\d+/",
        "range": "20-30",
    })

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
                "tags"   : ["kancolle", "kantai", "collection", "shimakaze"],
                "title"  : "shimakaze",
                "user"   : "Tenpura",
                "views"  : int,
                "width"  : 495,
            },
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
        data = self.get_image_metadata(post_url)
        data["user"] = self.user

        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, data["src"], data

    def skip(self, _):
        return 0


class HentaifoundryStoriesExtractor(HentaifoundryExtractor):
    """Extractor for stories of a hentai-foundry user"""
    subcategory = "stories"
    pattern = (r"(?:https?://)?(?:www\.)?hentai-foundry\.com"
               r"/stories/user/([^/]+)(?:/page/(\d+))?/?$")
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

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match, match.group(1))
        self.page_url = "{}/stories/user/{}".format(self.root, self.user)

    def items(self):
        self.get_job_metadata()
        self.set_filters()
        stories = self._pagination('<div class="storyRow">', '</tr></table>')
        for story_html in util.advance(stories, self.start_post):
            story = self.get_story_metadata(story_html)
            yield Message.Directory, story
            yield Message.Url, story["src"], story


class HentaifoundryStoryExtractor(HentaifoundryExtractor):
    """Extractor for a hentaifoundry story"""
    subcategory = "story"
    pattern = (r"(?:https?://)?(?:www\.)?hentai-foundry\.com"
               r"/stories/user/([^/]+)/(\d+)")
    test = (("https://www.hentai-foundry.com/stories/user/SnowWolf35"
             "/26416/Overwatch-High-Chapter-Voting-Location"), {
        "url": "5a67cfa8c3bf7634c8af8485dd07c1ea74ee0ae8",
        "keyword": {"title": "Overwatch High Chapter Voting Location"},
    })

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match, match.group(1))
        self.index = match.group(2)

    def items(self):
        story_url = "{}/stories/user/{}/{}/x?enterAgree=1".format(
            self.root, self.user, self.index)
        page = self.request(story_url).text
        story = self.get_story_metadata(page)
        yield Message.Directory, story
        yield Message.Url, story["src"], story

    def skip(self, _):
        return 0
