# -*- coding: utf-8 -*-

# Copyright 2025-2026 Mike Fährmann
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
    filename_fmt = "{post[id]}_{num:>02}{id:?_//}_{filename}.{extension}"
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
            r'|<a [^>]*?'
            r'href="([^"]*?/(?:index\.php\?)?attachments/[^"]+".*?)</a>'
            r'|<div class="bb(?:Image|Media)Wrapper[^>]*?'
            r'data-src="([^"]+".*?) />'
            r'|(?:<a [^>]*?href="|<iframe [^>]*?src="|'
            r'''onclick="loadMedia\(this, ')([^"']+)'''
            r')'
        ).findall

        root = self.root
        base = root if (pos := root.find("/", 8)) < 0 else root[:pos]
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
            for video, inl, bb, ext in urls:
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
                    if url[0] == "/":
                        url = base + url
                    yield Message.Url, url, data

                elif (inline := bb or inl):
                    url = inline[:inline.find('"')]
                    name, _, id = url[url.rfind("/", 0, -1):].strip(
                        "/").rpartition(".")
                    data["id"] = id = text.parse_int(id)
                    if id:
                        if id == id_last:
                            id_last = None
                            continue
                        else:
                            id_last = id
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
                    if url[0] == "/":
                        url = base + url
                    yield Message.Url, url, data

    def items_media(self, path, pnum):
        if (order := self.config("order-posts")) and \
                order[0] in ("d", "r"):
            pages = self._pagination_reverse(path, pnum)
            reverse = True
        else:
            pages = self._pagination(path, pnum)
            reverse = False

        if self.config("metadata"):
            extr_media = self._extract_media_ex
            meta = True
        else:
            extr_media = self._extract_media
            meta = False

        root = self.root
        base = root if (pos := root.find("/", 8)) < 0 else root[:pos]
        for page in pages:
            posts = page.split(
                '<div class="itemList-item js-inlineModContainer')
            del posts[0]

            if reverse:
                posts.reverse()

            for html in posts:
                href, pos = text.extract(html, 'href="', '"')
                name, pos = text.extract(html, "alt='", "'", pos)

                url, media = extr_media(
                    base + href, href[href.rfind("/", 0, -1)+1:-1])
                if not meta and name:
                    text.nameext_from_name(text.unescape(name), media)

                yield Message.Directory, "", media
                yield Message.Url, url, media

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

        url = self.root + "/login/login"
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
        base = self.root + base

        if pnum is None:
            url = base + "/"
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
        base = self.root + base

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
                url = base + "/"
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

        thread = {
            "id"   : url_t[url_t.rfind(".")+1:-1],
            "url"  : url_t,
            "title": schema["headline"],
            "date" : self.parse_datetime_iso(schema["datePublished"]),
            "tags" : (schema["keywords"].split(", ")
                      if "keywords" in schema else ()),
            "section": schema["articleSection"],
            "author" : author.get("name") or "",
        }

        if url_a := author.get("url"):
            thread["author_url"] = url_a
            thread["author_slug"], _, thread["author_id"] = \
                url_a[url_a.rfind("/", 0, -1)+1:-1].rpartition(".")
        else:
            thread["author_url"] = ""
            thread["author_slug"] = text.slugify(thread["author"][:15])
            thread["author_id"] = thread["author"][15:]

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
        post["author_slug"], _, post["author_id"] = \
            url_a[url_a.rfind("/", 0, -1)+1:-1].rpartition(".")

        con = post["content"]
        if (pos := con.find('<div class="bbWrapper')) >= 0:
            con = con[pos:]
        post["content"] = con.strip()

        return post

    def _extract_media(self, url, file):
        media = {}
        name, _, media["id"] = file.rpartition(".")
        media["filename"], _, media["extension"] = name.rpartition("-")
        return url + "full", media

    def _extract_media_ex(self, url, file):
        page = self.request(url).text

        schema = self._extract_jsonld(page)
        main = schema["mainEntity"]
        author = main["author"]
        stats = main["interactionStatistic"]

        media = text.nameext_from_name(main["name"], {
            "schema": schema,
            "id"    : file.rpartition(".")[2],
            "size"  : main.get("contentSize"),
            "description": main.get("description"),
            "date"  : self.parse_datetime_iso(main.get("dateCreated")),
            "width" : (w := main.get("width")) and text.parse_int(
                w["name"].partition(" ")[0]) or 0,
            "height": (h := main.get("height")) and text.parse_int(
                h["name"].partition(" ")[0]) or 0,
            "author": author.get("name") or "",
        })

        if url_a := author.get("url"):
            media["author_url"] = url_a
            media["author_slug"], _, media["author_id"] = \
                url_a[url_a.rfind("/", 0, -1)+1:-1].rpartition(".")
        else:
            media["author_url"] = ""
            media["author_slug"] = text.slugify(media["author"][15:])
            media["author_id"] = media["author"][15:]

        if ext := main.get("encodingFormat"):
            media["extension"] = ext

        if isinstance(stats, list):
            media["views"] = stats[0]["userInteractionCount"]
            media["likes"] = stats[1]["userInteractionCount"]
            media["comments"] = stats[2]["userInteractionCount"]

        return main["contentUrl"], media

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
    pattern = (BASE_PATTERN + r"(/(?:index\.php\?)?threads"
               r"/[^/?#]+/#?post-|/posts/)(\d+)")
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
    pattern = (BASE_PATTERN + r"(/(?:index\.php\?)?threads"
               r"/(?:[^/?#]+\.)?\d+)(?:/page-(\d+))?")
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
    pattern = (BASE_PATTERN + r"(/(?:index\.php\?)?forums"
               r"/(?:[^/?#]+\.)?[^/?#]+)(?:/page-(\d+))?")
    example = "https://simpcity.cr/forums/TITLE.123/"

    def items(self):
        extract_threads = text.re(
            r'(/(?:index\.php\?)?threads/[^"]+)"[^>]+data-xf-init=').findall

        data = {"_extractor": XenforoThreadExtractor}
        path = self.groups[-2]
        pnum = self.groups[-1]
        for page in self._pagination(path, pnum):
            for path in extract_threads(page):
                yield Message.Queue, self.root + text.unquote(path), data


class XenforoMediaUserExtractor(XenforoExtractor):
    subcategory = "media-user"
    directory_fmt = ("{category}", "Media", "{author_slug}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{id}"
    pattern = (BASE_PATTERN + r"(/(?:index\.php\?)?)me(?:"
               r"dia/users/([^/?#]+)(?:/page-(\d+))?|"
               r"mbers/([^/?#]+)/#xfmgMedia)")
    example = "https://simpcity.cr/media/users/USER.123/"

    def items(self):
        groups = self.groups

        user = groups[-3]
        if user is None:
            user = groups[-1]
            pnum = None
        else:
            pnum = groups[-2]

        if not self.config("metadata"):
            self.kwdict["author_slug"], _, self.kwdict["author_id"] = \
                user.rpartition(".")

        return self.items_media(f"{groups[-4]}media/users/{user}", pnum)


class XenforoMediaCategoryExtractor(XenforoExtractor):
    subcategory = "media-category"
    directory_fmt = ("{category}", "Media", "Category", "{mcategory}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{id}"
    pattern = (BASE_PATTERN + r"(/(?:index\.php\?)?"
               r"media/categories/([^/?#]+))(?:/page-(\d+))?")
    example = "https://simpcity.cr/media/categories/CATEGORY.123/"

    def items(self):
        self.kwdict["mcategory"], _, self.kwdict["mcategory_id"] = \
            self.groups[-2].rpartition(".")
        return self.items_media(self.groups[-3], self.groups[-1])


class XenforoMediaItemExtractor(XenforoExtractor):
    subcategory = "media-item"
    directory_fmt = ("{category}", "Media", "{author_slug|''}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"(/(?:index\.php\?)?media/((?:[^/?#]+\.)\d+))"
    example = "https://simpcity.cr/media/NAME.123/"

    def items(self):
        url = f"{self.root}{self.groups[-2]}/"
        url, media = (self._extract_media_ex if self.config("metadata") else
                      self._extract_media)(url, self.groups[-1])
        yield Message.Directory, "", media
        yield Message.Url, url, media
