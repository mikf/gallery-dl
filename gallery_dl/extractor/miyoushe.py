# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://miyoushe.com/"""

import itertools
import json
import re

from .common import Extractor, Message
from .. import text, exception


BASE_PATTERN = (r"(?:https?://)?(?:www\.|bbs\.)?"
                r"(?:miyoushe|mihoyo)\.com/([^/?#]+)/")


class MiyousheExtractor(Extractor):
    """Base class for miyoushe extractors"""
    category = "miyoushe"
    root = "https://miyoushe.com"
    directory_fmt = ("{category}", "{user[id]}")
    filename_fmt = "{id}_p{num}.{extension}"
    archive_fmt = "{id}_{filename}"
    cookiedomain = ".miyoushe.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.max_posts = self.config("max-posts", 0)
        self.api = MiyousheWebAPI(self)

    def items(self):
        self._prepare_ddosguard_cookies()

        posts = self.posts()
        metadata = self.metadata()

        if self.max_posts:
            posts = itertools.islice(posts, self.max_posts)
        for post in posts:
            data = {
                "id": post["post"]["post_id"],
                # image_list.len = vod_list.len(video cover) + post.images.len
                "media_number":
                    len(post['vod_list']) + len(post['post']['images']),
                "num": 0,
                "game_id": post["post"]["game_id"],
                "forum_id": post["post"]["f_forum_id"],
                "topics": [],
                "user": {
                    "id": post["post"]["uid"],
                    "name": post["user"]["nickname"],
                    "is_followed": post["user"]["is_following"],
                },
                "title": post["post"]["subject"],
                "content": post["post"]["content"],
                "stat": post["stat"],
                "create_date":
                    text.parse_timestamp(post["post"]["created_at"]),
                "last_modify_time":
                    text.parse_timestamp(post["last_modify_time"]),
            }
            for topic in post["topics"]:
                data["topics"].append(topic["name"])
            data.update(metadata)

            yield Message.Directory, data
            self.log.debug("id: " + data["id"])

            if not post["vod_list"]:  # only picture
                for imgUrl in post["post"]["images"]:
                    data['num'] = data['num'] + 1
                    yield Message.Url, imgUrl, text.nameext_from_url(
                        imgUrl, data)
            else:  # video and picture
                content = json.loads(post['post']['structured_content'])
                for c in content:
                    mediaUrl = self._get_url_from_insert(c["insert"], post)
                    if mediaUrl:
                        data['num'] = data['num'] + 1
                        yield Message.Url, mediaUrl, text.nameext_from_url(
                            mediaUrl, data)

            if (data['num'] != data['media_number']):
                self.log.warning(
                    "The number of files does not appear to be correct",
                    data['id'])

    def _get_url_from_insert(self, insert, post):
        if isinstance(insert, dict) is False:
            return None

        if "image" in insert:
            image = insert['image']
            if re.match(r"^[0-9]+$", image):
                for v in post['image_list']:
                    if v['image_id'] == image:
                        return v['url']
            return image
        elif "vod" in insert:
            vod_id = insert['vod']['id']
            for v in post['vod_list']:
                if v['id'] == vod_id:
                    return v['resolutions'][-1]['url']
        else:  # link_card, divider
            return None

    def posts(self):
        """Return an iterable containing all relevant 'posts' objects"""

    def metadata(self):
        """Collect metadata for extractor job"""
        return {}


class MiyousheArticleExtractor(MiyousheExtractor):
    """Extractor for a single miyoushe article"""
    subcategory = "article"
    pattern = BASE_PATTERN + r"article/([^/?#]+)"
    test = (
        # only picture
        ("https://www.miyoushe.com/ys/article/36907872", {}),
        # only video
        ("https://bbs.mihoyo.com/ys/article/36611810", {}),
        # mix media
        ("https://www.miyoushe.com/ys/article/14221110", {}),
        # mix media
        ("https://www.miyoushe.com/ys/article/25417490", {}),
        # image id
        ("https://www.miyoushe.com/ys/article/27741796", {}),
    )

    def __init__(self, match):
        MiyousheExtractor.__init__(self, match)
        self.article_id = match.group(2)

    def posts(self):
        return (self.api.get_post_full(self.article_id),)


class MiyousheFavouriteExtractor(MiyousheExtractor):
    """Extractor for all favorites of a miyoushe-user"""
    subcategory = "favourite"
    pattern = BASE_PATTERN + r"accountCenter/bookList\?id=([^/?#]+)"
    test = (
        ("https://www.miyoushe.com/ys/accountCenter/bookList?id=82229637", {
            "options": (("max-posts", 25),),
        })
    )

    def __init__(self, match):
        MiyousheExtractor.__init__(self, match)
        self.uid = match.group(2)

    def posts(self):
        return self.api.user_favourite_post(uid=self.uid)


class MiyousheWebAPI:

    def __init__(self, extractor):
        self.extractor = extractor
        extractor.session.headers.update({
            "Referer": "https://www.miyoushe.com",
        })

    def get_post_full(self, post_id):
        return self._call("/getPostFull", {
            "post_id": post_id,
        })['post']

    def user_favourite_post(self, uid=None, offset=None):
        params = {}
        if uid:
            params["uid"] = uid
        if offset:
            params["offset"] = offset
        return self._pagination("/userFavouritePost", params, "list")

    def _call(self, endpoint, params=None):
        url = "https://bbs-api.miyoushe.com/post/wapi" + endpoint

        response = self.extractor.request(url, params=params)
        data = response.json()

        if data['message'] == "OK":
            return data["data"]
        else:
            raise exception.StopExtraction("API request failed: %s",
                                           data['message'])

    def _pagination(self, endpoint, params, key="list"):
        while True:
            data = self._call(endpoint, params)
            yield from data[key]
            if data["is_last"]:
                return
            params['offset'] = data['next_offset']
