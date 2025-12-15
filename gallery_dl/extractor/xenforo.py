# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for XenForo forums"""

from .common import BaseExtractor, Message
from .. import text, exception
from ..cache import cache


class XenforoExtractor(BaseExtractor):
    """Base class for xenforo extractors"""
    basecategory = "xenforo"
    directory_fmt = ("{category}", "{thread[section]}",
                     "{thread[title]} ({thread[id]})")
    filename_fmt = "{post[id]}_{num:>02}_{id}_{filename}.{extension}"
    archive_fmt = "{post[id]}/{type[0]}{id}_{filename}"

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        self.cookies_domain = "." + self.root.split("/")[2]
        self.cookies_names = self.config_instance("cookies")

    def items(self):
        self.login()

        extract_urls = text.re(
            r'(?s)(?:'
            r'<video (.*?\ssrc="[^"]+".*?)</video>'
            r'|<a [^>]*?href="[^"]*?'
            r'(/(?:index\.php\?)?attachments/[^"]+".*?)</a>'
            r'|<div [^>]*?data-src="[^"]*?'
            r'(/(?:index\.php\?)attachments/[^"]+".*?)/>'
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
            yield Message.Directory, "", data

            id_last = None
            data["_http_expected_status"] = (403,)
            data["_http_validate"] = self._validate
            data["num"] = data["num_internal"] = data["num_external"] = 0
            for video, inl1, inl2, ext in urls:
                if ext:
                    data["num"] += 1
                    data["num_external"] += 1
                    data["type"] = "external"
                    if ext[0] == "/":
                        if ext[1] == "/":
                            ext = "https:" + ext
                        else:
                            continue
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
                    path = inline[:inline.find('"')]
                    name, _, id = path[path.rfind("/", 0, -1):].strip(
                        "/").rpartition(".")
                    if id == id_last:
                        id_last = None
                        continue
                    else:
                        id_last = id
                    data["id"] = text.parse_int(id)
                    if alt := text.extr(inline, 'alt="', '"'):
                        text.nameext_from_name(alt, data)
                        if not data["extension"]:
                            data["extension"] = name.rpartition("-")[2]
                    else:
                        data["filename"], _, data["extension"] = \
                            name.rpartition("-")
                    data["num"] += 1
                    data["num_internal"] += 1
                    data["type"] = "inline"
                    yield Message.Url, self.root + path, data

    def request_page(self, url):
        try:
            return self.request(url)
        except exception.HttpError as exc:
            if exc.status == 403 and b">Log in<" in exc.response.content:
                self._require_auth(exc.response)
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
            if pnum is None and not response.history:
                self._require_auth()
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
        try:
            data = self._extract_jsonld(page)
        except ValueError:
            return {}

        schema = data.get("mainEntity", data)
        author = schema["author"]
        stats = schema["interactionStatistic"]
        url_t = schema.get("url") or schema.get("@id") or ""
        url_a = author.get("url") or ""

        thread = {
            "id"   : url_t[url_t.rfind(".")+1:-1],
            "url"  : url_t,
            "title": schema["headline"],
            "date" : self.parse_datetime_iso(schema["datePublished"]),
            "tags" : (schema["keywords"].split(", ")
                      if "keywords" in schema else ()),
            "section"   : schema["articleSection"],
            "author"    : author.get("name") or "",
            "author_id" : (url_a[url_a.rfind(".")+1:-1] if url_a else
                           (author.get("name") or "")[15:]),
            "author_url": url_a,
        }

        if isinstance(stats, list):
            thread["views"] = stats[0]["userInteractionCount"]
            thread["posts"] = stats[1]["userInteractionCount"]
        else:
            thread["views"] = -1
            thread["posts"] = stats["userInteractionCount"]

        return thread

    def _parse_post(self, html):
        extr = text.extract_from(html)

        post = {
            "author": extr('data-author="', '"'),
            "id": extr('data-content="post-', '"'),
            "author_url": (extr('itemprop="url" content="', '"') or
                           extr('<a href="', '"')),
            "date": self.parse_datetime_iso(extr('datetime="', '"')),
            "content": extr('class="message-body',
                            '<div class="js-selectToQuote'),
            "attachments": extr('<section class="message-attachments">',
                                '</section>'),
        }

        url_a = post["author_url"]
        post["author_id"] = url_a[url_a.rfind(".")+1:-1]

        con = post["content"]
        if (pos := con.find('<div class="bbWrapper')) >= 0:
            con = con[pos:]
        post["content"] = con.strip()

        return post

    def _require_auth(self, response=None):
        raise exception.AuthRequired(
            ("username & password", "authenticated cookies"), None,
            None if response is None else self._extract_error(response.text))

    def _validate(self, response):
        if response.status_code == 403 and b">Log in<" in response.content:
            self._require_auth(response)
        return True


BASE_PATTERN = XenforoExtractor.update({
    "simpcity": {
        "root": "https://simpcity.cr",
        "pattern": r"(?:www\.)?simpcity\.(?:cr|su)",
        "cookies": ("ogaddgmetaprof_user",),
    },
    "nudostarforum": {
        "root": "https://nudostar.com/forum",
        "pattern": r"(?:www\.)?nudostar\.com/forum",
        "cookies": ("xf_user",),
    },
    "atfforum": {
        "root": "https://allthefallen.moe/forum",
        "pattern": r"(?:www\.)?allthefallen\.moe/forum",
        "cookies": ("xf_user",),
    },
})


class XenforoPostExtractor(XenforoExtractor):
    subcategory = "post"
    pattern = (rf"{BASE_PATTERN}(/(?:index\.php\?)?threads"
               rf"/[^/?#]+/post-|/posts/)(\d+)")
    example = "https://simpcity.cr/threads/TITLE.12345/post-54321"

    def posts(self):
        path = self.groups[-2]
        post_id = self.groups[-1]
        url = f"{self.root}{path}{post_id}/"
        page = self.request_page(url).text

        pos = page.find(f'data-content="post-{post_id}"')
        if pos < 0:
            raise exception.NotFoundError("post")
        html = text.extract(page, "<article ", "<footer", pos-200)[0]

        self.kwdict["thread"] = self._parse_thread(page)
        return (self._parse_post(html),)


class XenforoThreadExtractor(XenforoExtractor):
    subcategory = "thread"
    pattern = (rf"{BASE_PATTERN}(/(?:index\.php\?)?threads"
               rf"/(?:[^/?#]+\.)?\d+)(?:/page-(\d+))?")
    example = "https://simpcity.cr/threads/TITLE.12345/"

    def posts(self):
        path = self.groups[-2]
        pnum = self.groups[-1]

        if (order := self.config("order-posts")) and \
                order[0] not in ("d", "r"):
            pages = self._pagination(path, pnum)
            reverse = False
        else:
            pages = self._pagination_reverse(path, pnum)
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


class XenforoForumExtractor(XenforoExtractor):
    subcategory = "forum"
    pattern = (rf"{BASE_PATTERN}(/(?:index\.php\?)?forums"
               rf"/(?:[^/?#]+\.)?[^/?#]+)(?:/page-(\d+))?")
    example = "https://simpcity.cr/forums/TITLE.123/"

    def items(self):
        extract_threads = text.re(
            r'(/(?:index\.php\?)?threads/[^"]+)"[^>]+data-xf-init=').findall

        data = {"_extractor": XenforoThreadExtractor}
        path = self.groups[-2]
        pnum = self.groups[-1]
        for page in self._pagination(path, pnum):
            for path in extract_threads(page):
                yield Message.Queue, f"{self.root}{text.unquote(path)}", data
