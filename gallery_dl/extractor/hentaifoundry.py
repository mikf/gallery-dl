# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
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
    cookies_domain = "www.hentai-foundry.com"
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
            "index"      : text.parse_int(path.rsplit("/", 2)[1]),
            "title"      : text.unescape(extr('class="imageTitle">', '<')),
            "artist"     : text.unescape(extr('/profile">', '<')),
            "_body"      : extr(
                '<div class="boxbody"', '<div class="boxfooter"'),
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

        body = data["_body"]
        if "<object " in body:
            data["src"] = text.urljoin(self.root, text.unescape(text.extr(
                body, 'name="movie" value="', '"')))
            data["width"] = text.parse_int(text.extr(
                body, "name='width' value='", "'"))
            data["height"] = text.parse_int(text.extr(
                body, "name='height' value='", "'"))
        else:
            data["src"] = text.urljoin(self.root, text.unescape(text.extr(
                body, 'src="', '"')))
            data["width"] = text.parse_int(text.extr(body, 'width="', '"'))
            data["height"] = text.parse_int(text.extr(body, 'height="', '"'))

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

    def _request_check(self, url, **kwargs):
        self.request = self._request_original

        # check for Enter button / front page
        # and update PHPSESSID and content filters if necessary
        response = self.request(url, **kwargs)
        content = response.content
        if len(content) < 5000 and \
                b'<div id="entryButtonContainer"' in content:
            self._init_site_filters(False)
            response = self.request(url, **kwargs)
        return response

    def _init_site_filters(self, check_cookies=True):
        """Set site-internal filters to show all images"""
        if check_cookies and self.cookies.get(
                "PHPSESSID", domain=self.cookies_domain):
            self._request_original = self.request
            self.request = self._request_check
            return

        url = self.root + "/?enterAgree=1"
        self.request(url, method="HEAD")

        csrf_token = self.cookies.get(
            "YII_CSRF_TOKEN", domain=self.cookies_domain)
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
            "filter_order"    : "date_new",
            "filter_type"     : "0",
            "YII_CSRF_TOKEN"  : text.unquote(text.extr(
                csrf_token, "%22", "%22")),
        }
        self.request(url, method="POST", data=data)


class HentaifoundryUserExtractor(HentaifoundryExtractor):
    """Extractor for a hentaifoundry user profile"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/user/([^/?#]+)/profile"
    example = "https://www.hentai-foundry.com/user/USER/profile"

    def initialize(self):
        pass

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
    example = "https://www.hentai-foundry.com/pictures/user/USER"

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match)
        self.page_url = "{}/pictures/user/{}".format(self.root, self.user)


class HentaifoundryScrapsExtractor(HentaifoundryExtractor):
    """Extractor for scraps of a hentaifoundry user"""
    subcategory = "scraps"
    directory_fmt = ("{category}", "{user}", "Scraps")
    pattern = BASE_PATTERN + r"/pictures/user/([^/?#]+)/scraps"
    example = "https://www.hentai-foundry.com/pictures/user/USER/scraps"

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
    example = "https://www.hentai-foundry.com/user/USER/faves/pictures"

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match)
        self.page_url = "{}/user/{}/faves/pictures".format(
            self.root, self.user)


class HentaifoundryTagExtractor(HentaifoundryExtractor):
    """Extractor for tag searches on hentaifoundry.com"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{index}"
    pattern = BASE_PATTERN + r"/pictures/tagged/([^/?#]+)"
    example = "https://www.hentai-foundry.com/pictures/tagged/TAG"

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match)
        self.page_url = "{}/pictures/tagged/{}".format(self.root, self.user)

    def metadata(self):
        return {"search_tags": self.user}


class HentaifoundryRecentExtractor(HentaifoundryExtractor):
    """Extractor for 'Recent Pictures' on hentaifoundry.com"""
    subcategory = "recent"
    directory_fmt = ("{category}", "Recent Pictures", "{date}")
    archive_fmt = "r_{index}"
    pattern = BASE_PATTERN + r"/pictures/recent/(\d\d\d\d-\d\d-\d\d)"
    example = "https://www.hentai-foundry.com/pictures/recent/1970-01-01"

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
    example = "https://www.hentai-foundry.com/pictures/popular"

    def __init__(self, match):
        HentaifoundryExtractor.__init__(self, match)
        self.page_url = self.root + "/pictures/popular"


class HentaifoundryImageExtractor(HentaifoundryExtractor):
    """Extractor for a single image from hentaifoundry.com"""
    subcategory = "image"
    pattern = (r"(https?://)?(?:www\.|pictures\.)?hentai-foundry\.com"
               r"/(?:pictures/user|[^/?#])/([^/?#]+)/(\d+)")
    example = "https://www.hentai-foundry.com/pictures/user/USER/12345/TITLE"

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
    example = "https://www.hentai-foundry.com/stories/user/USER"

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
    example = "https://www.hentai-foundry.com/stories/user/USER/12345/TITLE"

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
