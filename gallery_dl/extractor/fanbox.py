# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.fanbox.cc/"""

import re
from .common import Extractor, Message
from .. import text


BASE_PATTERN = (
    r"(?:https?://)?(?:"
    r"(?!www\.)([\w-]+)\.fanbox\.cc|"
    r"(?:www\.)?fanbox\.cc/@([\w-]+))"
)


class FanboxExtractor(Extractor):
    """Base class for Fanbox extractors"""
    category = "fanbox"
    root = "https://www.fanbox.cc"
    directory_fmt = ("{category}", "{creatorId}")
    filename_fmt = "{id}_{num}.{extension}"
    archive_fmt = "{id}_{num}"
    _warning = True

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.embeds = self.config("embeds", True)

    def items(self):

        if self._warning:
            if not self._check_cookies(("FANBOXSESSID",)):
                self.log.warning("no 'FANBOXSESSID' cookie set")
            FanboxExtractor._warning = False

        for content_body, post in self.posts():
            yield Message.Directory, post
            yield from self._get_urls_from_post(content_body, post)

    def posts(self):
        """Return all relevant post objects"""

    def _pagination(self, url):
        headers = {"Origin": self.root}

        while url:
            url = text.ensure_http_scheme(url)
            body = self.request(url, headers=headers).json()["body"]
            for item in body["items"]:
                yield self._get_post_data(item["id"])

            url = body["nextUrl"]

    def _get_post_data(self, post_id):
        """Fetch and process post data"""
        headers = {"Origin": self.root}
        url = "https://api.fanbox.cc/post.info?postId="+post_id
        post = self.request(url, headers=headers).json()["body"]

        content_body = post.pop("body", None)
        if content_body:
            if "html" in content_body:
                post["html"] = content_body["html"]
            if post["type"] == "article":
                post["articleBody"] = content_body.copy()
            if "blocks" in content_body:
                content = []
                append = content.append
                for block in content_body["blocks"]:
                    if "text" in block:
                        append(block["text"])
                    if "links" in block:
                        for link in block["links"]:
                            append(link["url"])
                post["content"] = "\n".join(content)

        post["date"] = text.parse_datetime(post["publishedDatetime"])
        post["text"] = content_body.get("text") if content_body else None
        post["isCoverImage"] = False

        return content_body, post

    def _get_urls_from_post(self, content_body, post):
        num = 0
        cover_image = post.get("coverImageUrl")
        if cover_image:
            cover_image = re.sub("/c/[0-9a-z_]+", "", cover_image)
            final_post = post.copy()
            final_post["isCoverImage"] = True
            final_post["fileUrl"] = cover_image
            text.nameext_from_url(cover_image, final_post)
            final_post["num"] = num
            num += 1
            yield Message.Url, cover_image, final_post

        if not content_body:
            return

        if "html" in content_body:
            html_urls = []

            for href in text.extract_iter(content_body["html"], 'href="', '"'):
                if "fanbox.pixiv.net/images/entry" in href:
                    html_urls.append(href)
                elif "downloads.fanbox.cc" in href:
                    html_urls.append(href)
            for src in text.extract_iter(content_body["html"],
                                         'data-src-original="', '"'):
                html_urls.append(src)

            for url in html_urls:
                final_post = post.copy()
                text.nameext_from_url(url, final_post)
                final_post["fileUrl"] = url
                final_post["num"] = num
                num += 1
                yield Message.Url, url, final_post

        for group in ("images", "imageMap"):
            if group in content_body:
                for item in content_body[group]:
                    if group == "imageMap":
                        # imageMap is a dict with image objects as values
                        item = content_body[group][item]

                    final_post = post.copy()
                    final_post["fileUrl"] = item["originalUrl"]
                    text.nameext_from_url(item["originalUrl"], final_post)
                    if "extension" in item:
                        final_post["extension"] = item["extension"]
                    final_post["fileId"] = item.get("id")
                    final_post["width"] = item.get("width")
                    final_post["height"] = item.get("height")
                    final_post["num"] = num
                    num += 1
                    yield Message.Url, item["originalUrl"], final_post

        for group in ("files", "fileMap"):
            if group in content_body:
                for item in content_body[group]:
                    if group == "fileMap":
                        # fileMap is a dict with file objects as values
                        item = content_body[group][item]

                    final_post = post.copy()
                    final_post["fileUrl"] = item["url"]
                    text.nameext_from_url(item["url"], final_post)
                    if "extension" in item:
                        final_post["extension"] = item["extension"]
                    if "name" in item:
                        final_post["filename"] = item["name"]
                    final_post["fileId"] = item.get("id")
                    final_post["num"] = num
                    num += 1
                    yield Message.Url, item["url"], final_post

        if self.embeds:
            embeds_found = []
            if "video" in content_body:
                embeds_found.append(content_body["video"])
            embeds_found.extend(content_body.get("embedMap", {}).values())

            for embed in embeds_found:
                # embed_result is (message type, url, metadata dict)
                embed_result = self._process_embed(post, embed)
                if not embed_result:
                    continue
                embed_result[2]["num"] = num
                num += 1
                yield embed_result

    def _process_embed(self, post, embed):
        final_post = post.copy()
        provider = embed["serviceProvider"]
        content_id = embed.get("videoId") or embed.get("contentId")
        prefix = "ytdl:" if self.embeds == "ytdl" else ""
        url = None
        is_video = False

        if provider == "soundcloud":
            url = prefix+"https://soundcloud.com/"+content_id
            is_video = True
        elif provider == "youtube":
            url = prefix+"https://youtube.com/watch?v="+content_id
            is_video = True
        elif provider == "vimeo":
            url = prefix+"https://vimeo.com/"+content_id
            is_video = True
        elif provider == "fanbox":
            # this is an old URL format that redirects
            # to a proper Fanbox URL
            url = "https://www.pixiv.net/fanbox/"+content_id
            # resolve redirect
            response = self.request(url, method="HEAD", allow_redirects=False)
            url = response.headers["Location"]
            final_post["_extractor"] = FanboxPostExtractor
        elif provider == "twitter":
            url = "https://twitter.com/_/status/"+content_id
        elif provider == "google_forms":
            templ = "https://docs.google.com/forms/d/e/{}/viewform?usp=sf_link"
            url = templ.format(content_id)
        else:
            self.log.warning("service not recognized: {}".format(provider))

        if url:
            final_post["embed"] = embed
            final_post["embedUrl"] = url
            text.nameext_from_url(url, final_post)
            msg_type = Message.Queue
            if is_video and self.embeds == "ytdl":
                msg_type = Message.Url
            return msg_type, url, final_post


class FanboxCreatorExtractor(FanboxExtractor):
    """Extractor for a Fanbox creator's works"""
    subcategory = "creator"
    pattern = BASE_PATTERN + r"(?:/posts)?/?$"
    test = (
        ("https://xub.fanbox.cc", {
            "range": "1-15",
            "count": ">= 15",
            "keyword": {
                "creatorId" : "xub",
                "tags"       : list,
                "title"      : str,
            },
        }),
        ("https://xub.fanbox.cc/posts"),
        ("https://www.fanbox.cc/@xub/"),
        ("https://www.fanbox.cc/@xub/posts"),
    )

    def __init__(self, match):
        FanboxExtractor.__init__(self, match)
        self.creator_id = match.group(1) or match.group(2)

    def posts(self):
        url = "https://api.fanbox.cc/post.listCreator?creatorId={}&limit=10"

        return self._pagination(url.format(self.creator_id))


class FanboxPostExtractor(FanboxExtractor):
    """Extractor for media from a single Fanbox post"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/posts/(\d+)"
    test = (
        ("https://www.fanbox.cc/@xub/posts/1910054", {
            "count": 3,
            "keyword": {
                "title": "えま★おうがすと",
                "tags": list,
                "hasAdultContent": True,
                "isCoverImage": False
            },
        }),
        # entry post type, image embedded in html of the post
        ("https://nekoworks.fanbox.cc/posts/915", {
            "count": 2,
            "keyword": {
                "title": "【SAYORI FAN CLUB】お届け内容",
                "tags": list,
                "html": str,
                "hasAdultContent": True
            },
        }),
        # article post type, imageMap, 2 twitter embeds, fanbox embed
        ("https://steelwire.fanbox.cc/posts/285502", {
            "options": (("embeds", True),),
            "count": 10,
            "keyword": {
                "title": "イラスト+SS｜義足の炭鉱少年が義足を見せてくれるだけ 【全体公開版】",
                "tags": list,
                "articleBody": dict,
                "hasAdultContent": True
            },
        }),
        # 'content' metadata (#3020)
        ("https://www.fanbox.cc/@official-en/posts/4326303", {
            "keyword": {
                "content": r"re:(?s)^Greetings from FANBOX.\n \nAs of Monday, "
                           r"September 5th, 2022, we are happy to announce "
                           r"the start of the FANBOX hashtag event "
                           r"#MySetupTour ! \nAbout the event\nTo join this "
                           r"event .+ \nPlease check this page for further "
                           r"details regarding the Privacy & Terms.\n"
                           r"https://fanbox.pixiv.help/.+/10184952456601\n\n\n"
                           r"Thank you for your continued support of FANBOX.$",
            },
        }),
    )

    def __init__(self, match):
        FanboxExtractor.__init__(self, match)
        self.post_id = match.group(3)

    def posts(self):
        return (self._get_post_data(self.post_id),)


class FanboxRedirectExtractor(Extractor):
    """Extractor for pixiv redirects to fanbox.cc"""
    category = "fanbox"
    subcategory = "redirect"
    pattern = r"(?:https?://)?(?:www\.)?pixiv\.net/fanbox/creator/(\d+)"
    test = ("https://www.pixiv.net/fanbox/creator/52336352", {
        "pattern": FanboxCreatorExtractor.pattern,
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user_id = match.group(1)

    def items(self):
        url = "https://www.pixiv.net/fanbox/creator/" + self.user_id
        data = {"_extractor": FanboxCreatorExtractor}
        response = self.request(
            url, method="HEAD", allow_redirects=False, notfound="user")
        yield Message.Queue, response.headers["Location"], data
