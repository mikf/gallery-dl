# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.lofter.com/"""

from .common import Extractor, Message
from .. import text, util, exception


class LofterExtractor(Extractor):
    """Base class for lofter extractors"""
    category = "lofter"
    root = "https://www.lofter.com"
    directory_fmt = ("{category}", "{blog_name}")
    filename_fmt = "{id}_{num}.{extension}"
    archive_fmt = "{id}_{num}"

    def _init(self):
        self.api = LofterAPI(self)

    def items(self):
        for post in self.posts():
            if post is None:
                continue
            if "post" in post:
                post = post["post"]

            post["blog_name"] = post["blogInfo"]["blogName"]
            post["date"] = text.parse_timestamp(post["publishTime"] // 1000)
            post_type = post["type"]

            # Article
            if post_type == 1:
                content = post["content"]
                image_urls = text.extract_iter(content, '<img src="', '"')
                image_urls = [text.unescape(x) for x in image_urls]
                image_urls = [x.partition("?")[0] for x in image_urls]

            # Photo
            elif post_type == 2:
                photo_links = util.json_loads(post["photoLinks"])
                image_urls = [x["orign"] for x in photo_links]
                image_urls = [x.partition("?")[0] for x in image_urls]

            # Video
            elif post_type == 4:
                embed = util.json_loads(post["embed"])
                image_urls = [embed["originUrl"]]

            # Answer
            elif post_type == 5:
                images = util.json_loads(post["images"])
                image_urls = [x["orign"] for x in images]
                image_urls = [x.partition("?")[0] for x in image_urls]

            else:
                image_urls = ()
                self.log.warning(
                    "%s: Unsupported post type '%s'.",
                    post["id"], post_type)

            post["count"] = len(image_urls)
            yield Message.Directory, post
            for post["num"], url in enumerate(image_urls, 1):
                yield Message.Url, url, text.nameext_from_url(url, post)

    def posts(self):
        return ()


class LofterPostExtractor(LofterExtractor):
    """Extractor for a lofter post"""
    subcategory = "post"
    pattern = r"(?:https?://)?[\w-]+\.lofter\.com/post/([0-9a-f]+)_([0-9a-f]+)"
    example = "https://BLOG.lofter.com/post/12345678_90abcdef"

    def posts(self):
        blog_id, post_id = self.groups
        post = self.api.post(int(blog_id, 16), int(post_id, 16))
        return (post,)


class LofterBlogPostsExtractor(LofterExtractor):
    """Extractor for a lofter blog's posts"""
    subcategory = "blog-posts"
    pattern = (r"(?:https?://)?(?:"
               # https://www.lofter.com/front/blog/home-page/<blog_name>
               r"www\.lofter\.com/front/blog/home-page/([\w-]+)|"
               # https://<blog_name>.lofter.com/
               r"([\w-]+)\.lofter\.com"
               r")/?(?:$|\?|#)")
    example = "https://BLOG.lofter.com/"

    def posts(self):
        blog_name = self.groups[0] or self.groups[1]
        return self.api.blog_posts(blog_name)


class LofterAPI():

    def __init__(self, extractor):
        self.extractor = extractor

    def blog_posts(self, blog_name):
        endpoint = "/v2.0/blogHomePage.api"
        params = {
            "method": "getPostLists",
            "offset": 0,
            "limit": 200,
            "blogdomain": blog_name + ".lofter.com",
        }
        return self._pagination(endpoint, params)

    def post(self, blog_id, post_id):
        endpoint = "/oldapi/post/detail.api"
        params = {
            "targetblogid": blog_id,
            "postid": post_id,
        }
        return self._call(endpoint, params)["posts"][0]

    def _call(self, endpoint, data):
        url = "https://api.lofter.com" + endpoint
        params = {
            'product': 'lofter-android-7.9.10'
        }
        response = self.extractor.request(
            url, method="POST", params=params, data=data)
        info = response.json()

        if info["meta"]["status"] == 4200:
            raise exception.NotFoundError("blog")

        if info["meta"]["status"] != 200:
            self.extractor.log.debug("Server response: %s", info)
            raise exception.StopExtraction("API request failed")

        return info["response"]

    def _pagination(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)
            posts = data["posts"]

            yield from posts

            if data["offset"] < 0:
                break

            if params["offset"] + len(posts) < data["offset"]:
                break
            params["offset"] = data["offset"]
