# -*- coding: utf-8 -*-

# Copyright 2018-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.newgrounds.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache
import itertools
import re


class NewgroundsExtractor(Extractor):
    """Base class for newgrounds extractors"""
    category = "newgrounds"
    directory_fmt = ("{category}", "{artist[:10]:J, }")
    filename_fmt = "{category}_{_index}_{title}.{extension}"
    archive_fmt = "{_type}{_index}"
    root = "https://www.newgrounds.com"
    cookies_domain = ".newgrounds.com"
    cookies_names = ("NG_GG_username", "vmk1du5I8m")
    request_interval = (0.5, 1.5)

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)
        self.user_root = "https://{}.newgrounds.com".format(self.user)

    def _init(self):
        self._extract_comment_urls = re.compile(
            r'(?:<img |data-smartload-)src="([^"]+)').findall
        self.flash = self.config("flash", True)

        fmt = self.config("format")
        if not fmt or fmt == "original":
            self.format = ("mp4", "webm", "m4v", "mov", "mkv",
                           1080, 720, 360)
        elif isinstance(fmt, (list, tuple)):
            self.format = fmt
        else:
            self._video_formats = self._video_formats_limit
            self.format = (fmt if isinstance(fmt, int) else
                           text.parse_int(fmt.rstrip("p")))

    def items(self):
        self.login()
        metadata = self.metadata()

        for post_url in self.posts():
            try:
                post = self.extract_post(post_url)
                url = post.get("url")
            except Exception as exc:
                self.log.debug("", exc_info=exc)
                url = None

            if url:
                if metadata:
                    post.update(metadata)
                yield Message.Directory, post
                post["num"] = 0
                yield Message.Url, url, text.nameext_from_url(url, post)

                if "_multi" in post:
                    for data in post["_multi"]:
                        post["num"] += 1
                        post["_index"] = "{}_{:>02}".format(
                            post["index"], post["num"])
                        post.update(data)
                        url = data["image"]

                        text.nameext_from_url(url, post)
                        yield Message.Url, url, post

                        if "_fallback" in post:
                            del post["_fallback"]

                for url in self._extract_comment_urls(post["_comment"]):
                    post["num"] += 1
                    post["_index"] = "{}_{:>02}".format(
                        post["index"], post["num"])
                    url = text.ensure_http_scheme(url)
                    text.nameext_from_url(url, post)
                    yield Message.Url, url, post
            else:
                self.log.warning(
                    "Unable to get download URL for '%s'", post_url)

    def posts(self):
        """Return URLs of all relevant post pages"""
        return self._pagination(self._path)

    def metadata(self):
        """Return general metadata"""

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            self.cookies_update(self._login_impl(username, password))

    @cache(maxage=365*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = self.root + "/passport"
        response = self.request(url)
        if response.history and response.url.endswith("/social"):
            return self.cookies

        page = response.text
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.root,
            "Referer": url,
        }
        url = text.urljoin(self.root, text.extr(page, 'action="', '"'))
        data = {
            "auth"    : text.extr(page, 'name="auth" value="', '"'),
            "remember": "1",
            "username": username,
            "password": str(password),
            "code"    : "",
            "codehint": "------",
            "mfaCheck": "1",
        }

        while True:
            response = self.request(
                url, method="POST", headers=headers, data=data)
            result = response.json()

            if result.get("success"):
                break
            if "errors" in result:
                raise exception.AuthenticationError(
                    '"' + '", "'.join(result["errors"]) + '"')

            if result.get("requiresMfa"):
                data["code"] = self.input("Verification Code: ")
                data["codehint"] = "      "
            elif result.get("requiresEmailMfa"):
                email = result.get("obfuscatedEmail")
                prompt = "Email Verification Code ({}): ".format(email)
                data["code"] = self.input(prompt)
                data["codehint"] = "      "

            data.pop("mfaCheck", None)

        return {
            cookie.name: cookie.value
            for cookie in response.cookies
        }

    def extract_post(self, post_url):
        url = post_url
        if "/art/view/" in post_url:
            extract_data = self._extract_image_data
        elif "/audio/listen/" in post_url:
            extract_data = self._extract_audio_data
        else:
            extract_data = self._extract_media_data
            if self.flash:
                url += "/format/flash"

        response = self.request(url, fatal=False)
        page = response.text

        pos = page.find('id="adults_only"')
        if pos >= 0:
            msg = text.extract(page, 'class="highlight">', '<', pos)[0]
            self.log.warning('"%s"', msg)
            return {}

        if response.status_code >= 400:
            return {}

        extr = text.extract_from(page)
        data = extract_data(extr, post_url)

        data["_comment"] = extr(
            'id="author_comments"', '</div>').partition(">")[2]
        data["comment"] = text.unescape(text.remove_html(
            data["_comment"], "", ""))
        data["favorites"] = text.parse_int(extr(
            'id="faves_load">', '<').replace(",", ""))
        data["score"] = text.parse_float(extr('id="score_number">', '<'))
        data["tags"] = text.split_html(extr('<dd class="tags">', '</dd>'))
        data["artist"] = [
            text.extr(user, '//', '.')
            for user in text.extract_iter(page, '<div class="item-user">', '>')
        ]

        data["tags"].sort()
        data["user"] = self.user or data["artist"][0]
        data["post_url"] = post_url
        return data

    def _extract_image_data(self, extr, url):
        full = text.extract_from(util.json_loads(extr(
            '"full_image_text":', '});')))
        data = {
            "title"      : text.unescape(extr('"og:title" content="', '"')),
            "description": text.unescape(extr(':description" content="', '"')),
            "type"       : extr('og:type" content="', '"'),
            "_type"      : "i",
            "date"       : text.parse_datetime(extr(
                'itemprop="datePublished" content="', '"')),
            "rating"     : extr('class="rated-', '"'),
            "url"        : full('src="', '"'),
            "width"      : text.parse_int(full('width="', '"')),
            "height"     : text.parse_int(full('height="', '"')),
        }
        index = data["url"].rpartition("/")[2].partition("_")[0]
        data["index"] = text.parse_int(index)
        data["_index"] = index

        image_data = extr("let imageData =", "\n];")
        if image_data:
            data["_multi"] = self._extract_images_multi(image_data)
        else:
            art_images = extr('<div class="art-images', '\n</div>')
            if art_images:
                data["_multi"] = self._extract_images_art(art_images, data)

        return data

    def _extract_images_multi(self, html):
        data = util.json_loads(html + "]")
        yield from data[1:]

    def _extract_images_art(self, html, data):
        ext = text.ext_from_url(data["url"])
        for url in text.extract_iter(html, 'data-smartload-src="', '"'):
            url = text.ensure_http_scheme(url)
            url = url.replace("/medium_views/", "/images/", 1)
            if text.ext_from_url(url) == "webp":
                fallback = [url.replace(".webp", "." + e)
                            for e in ("jpg", "png", "gif") if e != ext]
                fallback.append(url)
                yield {
                    "image"    : url.replace(".webp", "." + ext),
                    "_fallback": fallback,
                }
            else:
                yield {"image": url}

    @staticmethod
    def _extract_audio_data(extr, url):
        index = url.split("/")[5]
        return {
            "title"      : text.unescape(extr('"og:title" content="', '"')),
            "description": text.unescape(extr(':description" content="', '"')),
            "type"       : extr('og:type" content="', '"'),
            "_type"      : "a",
            "date"       : text.parse_datetime(extr(
                'itemprop="datePublished" content="', '"')),
            "url"        : extr('{"url":"', '"').replace("\\/", "/"),
            "index"      : text.parse_int(index),
            "_index"     : index,
            "rating"     : "",
        }

    def _extract_media_data(self, extr, url):
        index = url.split("/")[5]
        title = extr('"og:title" content="', '"')
        type = extr('og:type" content="', '"')
        descr = extr('"og:description" content="', '"')
        src = extr('{"url":"', '"')

        if src:
            src = src.replace("\\/", "/")
            formats = ()
            date = text.parse_datetime(extr(
                'itemprop="datePublished" content="', '"'))
        else:
            url = self.root + "/portal/video/" + index
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
            }
            sources = self.request(url, headers=headers).json()["sources"]
            formats = self._video_formats(sources)
            src = next(formats, "")
            date = text.parse_timestamp(src.rpartition("?")[2])

        return {
            "title"      : text.unescape(title),
            "url"        : src,
            "date"       : date,
            "type"       : type,
            "_type"      : "",
            "description": text.unescape(descr or extr(
                'itemprop="description" content="', '"')),
            "rating"     : extr('class="rated-', '"'),
            "index"      : text.parse_int(index),
            "_index"     : index,
            "_fallback"  : formats,
        }

    def _video_formats(self, sources):
        src = sources["360p"][0]["src"]
        sub = re.compile(r"\.360p\.\w+").sub

        for fmt in self.format:
            try:
                if isinstance(fmt, int):
                    yield sources[str(fmt) + "p"][0]["src"]
                elif fmt in sources:
                    yield sources[fmt][0]["src"]
                else:
                    yield sub("." + fmt, src, 1)
            except Exception as exc:
                self.log.debug("Video format '%s' not available (%s: %s)",
                               fmt, exc.__class__.__name__, exc)

    def _video_formats_limit(self, sources):
        formats = []
        for fmt, src in sources.items():
            width = text.parse_int(fmt.rstrip("p"))
            if width <= self.format:
                formats.append((width, src))

        formats.sort(reverse=True)
        for fmt in formats:
            yield fmt[1][0]["src"]

    def _pagination(self, kind):
        url = "{}/{}".format(self.user_root, kind)
        params = {
            "page": 1,
            "isAjaxRequest": "1",
        }
        headers = {
            "Referer": url,
            "X-Requested-With": "XMLHttpRequest",
        }

        while True:
            with self.request(
                    url, params=params, headers=headers,
                    fatal=False) as response:
                try:
                    data = response.json()
                except ValueError:
                    return
                if not data:
                    return
                if "errors" in data:
                    msg = ", ".join(text.unescape(e) for e in data["errors"])
                    raise exception.StopExtraction(msg)

            items = data.get("items")
            if not items:
                return

            for year, items in items.items():
                for item in items:
                    page_url = text.extr(item, 'href="', '"')
                    if page_url[0] == "/":
                        page_url = self.root + page_url
                    yield page_url

            more = data.get("load_more")
            if not more or len(more) < 8:
                return
            params["page"] += 1


class NewgroundsImageExtractor(NewgroundsExtractor):
    """Extractor for a single image from newgrounds.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:"
               r"(?:www\.)?newgrounds\.com/art/view/([^/?#]+)/[^/?#]+"
               r"|art\.ngfiles\.com/images/\d+/\d+_([^_]+)_([^.]+))")
    example = "https://www.newgrounds.com/art/view/USER/TITLE"

    def __init__(self, match):
        NewgroundsExtractor.__init__(self, match)
        if match.group(2):
            self.user = match.group(2)
            self.post_url = "https://www.newgrounds.com/art/view/{}/{}".format(
                self.user, match.group(3))
        else:
            self.post_url = text.ensure_http_scheme(match.group(0))

    def posts(self):
        return (self.post_url,)


class NewgroundsMediaExtractor(NewgroundsExtractor):
    """Extractor for a media file from newgrounds.com"""
    subcategory = "media"
    pattern = (r"(?:https?://)?(?:www\.)?newgrounds\.com"
               r"(/(?:portal/view|audio/listen)/\d+)")
    example = "https://www.newgrounds.com/portal/view/12345"

    def __init__(self, match):
        NewgroundsExtractor.__init__(self, match)
        self.user = ""
        self.post_url = self.root + match.group(1)

    def posts(self):
        return (self.post_url,)


class NewgroundsArtExtractor(NewgroundsExtractor):
    """Extractor for all images of a newgrounds user"""
    subcategory = _path = "art"
    pattern = r"(?:https?://)?([\w-]+)\.newgrounds\.com/art/?$"
    example = "https://USER.newgrounds.com/art"


class NewgroundsAudioExtractor(NewgroundsExtractor):
    """Extractor for all audio submissions of a newgrounds user"""
    subcategory = _path = "audio"
    pattern = r"(?:https?://)?([\w-]+)\.newgrounds\.com/audio/?$"
    example = "https://USER.newgrounds.com/audio"


class NewgroundsMoviesExtractor(NewgroundsExtractor):
    """Extractor for all movies of a newgrounds user"""
    subcategory = _path = "movies"
    pattern = r"(?:https?://)?([\w-]+)\.newgrounds\.com/movies/?$"
    example = "https://USER.newgrounds.com/movies"


class NewgroundsGamesExtractor(NewgroundsExtractor):
    """Extractor for a newgrounds user's games"""
    subcategory = _path = "games"
    pattern = r"(?:https?://)?([\w-]+)\.newgrounds\.com/games/?$"
    example = "https://USER.newgrounds.com/games"


class NewgroundsUserExtractor(NewgroundsExtractor):
    """Extractor for a newgrounds user profile"""
    subcategory = "user"
    pattern = r"(?:https?://)?([\w-]+)\.newgrounds\.com/?$"
    example = "https://USER.newgrounds.com"

    def initialize(self):
        pass

    def items(self):
        base = self.user_root + "/"
        return self._dispatch_extractors((
            (NewgroundsArtExtractor   , base + "art"),
            (NewgroundsAudioExtractor , base + "audio"),
            (NewgroundsGamesExtractor , base + "games"),
            (NewgroundsMoviesExtractor, base + "movies"),
        ), ("art",))


class NewgroundsFavoriteExtractor(NewgroundsExtractor):
    """Extractor for posts favorited by a newgrounds user"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "{user}", "Favorites")
    pattern = (r"(?:https?://)?([\w-]+)\.newgrounds\.com"
               r"/favorites(?!/following)(?:/(art|audio|movies))?/?")
    example = "https://USER.newgrounds.com/favorites"

    def __init__(self, match):
        NewgroundsExtractor.__init__(self, match)
        self.kind = match.group(2)

    def posts(self):
        if self.kind:
            return self._pagination(self.kind)
        return itertools.chain.from_iterable(
            self._pagination(k) for k in ("art", "audio", "movies")
        )

    def _pagination(self, kind):
        url = "{}/favorites/{}".format(self.user_root, kind)
        params = {
            "page": 1,
            "isAjaxRequest": "1",
        }
        headers = {
            "Referer": url,
            "X-Requested-With": "XMLHttpRequest",
        }

        while True:
            response = self.request(url, params=params, headers=headers)
            if response.history:
                return

            data = response.json()
            favs = self._extract_favorites(data.get("component") or "")
            yield from favs

            if len(favs) < 24:
                return
            params["page"] += 1

    def _extract_favorites(self, page):
        return [
            self.root + path
            for path in text.extract_iter(
                page, 'href="https://www.newgrounds.com', '"')
        ]


class NewgroundsFollowingExtractor(NewgroundsFavoriteExtractor):
    """Extractor for a newgrounds user's favorited users"""
    subcategory = "following"
    pattern = r"(?:https?://)?([\w-]+)\.newgrounds\.com/favorites/(following)"
    example = "https://USER.newgrounds.com/favorites/following"

    def items(self):
        data = {"_extractor": NewgroundsUserExtractor}
        for url in self._pagination(self.kind):
            yield Message.Queue, url, data

    @staticmethod
    def _extract_favorites(page):
        return [
            text.ensure_http_scheme(user.rpartition('"')[2])
            for user in text.extract_iter(page, 'class="item-user', '"><img')
        ]


class NewgroundsSearchExtractor(NewgroundsExtractor):
    """Extractor for newgrounds.com search reesults"""
    subcategory = "search"
    directory_fmt = ("{category}", "search", "{search_tags}")
    pattern = (r"(?:https?://)?(?:www\.)?newgrounds\.com"
               r"/search/conduct/([^/?#]+)/?\?([^#]+)")
    example = "https://www.newgrounds.com/search/conduct/art?terms=QUERY"

    def __init__(self, match):
        NewgroundsExtractor.__init__(self, match)
        self._path, query = match.groups()
        self.query = text.parse_query(query)

    def posts(self):
        suitabilities = self.query.get("suitabilities")
        if suitabilities:
            data = {"view_suitability_" + s: "on"
                    for s in suitabilities.split(",")}
            self.request(self.root + "/suitabilities",
                         method="POST", data=data)
        return self._pagination("/search/conduct/" + self._path, self.query)

    def metadata(self):
        return {"search_tags": self.query.get("terms", "")}

    def _pagination(self, path, params):
        url = self.root + path
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
        }
        params["inner"] = "1"
        params["page"] = 1

        while True:
            data = self.request(url, params=params, headers=headers).json()

            post_url = None
            for post_url in text.extract_iter(data["content"], 'href="', '"'):
                if not post_url.startswith("/search/"):
                    yield post_url

            if post_url is None:
                return
            params["page"] += 1
