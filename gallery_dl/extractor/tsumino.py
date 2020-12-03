# -*- coding: utf-8 -*-

# Copyright 2019-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.tsumino.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, exception
from ..cache import cache


class TsuminoBase():
    """Base class for tsumino extractors"""
    category = "tsumino"
    cookiedomain = "www.tsumino.com"
    root = "https://www.tsumino.com"

    def login(self):
        username, password = self._get_auth_info()
        if username:
            self._update_cookies(self._login_impl(username, password))
        else:
            self.session.cookies.setdefault(
                "ASP.NET_SessionId", "x1drgggilez4cpkttneukrc5")

    @cache(maxage=14*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)
        url = "{}/Account/Login".format(self.root)
        headers = {"Referer": url}
        data = {"Username": username, "Password": password}

        response = self.request(url, method="POST", headers=headers, data=data)
        if not response.history:
            raise exception.AuthenticationError()
        return self.session.cookies


class TsuminoGalleryExtractor(TsuminoBase, GalleryExtractor):
    """Extractor for image galleries on tsumino.com"""
    pattern = (r"(?i)(?:https?://)?(?:www\.)?tsumino\.com"
               r"/(?:entry|Book/Info|Read/(?:Index|View))/(\d+)")
    test = (
        ("https://www.tsumino.com/entry/40996", {
            "pattern": r"https://content.tsumino.com/parts/40996/\d+\?key=\w+",
            "keyword": {
                "title"     : r"re:Shikoshiko Daisuki Nightingale \+ Kaijou",
                "title_en"  : r"re:Shikoshiko Daisuki Nightingale \+ Kaijou",
                "title_jp"  : "シコシコ大好きナイチンゲール + 会場限定おまけ本",
                "gallery_id": 40996,
                "date"      : "dt:2018-06-29 00:00:00",
                "count"     : 42,
                "collection": "",
                "artist"    : ["Itou Life"],
                "group"     : ["Itou Life"],
                "parody"    : list,
                "characters": list,
                "tags"      : list,
                "type"      : "Doujinshi",
                "rating"    : float,
                "uploader"  : "sehki",
                "lang"      : "en",
                "language"  : "English",
                "thumbnail" : "https://content.tsumino.com/thumbs/40996/1",
            },
        }),
        ("https://www.tsumino.com/Book/Info/40996"),
        ("https://www.tsumino.com/Read/View/45834"),
        ("https://www.tsumino.com/Read/Index/45834"),
    )

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = "{}/entry/{}".format(self.root, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)
        title = extr('"og:title" content="', '"')
        title_en, _, title_jp = text.unescape(title).partition("/")
        title_en = title_en.strip()
        title_jp = title_jp.strip()

        return {
            "gallery_id": text.parse_int(self.gallery_id),
            "title"     : title_en or title_jp,
            "title_en"  : title_en,
            "title_jp"  : title_jp,
            "thumbnail" : extr('"og:image" content="', '"'),
            "uploader"  : text.remove_html(extr('id="Uploader">', '</div>')),
            "date"      : text.parse_datetime(
                extr('id="Uploaded">', '</div>').strip(), "%Y %B %d"),
            "rating"    : text.parse_float(extr(
                'id="Rating">', '</div>').partition(" ")[0]),
            "type"      : text.remove_html(extr('id="Category">'  , '</div>')),
            "collection": text.remove_html(extr('id="Collection">', '</div>')),
            "group"     : text.split_html(extr('id="Group">'      , '</div>')),
            "artist"    : text.split_html(extr('id="Artist">'     , '</div>')),
            "parody"    : text.split_html(extr('id="Parody">'     , '</div>')),
            "characters": text.split_html(extr('id="Character">'  , '</div>')),
            "tags"      : text.split_html(extr('id="Tag">'        , '</div>')),
            "language"  : "English",
            "lang"      : "en",
        }

    def images(self, page):
        url = "{}/Read/Index/{}?page=1".format(self.root, self.gallery_id)
        headers = {"Referer": self.gallery_url}
        response = self.request(url, headers=headers, fatal=False)

        if "/Auth/" in response.url:
            raise exception.StopExtraction(
                "Failed to get gallery JSON data. Visit '%s' in a browser "
                "and solve the CAPTCHA to continue.", response.url)

        page = response.text
        tpl, pos = text.extract(page, 'data-cdn="', '"')
        cnt, pos = text.extract(page, '> of ', '<', pos)
        base, _, params = text.unescape(tpl).partition("[PAGE]")

        return [
            (base + str(i) + params, None)
            for i in range(1, text.parse_int(cnt)+1)
        ]


class TsuminoSearchExtractor(TsuminoBase, Extractor):
    """Extractor for search results on tsumino.com"""
    subcategory = "search"
    pattern = (r"(?i)(?:https?://)?(?:www\.)?tsumino\.com"
               r"/(?:Books/?)?#(.+)")
    test = (
        ("https://www.tsumino.com/Books#?Character=Reimu+Hakurei", {
            "pattern": TsuminoGalleryExtractor.pattern,
            "range": "1-40",
            "count": 40,
        }),
        (("http://www.tsumino.com/Books#~(Tags~(~"
          "(Type~7~Text~'Reimu*20Hakurei~Exclude~false)~"
          "(Type~'1~Text~'Pantyhose~Exclude~false)))#"), {
            "pattern": TsuminoGalleryExtractor.pattern,
            "count": ">= 3",
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.query = match.group(1)

    def items(self):
        yield Message.Version, 1
        for gallery in self.galleries():
            url = "{}/entry/{}".format(self.root, gallery["id"])
            gallery["_extractor"] = TsuminoGalleryExtractor
            yield Message.Queue, url, gallery

    def galleries(self):
        """Return all gallery results matching 'self.query'"""
        url = "{}/Search/Operate?type=Book".format(self.root)
        headers = {
            "Referer": "{}/".format(self.root),
            "X-Requested-With": "XMLHttpRequest",
        }
        data = {
            "PageNumber": 1,
            "Text": "",
            "Sort": "Newest",
            "List": "0",
            "Length": "0",
            "MinimumRating": "0",
            "ExcludeList": "0",
            "CompletelyExcludeHated": "false",
        }
        data.update(self._parse(self.query))

        while True:
            info = self.request(
                url, method="POST", headers=headers, data=data).json()

            for gallery in info["data"]:
                yield gallery["entry"]

            if info["pageNumber"] >= info["pageCount"]:
                return
            data["PageNumber"] += 1

    def _parse(self, query):
        try:
            if query.startswith("?"):
                return self._parse_simple(query)
            return self._parse_jsurl(query)
        except Exception as exc:
            raise exception.StopExtraction(
                "Invalid search query '%s' (%s)", query, exc)

    @staticmethod
    def _parse_simple(query):
        """Parse search query with format '?<key>=value>'"""
        key, _, value = query.partition("=")
        tag_types = {
            "Tag": "1",
            "Category": "2",
            "Collection": "3",
            "Group": "4",
            "Artist": "5",
            "Parody": "6",
            "Character": "7",
            "Uploader": "100",
        }

        return {
            "Tags[0][Type]": tag_types[key[1:].capitalize()],
            "Tags[0][Text]": text.unquote(value).replace("+", " "),
            "Tags[0][Exclude]": "false",
        }

    @staticmethod
    def _parse_jsurl(data):
        """Parse search query in JSURL format

        Nested lists and dicts are handled in a special way to deal
        with the way Tsumino expects its parameters -> expand(...)

        Example: ~(name~'John*20Doe~age~42~children~(~'Mary~'Bill))
        Ref: https://github.com/Sage/jsurl
        """
        if not data:
            return {}
        i = 0
        imax = len(data)

        def eat(expected):
            nonlocal i

            if data[i] != expected:
                error = "bad JSURL syntax: expected '{}', got {}".format(
                    expected, data[i])
                raise ValueError(error)
            i += 1

        def decode():
            nonlocal i

            beg = i
            result = ""

            while i < imax:
                ch = data[i]

                if ch not in "~)*!":
                    i += 1

                elif ch == "*":
                    if beg < i:
                        result += data[beg:i]
                    if data[i + 1] == "*":
                        result += chr(int(data[i+2:i+6], 16))
                        i += 6
                    else:
                        result += chr(int(data[i+1:i+3], 16))
                        i += 3
                    beg = i

                elif ch == "!":
                    if beg < i:
                        result += data[beg:i]
                    result += "$"
                    i += 1
                    beg = i

                else:
                    break

            return result + data[beg:i]

        def parse_one():
            nonlocal i

            eat('~')
            result = ""
            ch = data[i]

            if ch == "(":
                i += 1

                if data[i] == "~":
                    result = []
                    if data[i+1] == ")":
                        i += 1
                    else:
                        result.append(parse_one())
                        while data[i] == "~":
                            result.append(parse_one())

                else:
                    result = {}

                    if data[i] != ")":
                        while True:
                            key = decode()
                            value = parse_one()
                            for ekey, evalue in expand(key, value):
                                result[ekey] = evalue
                            if data[i] != "~":
                                break
                            i += 1
                eat(")")

            elif ch == "'":
                i += 1
                result = decode()

            else:
                beg = i
                i += 1

                while i < imax and data[i] not in "~)":
                    i += 1

                sub = data[beg:i]
                if ch in "0123456789-":
                    fval = float(sub)
                    ival = int(fval)
                    result = ival if ival == fval else fval
                else:
                    if sub not in ("true", "false", "null"):
                        raise ValueError("bad value keyword: " + sub)
                    result = sub

            return result

        def expand(key, value):
            if isinstance(value, list):
                for index, cvalue in enumerate(value):
                    ckey = "{}[{}]".format(key, index)
                    yield from expand(ckey, cvalue)
            elif isinstance(value, dict):
                for ckey, cvalue in value.items():
                    ckey = "{}[{}]".format(key, ckey)
                    yield from expand(ckey, cvalue)
            else:
                yield key, value

        return parse_one()
