# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.bellazon.com/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?bellazon\.com/main"


class BellazonExtractor(Extractor):
    """Base class for bellazon extractors"""
    category = "bellazon"
    root = "https://www.bellazon.com/main"
    directory_fmt = ("{category}", "{thread[section]}",
                     "{thread[title]} ({thread[id]})")
    filename_fmt = "{post[id]}_{num:>02}_{id}_{filename}.{extension}"
    archive_fmt = "{post[id]}/{id}_{filename}"

    def items(self):
        native = (f"{self.root}/", f"{self.root[6:]}/")
        extract_urls = text.re(
            r'(?s)<('
            r'(?:video .*?<source [^>]*?src|a [^>]*?href)="([^"]+).*?</a>'
            r'|img [^>]*?src="([^"]+)"[^>]*>'
            r')'
        ).findall

        if self.config("quoted", False):
            strip_quoted = None
        else:
            strip_quoted = text.re(r"(?s)<blockquote .*?</blockquote>").sub

        for post in self.posts():
            if strip_quoted is None:
                urls = extract_urls(post["content"])
            else:
                urls = extract_urls(strip_quoted("", post["content"]))

            data = {"post": post}
            post["count"] = data["count"] = len(urls)

            yield Message.Directory, "", data
            data["num"] = data["num_internal"] = data["num_external"] = 0
            for info, url, url_img in urls:
                url = text.unescape(url or url_img)

                if url.startswith(native):
                    if (
                        "/uploads/emoticons/" in url or
                        "/profile/" in url or
                        "/topic/" in url
                    ):
                        continue
                    data["num"] += 1
                    data["num_internal"] += 1
                    if not (alt := text.extr(info, ' alt="', '"')) or (
                            alt.startswith("post-") and "_thumb." in alt):
                        dc = text.nameext_from_url(url, data.copy())
                    else:
                        dc = data.copy()
                        dc["name"] = name = text.unescape(alt)
                        dc["filename"] = name.partition(".")[0]

                    dc["id"] = text.extr(info, 'data-fileid="', '"')
                    if ext := text.extr(info, 'data-fileext="', '"'):
                        dc["extension"] = ext
                    elif "/core/interface/file/attachment.php" in url:
                        if not dc["id"]:
                            dc["id"] = \
                                url.rpartition("?id=")[2].partition("&")[0]
                        if name := text.extr(info, ">", "<").strip():
                            dc["name"] = name = text.unescape(name)
                            text.nameext_from_name(name, dc)
                    else:
                        dc["extension"] = text.ext_from_url(url)

                    if url[0] == "/":
                        url = f"https:{url}"
                    yield Message.Url, url, dc

                else:
                    data["num"] += 1
                    data["num_external"] += 1
                    yield Message.Queue, url, data

    def _pagination(self, base, pnum=None):
        base = f"{self.root}{base}"

        if pnum is None:
            url = f"{base}/"
            pnum = 1
        else:
            url = f"{base}/page/{pnum}/"
            pnum = None

        while True:
            page = self.request(url).text

            yield page

            if pnum is None or ' rel="next" ' not in page or text.extr(
                    page, " rel=\"next\" data-page='", "'") == str(pnum):
                return
            pnum += 1
            url = f"{base}/page/{pnum}/"

    def _pagination_reverse(self, base, pnum=None):
        base = f"{self.root}{base}"

        url = f"{base}/page/{'9999' if pnum is None else pnum}/"
        with self.request(url) as response:
            parts = response.url.rsplit("/", 3)
            pnum = text.parse_int(parts[2]) if parts[1] == "page" else 1
            page = response.text

        while True:
            yield page

            pnum -= 1
            if pnum > 1:
                url = f"{base}/page/{pnum}/"
            elif pnum == 1:
                url = f"{base}/"
            else:
                return

            page = self.request(url).text

    def _parse_thread(self, page):
        schema = self._extract_jsonld(page)
        author = schema["author"]
        stats = schema["interactionStatistic"]
        url_t = schema["url"]
        url_a = author.get("url") or ""

        path = text.split_html(text.extr(
            page, '<nav class="ipsBreadcrumb', "</nav>"))[2:-1]

        thread = {
            "url"  : url_t,
            "path" : path,
            "title": schema["headline"],
            "views": stats[0]["userInteractionCount"],
            "posts": stats[1]["userInteractionCount"],
            "date" : self.parse_datetime_iso(schema["datePublished"]),
            "date_updated": self.parse_datetime_iso(schema["dateModified"]),
            "description" : text.unescape(schema["text"]).strip(),
            "section"     : path[-2],
            "author"      : author["name"],
            "author_url"  : url_a,
        }

        thread["id"], _, thread["slug"] = \
            url_t.rsplit("/", 2)[1].partition("-")

        if url_a:
            thread["author_id"], _, thread["author_slug"] = \
                url_a.rsplit("/", 2)[1].partition("-")
        else:
            thread["author_id"] = thread["author_slug"] = ""

        return thread

    def _parse_post(self, html):
        extr = text.extract_from(html)

        post = {
            "id": extr('id="elComment_', '"'),
            "author_url": extr(" href='", "'"),
            "date": self.parse_datetime_iso(extr("datetime='", "'")),
            "content": extr("<!-- Post content -->", "\n\t\t</div>"),
        }

        if (pos := post["content"].find(">")) >= 0:
            post["content"] = post["content"][pos+1:].strip()

        if url_a := post["author_url"]:
            post["author_id"], _, post["author_slug"] = \
                url_a.rsplit("/", 2)[1].partition("-")
        else:
            post["author_id"] = post["author_slug"] = ""

        return post


class BellazonPostExtractor(BellazonExtractor):
    subcategory = "post"
    pattern = (rf"{BASE_PATTERN}(/topic/\d+-[\w-]+(?:/page/\d+)?)"
               rf"/?#(?:findC|c)omment-(\d+)")
    example = "https://www.bellazon.com/main/topic/123-SLUG/#findComment-12345"

    def posts(self):
        path, post_id = self.groups
        page = self.request(f"{self.root}{path}").text

        pos = page.find(f'id="elComment_{post_id}')
        if pos < 0:
            raise exception.NotFoundError("post")
        html = text.extract(page, "<article ", "</article>", pos-100)[0]

        self.kwdict["thread"] = self._parse_thread(page)
        return (self._parse_post(html),)


class BellazonThreadExtractor(BellazonExtractor):
    subcategory = "thread"
    pattern = rf"{BASE_PATTERN}(/topic/\d+-[\w-]+)(?:/page/(\d+))?"
    example = "https://www.bellazon.com/main/topic/123-SLUG/"

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
            posts = text.extract_iter(page, "<article ", "</article>")
            if reverse:
                posts = list(posts)
                posts.reverse()
            for html in posts:
                yield self._parse_post(html)


class BellazonForumExtractor(BellazonExtractor):
    subcategory = "forum"
    pattern = rf"{BASE_PATTERN}(/forum/\d+-[\w-]+)(?:/page/(\d+))?"
    example = "https://www.bellazon.com/main/forum/123-SLUG/"

    def items(self):
        data = {"_extractor": BellazonThreadExtractor}
        for page in self._pagination(*self.groups):
            for row in text.extract_iter(
                    page, '<li data-ips-hook="topicRow"', "</"):
                yield Message.Queue, text.extr(row, 'href="', '"'), data
