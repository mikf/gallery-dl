# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nudostar.com/forum/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache

BASE_PATTERN = r"(?:https?://)?(?:www\.)?nudostar\.com/forum"


class NudostarforumExtractor(Extractor):
    """Base class for nudostar forum extractors"""
    category = "nudostarforum"
    cookies_domain = "nudostar.com"
    cookies_names = ("xf_user",)
    root = "https://nudostar.com/forum"
    directory_fmt = ("{category}", "{thread[title]} ({thread[id]})")
    filename_fmt = "{post[id]}_{num:>02}_{filename}.{extension}"
    archive_fmt = "{post[id]}/{filename}"

    def items(self):
        self.login()

        for post in self.posts():
            internal, external = self._extract_post_urls(post["content"])

            data = {"post": post}
            post["count"] = data["count"] = len(internal) + len(external)
            yield Message.Directory, "", data

            data["num"] = 0
            for url in internal:
                data["num"] += 1
                text.nameext_from_url(url, data)
                yield Message.Url, url, data

            for url in external:
                data["num"] += 1
                yield Message.Queue, url, data

    def _extract_post_urls(self, content):
        """Extract image and video URLs from post content"""
        internal = []
        external = []
        seen = set()

        # Extract URLs from both href= and src= attributes
        for attr in ('href="', 'src="'):
            for url in text.extract_iter(content, attr, '"'):
                if url in seen:
                    continue

                # Internal attachments
                if "/forum/attachments/" in url:
                    # Skip numeric-only IDs and non-file links
                    path = url.rstrip("/")
                    if path.split(".")[-1].isdigit() and "-" not in path:
                        continue
                    if "upload?" in url:
                        continue
                    seen.add(url)
                    # Normalize to full URL
                    if url.startswith("/"):
                        url = "https://nudostar.com" + url
                    internal.append(url)

                # External image hosts
                elif url.startswith("http") and "nudostar.com" not in url:
                    seen.add(url)
                    external.append(url)

        return internal, external

    def request_page(self, url):
        try:
            return self.request(url)
        except exception.HttpError as exc:
            if exc.status == 403:
                raise exception.AuthRequired(
                    ("username & password", "authenticated cookies"), None,
                    "Login required to view this content")
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

        url = f"{self.root}/login/"
        page = self.request(url).text
        token = text.extr(page, 'name="_xfToken" value="', '"')

        url = f"{self.root}/login/login"
        data = {
            "_xfToken" : token,
            "login"    : username,
            "password" : password,
            "remember" : "1",
            "_xfRedirect": self.root + "/",
        }
        response = self.request(url, method="POST", data=data)

        if not response.history or "xf_user" not in response.cookies:
            raise exception.AuthenticationError()

        return {
            cookie.name: cookie.value
            for cookie in self.cookies
            if cookie.domain.endswith(self.cookies_domain)
        }

    def _pagination(self, base, pnum=None):
        if pnum is None:
            url = f"{self.root}{base}/"
            pnum = 1
        else:
            url = f"{self.root}{base}/page-{pnum}"
            pnum = None

        while True:
            page = self.request_page(url).text
            yield page

            if pnum is None or "pageNav-jump--next" not in page:
                return
            pnum += 1
            url = f"{self.root}{base}/page-{pnum}"

    def _parse_thread(self, page):
        extr = text.extract_from(page)

        title = text.unescape(extr("<title>", "<"))
        if " | " in title:
            title = title.rpartition(" | ")[0]

        thread_id = extr('data-content-key="thread-', '"')

        return {
            "id"   : thread_id,
            "title": title.strip(),
        }

    def _parse_post(self, html):
        extr = text.extract_from(html)

        return {
            "author": extr('data-author="', '"'),
            "id"    : extr('data-content="post-', '"'),
            "date"  : extr('datetime="', '"'),
            "content": html,  # Pass full article HTML for URL extraction
        }


class NudostarforumPostExtractor(NudostarforumExtractor):
    """Extractor for individual posts on nudostar forum"""
    subcategory = "post"
    pattern = (rf"{BASE_PATTERN}"
               rf"/threads/[^/?#]+\.(\d+)/post-(\d+)")
    example = "https://nudostar.com/forum/threads/NAME.12345/post-67890"

    def posts(self):
        thread_id, post_id = self.groups
        url = f"{self.root}/posts/{post_id}/"
        page = self.request_page(url).text

        pos = page.find(f'data-content="post-{post_id}"')
        if pos < 0:
            raise exception.NotFoundError("post")
        html = text.extract(page, "<article ", "</article>", pos-200)[0]

        self.kwdict["thread"] = self._parse_thread(page)
        return (self._parse_post(html),)


class NudostarforumThreadExtractor(NudostarforumExtractor):
    """Extractor for threads on nudostar forum"""
    subcategory = "thread"
    pattern = rf"{BASE_PATTERN}(/threads/[^/?#]+\.(\d+))(?:/page-(\d+))?"
    example = "https://nudostar.com/forum/threads/NAME.12345/"

    def posts(self):
        path, thread_id, pnum = self.groups

        for page in self._pagination(path, pnum):
            if "thread" not in self.kwdict:
                self.kwdict["thread"] = self._parse_thread(page)

            for html in text.extract_iter(page, "<article ", "</article>"):
                yield self._parse_post(html)
