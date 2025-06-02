# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Shimmie2 instances"""

from .common import BaseExtractor, Message
from .. import text


class Shimmie2Extractor(BaseExtractor):
    """Base class for shimmie2 extractors"""
    basecategory = "shimmie2"
    filename_fmt = "{category}_{id}{md5:?_//}.{extension}"
    archive_fmt = "{id}"

    def _init(self):
        cookies = self.config_instance("cookies")
        if cookies:
            domain = self.root.rpartition("/")[2]
            self.cookies_update_dict(cookies, domain=domain)

        file_url = self.config_instance("file_url")
        if file_url:
            self.file_url_fmt = file_url

        if self.category == "giantessbooru":
            self.posts = self._posts_giantessbooru

    def items(self):
        data = self.metadata()

        for post in self.posts():

            post["id"] = text.parse_int(post["id"])
            post["width"] = text.parse_int(post["width"])
            post["height"] = text.parse_int(post["height"])
            post["tags"] = text.unquote(post["tags"])
            post.update(data)

            url = post["file_url"]
            if "/index.php?" in url:
                post["filename"], _, post["extension"] = \
                    url.rpartition("/")[2].rpartition(".")
            else:
                text.nameext_from_url(url, post)

            yield Message.Directory, post
            yield Message.Url, url, post

    def metadata(self):
        """Return general metadata"""
        return ()

    def posts(self):
        """Return an iterable containing data of all relevant posts"""
        return ()

    def _quote_type(self, page):
        """Return quoting character used in 'page' (' or ")"""
        try:
            return page[page.index("<link rel=")+10]
        except Exception:
            return "'"


BASE_PATTERN = Shimmie2Extractor.update({
    "giantessbooru": {
        "root": "https://sizechangebooru.com",
        "pattern": r"(?:sizechange|giantess)booru\.com",
        "cookies": {"agreed": "true"},
    },
    "cavemanon": {
        "root": "https://booru.cavemanon.xyz",
        "pattern": r"booru\.cavemanon\.xyz",
        "file_url": "{0}/index.php?q=image/{2}.{4}",
    },
    "rule34hentai": {
        "root": "https://rule34hentai.net",
        "pattern": r"rule34hentai\.net",
    },
    "vidyapics": {
        "root": "https://vidya.pics",
        "pattern": r"vidya\.pics",
    },
}) + r"/(?:index\.php\?q=/?)?"


class Shimmie2TagExtractor(Shimmie2Extractor):
    """Extractor for shimmie2 posts by tag search"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    file_url_fmt = "{}/_images/{}/{}%20-%20{}.{}"
    pattern = BASE_PATTERN + r"post/list/([^/?#]+)(?:/(\d+))?"
    example = "https://vidya.pics/post/list/TAG/1"

    def metadata(self):
        self.tags = text.unquote(self.groups[-2])
        return {"search_tags": self.tags}

    def posts(self):
        pnum = text.parse_int(self.groups[-1], 1)
        file_url_fmt = self.file_url_fmt.format

        init = True
        mime = ""

        while True:
            url = "{}/post/list/{}/{}".format(self.root, self.tags, pnum)
            page = self.request(url).text
            extr = text.extract_from(page)

            if init:
                init = False
                quote = self._quote_type(page)
                has_mime = (" data-mime=" in page)
                has_pid = (" data-post-id=" in page)

            while True:
                if has_mime:
                    mime = extr(" data-mime="+quote, quote)
                if has_pid:
                    pid = extr(" data-post-id="+quote, quote)
                else:
                    pid = extr(" href='/post/view/", quote)

                if not pid:
                    break

                data = extr("title="+quote, quote).split(" // ")
                tags = data[0]
                dimensions = data[1]
                size = data[2]

                width, _, height = dimensions.partition("x")
                md5 = extr("/_thumbs/", "/")

                yield {
                    "file_url": file_url_fmt(
                        self.root, md5, pid, text.quote(tags),
                        mime.rpartition("/")[2] if mime else "jpg"),
                    "id": pid,
                    "md5": md5,
                    "tags": tags,
                    "width": width,
                    "height": height,
                    "size": text.parse_bytes(size[:-1]),
                }

            pnum += 1
            if not extr(">Next<", ">"):
                if not extr("/{}'>{}<".format(pnum, pnum), ">"):
                    return

    def _posts_giantessbooru(self):
        pnum = text.parse_int(self.groups[-1], 1)
        file_url_fmt = (self.root + "/index.php?q=/image/{}.jpg").format

        while True:
            url = "{}/index.php?q=/post/list/{}/{}".format(
                self.root, self.tags, pnum)
            extr = text.extract_from(self.request(url).text)

            while True:
                pid = extr("href='./index.php?q=/post/view/", "&")
                if not pid:
                    break

                tags, dimensions, size = extr("title='", "'").split(" // ")
                width, _, height = dimensions.partition("x")

                yield {
                    "file_url": file_url_fmt(pid),
                    "id"      : pid,
                    "md5"     : "",
                    "tags"    : tags,
                    "width"   : width,
                    "height"  : height,
                    "size"    : text.parse_bytes(size[:-1]),
                }

            pnum += 1
            if not extr("/{0}'>{0}<".format(pnum), ">"):
                return


class Shimmie2PostExtractor(Shimmie2Extractor):
    """Extractor for single shimmie2 posts"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"post/view/(\d+)"
    example = "https://vidya.pics/post/view/12345"

    def posts(self):
        post_id = self.groups[-1]
        url = "{}/post/view/{}".format(self.root, post_id)
        page = self.request(url).text
        extr = text.extract_from(page)
        quote = self._quote_type(page)

        post = {
            "id"      : post_id,
            "tags"    : extr(": ", "<").partition(" - ")[0].rstrip(")"),
            "md5"     : extr("/_thumbs/", "/"),
            "file_url": self.root + (
                extr("id={0}main_image{0} src={0}".format(quote), quote) or
                extr("<source src="+quote, quote)).lstrip("."),
            "width"   : extr("data-width=", " ").strip("\"'"),
            "height"  : extr("data-height=", ">").partition(
                " ")[0].strip("\"'"),
            "size"    : 0,
        }

        if not post["md5"]:
            post["md5"] = text.extr(post["file_url"], "/_images/", "/")

        return (post,)

    def _posts_giantessbooru(self):
        post_id = self.groups[-1]
        url = "{}/index.php?q=/post/view/{}".format(self.root, post_id)
        extr = text.extract_from(self.request(url).text)

        return ({
            "id"      : post_id,
            "tags"    : extr(": ", "<").partition(" - ")[0].rstrip(")"),
            "md5"     : "",
            "file_url": self.root + extr("id='main_image' src='.", "'"),
            "width"   : extr("orig_width =", ";"),
            "height"  : 0,
            "size"    : 0,
        },)
