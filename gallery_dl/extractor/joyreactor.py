# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://joyreactor.com/"""

from .common import Extractor, Message
from .. import text
import binascii

BASE_PATTERN = r"(?:https?://)?joyreactor\.c(om|c)"


class JoyreactorExtractor(Extractor):
    """Base class for joyreactor extractors"""
    basecategory = "reactor"
    category = "joyreactor"
    root = "https://joyreactor.com"
    filename_fmt = ("{post_id}_{num:>02}_{file_id}"
                    "{title:?_//[b:200]}.{extension}")
    archive_fmt = "{post_id}_{num}"
    request_interval = (3.0, 6.0)

    def __init__(self, match):
        self.root = "https://joyreactor.c" + match[1]
        Extractor.__init__(self, match)

    def _init(self):
        self.embeds = self.config("embeds", False)
        self.metadata = self.config("metadata", False)
        self.videos = self.config("videos", True)
        self.videos_formats = self.config("format")

        if isinstance(self.videos_formats, str):
            self.videos_formats = self.videos_formats.split(",")

    def items(self):
        headers = {"Referer": self.root + "/"}
        if not self.metadata:
            dfmt = ("%d.%m.%y, %H:%M" if self.groups[0] == "c" else
                    "%d/%m/%y, %H:%M")

        for html, data in self.posts():
            files = self._extract_files(html)

            extr = text.extract_from(html)
            post = {
                "count"  : len(files),
                "user"   : text.unescape(extr(' alt="', '"')),
                "user_id": extr("/avatar/user/", '"'),
                "tags"   : text.split_html(extr(
                    'class="post-tags', '</div>'))[1:],
                "content": extr(
                    'class="post-content">', '<div class="post-footer">'),
                "date"   : extr("</span></button>", "</div>"),
                "post_id": extr('"/post/', '"'),
                "_http_headers": headers,
            }

            if data is None:
                post["date"] = self.parse_datetime(
                    post["date"].rpartition(">")[2], dfmt)
            else:
                post["date"] = self.parse_datetime_iso(data.get("createdAt"))
                post["nsfw"] = data.get("nsfw")
                post["unsafe"] = data.get("unsafe")
                post["banned"] = data.get("banned")
                post["comments"] = data.get("commentsCount")
                post["rating"] = data.get("rating")
                if seo := data.get("seoAttributes"):
                    post["title"] = seo.get("title")

            yield Message.Directory, "", post
            for post["num"], file in enumerate(files, 1):
                url = file["file_url"]
                text.nameext_from_url(url, post)
                post.update(file)
                post["file_id"] = post["filename"].rpartition("-")[2]
                yield Message.Url, url, post

    def _extract_files(self, html):
        files = []
        last = ""

        for url in text.extract_iter(html, 'src="', '"'):
            if "/avatar/" in url or last == url:
                continue
            last = url

            if ".joyreactor.c" not in url:
                if not self.embeds:
                    continue
                files.append({"file_url": "ytdl:"+url, "type": "embed"})
            elif "/webm/" in url:
                if not self.videos:
                    continue
                if self.videos_formats is None:
                    files.append({
                        "file_url": url,
                        "type"    : "video",
                        "format"  : "webm",
                    })
                else:
                    for fmt in self.videos_formats:
                        lhs, _, rhs = url.rpartition("/webm/")
                        files.append({
                            "file_url": f"{lhs}/{fmt}/"
                                        f"{rhs[:rhs.find('.')]}.{fmt}",
                            "type"    : "video",
                            "format"  : fmt,
                        })
            else:
                lhs, _, rhs = url.rpartition("/")
                url = f"{lhs}/full/{rhs}"
                files.append({"file_url": url, "type": "image"})

        return files

    def _request_graphql(self, opname, variables):
        url = "https://api.joyreactor.com/graphql"
        headers = {
            "Referer": self.root + "/",
            "Origin" : self.root,
        }
        data = {
            "variables": variables,
            "query"    : self.utils("graphql", opname),
        }
        return self.request_json(
            url, method="POST", headers=headers, json=data,
            interval=False)["data"]

    def _pagination(self, url, opname, variables):
        data = path = None

        while True:
            html = self.request(url).text
            html_posts = html.split('class="content"')
            del html_posts[0]

            if path is None and ('class="expand-wrapper relative">'
                                 '<div class="absolute' in html_posts[0]):
                del html_posts[0]

            pgn = text.extr(html, 'ant-pagination-next', "</li>")
            path = text.extr(pgn, 'href="', '"')

            if self.metadata:
                variables["page"] = (text.parse_int(path[path.rfind("/")+1:])+1
                                     if path else None)
                data = self._request_graphql(opname, variables)
                data_posts = data.popitem()[1]["postPager"]["posts"]
                yield from zip(html_posts, data_posts)
            else:
                for post in html_posts:
                    yield post, None

            if not path or not path.endswith("/1/rev"):
                break
            url = self.root + path


class JoyreactorPostExtractor(JoyreactorExtractor):
    """Extractor for single joyreactor posts"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/post/(\d+)"
    example = "http://joyreactor.com/post/12345"

    def posts(self):
        pid = self.groups[1]
        url = f"{self.root}/post/{pid}"
        page = self.request(url).text
        html = text.extr(page, 'class="content"', 'class="comment"')

        if self.metadata:
            data = self._request_graphql("IdPostPageQuery", {
                "id": binascii.b2a_base64(b"Post:" + bytes(str(pid), "ascii"),
                                          newline=False).decode(),
                "isAuthorised": False,
            })["node"]
        else:
            data = None

        return ((html, data),)


class JoyreactorTagExtractor(JoyreactorExtractor):
    """Extractor for joyreactor tag searches"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "{search_tags}_{post_id}_{num}"
    pattern = BASE_PATTERN + r"(/tag/([^/?#]+)(?:/[^/?#]+)?)"
    example = "http://joyreactor.com/tag/TAG"

    def posts(self):
        _, path, tag = self.groups
        self.kwdict["search_tags"] = tag = text.unquote(tag)

        variables = {
            "name"        : tag,
            "page"        : None,
            "lineType"    : "GOOD",
            "isAuthorised": False,
            "isHomepage"  : False,
        }
        return self._pagination(
            self.root + path, "TagPageQuery", variables)


class JoyreactorUserExtractor(JoyreactorExtractor):
    """Extractor for posts of a joyreactor user"""
    subcategory = "user"
    directory_fmt = ("{category}", "user", "{user}")
    pattern = BASE_PATTERN + r"(/user/([^/?#]+)(?:/[^/?#]+)?)"
    example = "http://joyreactor.com/user/USER"

    def posts(self):
        _, path, user = self.groups

        variables = {
            "username"    : text.unquote(user),
            "page"        : None,
            "lineType"    : "GOOD",
            "isAuthorised": False,
            "isHomepage"  : False,
        }
        return self._pagination(
            self.root + path, "UserProfilePageQuery", variables)


class JoyreactorSearchExtractor(JoyreactorExtractor):
    """Extractor for joyreactor search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "{search_tags}_{post_id}_{num}"
    pattern = BASE_PATTERN + r"(/search/([^/?#]+)(?:/[^/?#]+)?)"
    example = "http://joyreactor.com/search/TAG"

    def posts(self):
        _, path, query = self.groups
        self.kwdict["search_tags"] = query = text.unquote(query)

        variables = {
            "query"       : query,
            "page"        : None,
            "tagNames"    : (),
            "username"    : None,
            "isAuthorised": False,
            "showUnsafe"  : None,
            "showNsfw"    : True,
            "showOnlyNsfw": False,
            "minRating"   : None,
            "maxRating"   : None,
            "sortByDate"  : False,
            "sortByRating": False,
        }

        return self._pagination(
            self.root + path, "SearchPageQuery", variables)
