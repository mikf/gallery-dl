# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://meme.museum/"""

from .common import Extractor, Message
from .. import text


class MememuseumExtractor(Extractor):
    """Base class for meme.museum extractors"""
    basecategory = "booru"
    category = "mememuseum"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    archive_fmt = "{id}"
    root = "https://meme.museum"

    def items(self):
        data = self.metadata()

        for post in self.posts():
            url = post["file_url"]
            for key in ("id", "width", "height"):
                post[key] = text.parse_int(post[key])
            post["tags"] = text.unquote(post["tags"])
            post.update(data)
            yield Message.Directory, post
            yield Message.Url, url, text.nameext_from_url(url, post)

    def metadata(self):
        """Return general metadata"""
        return ()

    def posts(self):
        """Return an iterable containing data of all relevant posts"""
        return ()


class MememuseumTagExtractor(MememuseumExtractor):
    """Extractor for images from meme.museum by search-tags"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    pattern = r"(?:https?://)?meme\.museum/post/list/([^/?#]+)"
    test = ("https://meme.museum/post/list/animated/1", {
        "pattern": r"https://meme\.museum/_images/\w+/\d+%20-%20",
        "count": ">= 30"
    })
    per_page = 25

    def __init__(self, match):
        MememuseumExtractor.__init__(self, match)
        self.tags = text.unquote(match.group(1))

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        pnum = 1
        while True:
            url = "{}/post/list/{}/{}".format(self.root, self.tags, pnum)
            extr = text.extract_from(self.request(url).text)

            while True:
                mime = extr("data-mime='", "'")
                if not mime:
                    break

                pid = extr("data-post-id='", "'")
                tags, dimensions, size = extr("title='", "'").split(" // ")
                md5 = extr("/_thumbs/", "/")
                width, _, height = dimensions.partition("x")

                yield {
                    "file_url": "{}/_images/{}/{}%20-%20{}.{}".format(
                        self.root, md5, pid, text.quote(tags),
                        mime.rpartition("/")[2]),
                    "id": pid, "md5": md5, "tags": tags,
                    "width": width, "height": height,
                    "size": text.parse_bytes(size[:-1]),
                }

            if not extr(">Next<", ">"):
                return
            pnum += 1


class MememuseumPostExtractor(MememuseumExtractor):
    """Extractor for single images from meme.museum"""
    subcategory = "post"
    pattern = r"(?:https?://)?meme\.museum/post/view/(\d+)"
    test = ("https://meme.museum/post/view/10243", {
        "pattern": r"https://meme\.museum/_images/105febebcd5ca791ee332adc4997"
                   r"1f78/10243%20-%20g%20beard%20open_source%20richard_stallm"
                   r"an%20stallman%20tagme%20text\.jpg",
        "keyword": "3c8009251480cf17248c08b2b194dc0c4d59580e",
        "content": "45565f3f141fc960a8ae1168b80e718a494c52d2",
    })

    def __init__(self, match):
        MememuseumExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def posts(self):
        url = "{}/post/view/{}".format(self.root, self.post_id)
        extr = text.extract_from(self.request(url).text)

        return ({
            "id"      : self.post_id,
            "tags"    : extr(": ", "<"),
            "md5"     : extr("/_thumbs/", "/"),
            "file_url": self.root + extr("id='main_image' src='", "'"),
            "width"   : extr("data-width=", " ").strip("'\""),
            "height"  : extr("data-height=", " ").strip("'\""),
            "size"    : 0,
        },)
