# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.toongod.org/

This site uses Cloudflare protection. You have two options:

1. Use FlareSolverr (recommended):
   - Install:
     docker run -d -p 8191:8191 ghcr.io/flaresolverr/flaresolverr
   - Configure: Add to gallery-dl config:
     {
       "extractor": {
         "toongod": {
           "flaresolverr-url": "http://localhost:8191/v1"
         }
       }
     }

2. Use browser cookies:
   - Export cookies from your browser after visiting toongod.org
   - Use: gallery-dl --cookies cookies.txt <url>
"""

from .common import Extractor, ChapterExtractor, MangaExtractor
from .. import text, exception
import requests

BASE_PATTERN = r"(?:https?://)?(?:www\.)?toongod\.org"


class _FlaresolverrResponse:
    """Mock response object for FlareSolverr results"""
    __slots__ = ("text", "content", "status_code", "headers", "url")

    def __init__(self, solution):
        self.text = solution["response"]
        self.content = self.text.encode("utf-8")
        self.status_code = solution["status"]
        self.headers = solution.get("headers", {})
        self.url = solution["url"]


class ToongodBase():
    """Base class for toongod extractors"""
    category = "toongod"
    root = "https://www.toongod.org"
    cookies_domain = ".toongod.org"
    cookies_names = ("cf_clearance",)
    _flaresolverr_session = None

    def request(self, url, **kwargs):
        flaresolverr_url = self.config("flaresolverr-url")
        if flaresolverr_url:
            return self._request_with_flaresolverr(url, flaresolverr_url)

        headers = kwargs.setdefault("headers", {})
        headers.setdefault("Referer", self.root + "/")
        return Extractor.request(self, url, **kwargs)

    def _get_or_create_session(self, flaresolverr_url):
        """Get or create a FlareSolverr session for cookie reuse"""
        if ToongodBase._flaresolverr_session:
            return ToongodBase._flaresolverr_session

        self.log.debug("Creating FlareSolverr session")
        payload = {"cmd": "sessions.create"}

        try:
            response = requests.post(
                flaresolverr_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get("status") == "ok":
                session_id = result["session"]
                ToongodBase._flaresolverr_session = session_id
                self.log.info("Created FlareSolverr session: %s", session_id)
                return session_id
            else:
                self.log.warning(
                    "Failed to create session, will use one-off requests")
                return None

        except Exception as exc:
            self.log.warning("Session creation failed: %s", exc)
            return None

    def _request_with_flaresolverr(self, url, flaresolverr_url):
        """Use FlareSolverr to bypass Cloudflare with session support"""
        session_id = self._get_or_create_session(flaresolverr_url)

        payload = {
            "cmd": "request.get",
            "url": url,
            "maxTimeout": 60000,
        }

        if session_id:
            payload["session"] = session_id
            self.log.debug("Using FlareSolverr session: %s", session_id)
        else:
            self.log.debug("Using FlareSolverr without session")

        try:
            response = requests.post(
                flaresolverr_url, json=payload, timeout=65)
            response.raise_for_status()
            result = response.json()

            if result.get("status") != "ok":
                msg = result.get("message", "Unknown error")
                raise exception.HttpError(
                    "FlareSolverr failed: " + msg)

            return _FlaresolverrResponse(result["solution"])

        except requests.exceptions.RequestException as exc:
            self.log.error("FlareSolverr request failed: %s", exc)
            raise exception.HttpError("FlareSolverr unavailable: " + str(exc))


class ToongodChapterExtractor(ToongodBase, ChapterExtractor):
    """Extractor for toongod webtoon chapters"""
    pattern = BASE_PATTERN + r"/webtoon/([^/]+)/chapter-([\d.]+)/?"
    example = "https://www.toongod.org/webtoon/SLUG/chapter-1/"

    def __init__(self, match):
        self.slug, self.chapter = match.groups()
        url = "{}/webtoon/{}/chapter-{}/".format(
            self.root, self.slug, self.chapter)
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        title = (text.extr(page, "<h1>", "</h1>") or
                 text.extr(page, 'property="og:title" content="', '"'))

        if title and " - " in title:
            manga = title.split(" - ")[0]
        else:
            manga = self.slug.replace("-", " ").title()

        return {
            "manga"        : manga,
            "slug"         : self.slug,
            "chapter"      : text.parse_int(self.chapter),
            "chapter_minor": "",
            "title"        : "",
        }

    def images(self, page):
        return [
            (clean_url, None)
            for url in text.extract_iter(page, 'data-src="', '"')
            if (clean_url := url.strip()).startswith("http") and
            "tngcdn.com/manga_" in clean_url
        ]


class ToongodWebtoonExtractor(ToongodBase, MangaExtractor):
    """Extractor for toongod webtoons"""
    chapterclass = ToongodChapterExtractor
    pattern = BASE_PATTERN + r"/webtoon/([^/?#]+)/?$"
    example = "https://www.toongod.org/webtoon/SLUG"

    def __init__(self, match):
        self.slug = match.group(1)
        url = "{}/webtoon/{}/".format(self.root, self.slug)
        MangaExtractor.__init__(self, match, url)

    def chapters(self, page):
        manga = (text.extr(page, "<h1>", "</h1>") or
                 text.extr(page, 'property="og:title" content="', '"'))

        chapter_list = (
            text.extr(page, 'class="wp-manga-chapter', '</ul>') or
            text.extr(page, 'id="chapter-list', '</ul>') or "")

        results = []
        for url in text.extract_iter(chapter_list, '<a href="', '"'):
            if "/chapter-" not in url:
                continue
            chapter = text.extr(url, "/chapter-", "/")
            if chapter:
                results.append((url, {
                    "manga"        : manga,
                    "chapter"      : text.parse_int(chapter),
                    "chapter_minor": "",
                }))
        return results
