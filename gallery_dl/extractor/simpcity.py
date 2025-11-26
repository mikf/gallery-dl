# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://simpcity.cr/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache

BASE_PATTERN = r"(?:https?://)?(?:www\.)?simpcity\.(?:cr|su)"


class SimpcityExtractor(Extractor):
    """Base class for simpcity extractors"""
    category = "simpcity"
    cookies_domain = "simpcity.cr"
    cookies_names = ("ogaddgmetaprof_user",)
    root = "https://simpcity.cr"
    directory_fmt = ("{category}", "{thread[section]}",
                     "{thread[title]} ({thread[id]})")
    filename_fmt = "{post[id]}_{num:>02}_{id}_{filename}.{extension}"
    archive_fmt = "{post[id]}/{type[0]}{id}_{filename}"

    def items(self):
        self.login()

        extract_urls = text.re(
            r'(?s)(?:'
            r'<video (.*?\ssrc="[^"]+".*?)</video>'
            r'|<a [^>]*?href="'
            r'(?:https://[^"]+)?(/attachments/[^"]+".*?)</a>'
            r'|<div [^>]*?data-src="'
            r'(?:https://[^"]+)?(/attachments/[^"]+".*?)/>'
            r'|(?:<a [^>]*?href="|<iframe [^>]*?src="|'
            r'''onclick="loadMedia\(this, ')([^"']+)'''
            r')'
        ).findall

        for post in self.posts():
            urls = extract_urls(post["content"])
            if post["attachments"]:
                urls.extend(extract_urls(post["attachments"]))

            data = {"post": post}
            post["count"] = data["count"] = len(urls)
            yield Message.Directory, data

            data["num"] = data["num_internal"] = data["num_external"] = 0
            for video, inl1, inl2, ext in urls:
                if ext:
                    data["num"] += 1
                    data["num_external"] += 1
                    data["type"] = "external"
                    if ext.startswith("//"):
                        ext = "https:" + ext
                    yield Message.Queue, ext, data

                elif video:
                    data["num"] += 1
                    data["num_internal"] += 1
                    data["type"] = "video"
                    url = text.extr(video, 'src="', '"')
                    text.nameext_from_url(url, data)
                    data["id"] = text.parse_int(
                        data["filename"].partition("-")[0])
                    yield Message.Url, url, data

                elif (inline := inl1 or inl2):
                    data["num"] += 1
                    data["num_internal"] += 1
                    data["type"] = "inline"
                    path = inline[:inline.find('"')]
                    name, _, id = path[path.rfind("/", 0, -1):].strip(
                        "/").rpartition(".")
                    data["id"] = text.parse_int(id)
                    if alt := text.extr(inline, 'alt="', '"'):
                        text.nameext_from_name(alt, data)
                        if not data["extension"]:
                            data["extension"] = name.rpartition("-")[2]
                    else:
                        data["filename"], _, data["extension"] = \
                            name.rpartition("-")
                    yield Message.Url, self.root + path, data

    def request_page(self, url):
        try:
            return self.request(url)
        except exception.HttpError as exc:
            if exc.status == 403 and b">Log in<" in exc.response.content:
                raise exception.AuthRequired(
                    ("username & password", "authenticated cookies"), None,
                    self._extract_error(exc.response.text))
            raise

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            self.cookies_update(self._login_impl(username, password))

    @cache(maxage=365*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = f"{self.root}/login/login"
        page = self.request(url).text
        data = {
            "_xfToken": text.extr(page, 'name="_xfToken" value="', '"'),
            "login"   : username,
            "password": password,
            "remember": "1",
            "_xfRedirect": "",
        }
        response = self.request(url, method="POST", data=data)

        if not response.history:
            err = self._extract_error(response.text)
            raise exception.AuthenticationError(f'"{err}"')

        return {
            cookie.name: cookie.value
            for cookie in self.cookies
            if cookie.domain.endswith(self.cookies_domain)
        }

    def _pagination(self, base, pnum=None):
        base = f"{self.root}{base}"

        if pnum is None:
            url = f"{base}/"
            pnum = 1
        else:
            url = f"{base}/page-{pnum}"
            pnum = None

        while True:
            page = self.request_page(url).text

            yield page

            if pnum is None or "pageNav-jump--next" not in page:
                return
            pnum += 1
            url = f"{base}/page-{pnum}"

    def _pagination_reverse(self, base, pnum=None):
        base = f"{self.root}{base}"

        url = f"{base}/page-{'9999' if pnum is None else pnum}"
        with self.request_page(url) as response:
            url = response.url
            if url[-1] == "/":
                pnum = 1
            else:
                pnum = text.parse_int(url[url.rfind("-")+1:], 1)
            page = response.text

        while True:
            yield page

            pnum -= 1
            if pnum > 1:
                url = f"{base}/page-{pnum}"
            elif pnum == 1:
                url = f"{base}/"
            else:
                return

            page = self.request_page(url).text

    def _extract_error(self, html):
        return text.unescape(text.extr(
            html, "blockMessage--error", "</").rpartition(">")[2].strip())

    def _parse_thread(self, page):
        schema = self._extract_jsonld(page)["mainEntity"]
        author = schema["author"]
        stats = schema["interactionStatistic"]
        url_t = schema["url"]
        url_a = author.get("url") or ""

        thread = {
            "id"   : url_t[url_t.rfind(".")+1:-1],
            "url"  : url_t,
            "title": schema["headline"],
            "date" : self.parse_datetime_iso(schema["datePublished"]),
            "views": stats[0]["userInteractionCount"],
            "posts": stats[1]["userInteractionCount"],
            "tags" : (schema["keywords"].split(", ")
                      if "keywords" in schema else ()),
            "section"   : schema["articleSection"],
            "author"    : author.get("name") or "",
            "author_id" : (url_a[url_a.rfind(".")+1:-1] if url_a else
                           (author.get("name") or "")[15:]),
            "author_url": url_a,
        }

        return thread

    def _parse_post(self, html):
        extr = text.extract_from(html)

        post = {
            "author": extr('data-author="', '"'),
            "id": extr('data-content="post-', '"'),
            "author_url": extr('itemprop="url" content="', '"'),
            "date": self.parse_datetime_iso(extr('datetime="', '"')),
            "content": (
                extr('<div itemprop="text">',
                     '<div class="js-selectToQuote') or
                extr('<div >',
                     '<div class="js-selectToQuote')).strip(),
            "attachments": extr('<section class="message-attachments">',
                                '</section>'),
        }

        url_a = post["author_url"]
        post["author_id"] = url_a[url_a.rfind(".")+1:-1]

        return post


class SimpcityPostExtractor(SimpcityExtractor):
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/(?:threads/[^/?#]+/post-|posts/)(\d+)"
    example = "https://simpcity.cr/threads/TITLE.12345/post-54321"

    def posts(self):
        post_id = self.groups[0]
        url = f"{self.root}/posts/{post_id}/"
        page = self.request_page(url).text

        pos = page.find(f'data-content="post-{post_id}"')
        if pos < 0:
            raise exception.NotFoundError("post")
        html = text.extract(page, "<article ", "<footer", pos-200)[0]

        self.kwdict["thread"] = self._parse_thread(page)
        return (self._parse_post(html),)


class SimpcityThreadExtractor(SimpcityExtractor):
    subcategory = "thread"
    pattern = rf"{BASE_PATTERN}(/threads/(?:[^/?#]+\.)?\d+)(?:/page-(\d+))?"
    example = "https://simpcity.cr/threads/TITLE.12345/"

    def posts(self):
        if (order := self.config("order-posts")) and \
                order[0] not in ("d", "r"):
            pages = self._pagination(*self.groups)
            reverse = False
        else:
            pages = self._pagination_reverse(*self.groups)
            reverse = True

        for page in pages:
            if "thread" not in self.kwdict:
                self.kwdict["thread"] = self._parse_thread(page)
            posts = text.extract_iter(page, "<article ", "<footer")
            if reverse:
                posts = list(posts)
                posts.reverse()
            for html in posts:
                yield self._parse_post(html)


class SimpcityForumExtractor(SimpcityExtractor):
    subcategory = "forum"
    pattern = rf"{BASE_PATTERN}(/forums/(?:[^/?#]+\.)?\d+)(?:/page-(\d+))?"
    example = "https://simpcity.cr/forums/TITLE.123/"

    def items(self):
        data = {"_extractor": SimpcityThreadExtractor}
        for page in self._pagination(*self.groups):
            for path in text.extract_iter(page, ' uix-href="', '"'):
                yield Message.Queue, f"{self.root}{text.unquote(path)}", data
