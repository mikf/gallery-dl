# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.tsumino.com/"""

from .common import ChapterExtractor, Extractor, Message
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

    @cache(maxage=14*24*60*60, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)
        url = "{}/Account/Login".format(self.root)
        headers = {"Referer": url}
        data = {"Username": username, "Password": password}

        response = self.request(url, method="POST", headers=headers, data=data)
        if not response.history:
            raise exception.AuthenticationError()
        return {".aotsumino": response.history[0].cookies[".aotsumino"]}


class TsuminoGalleryExtractor(TsuminoBase, ChapterExtractor):
    """Extractor for image galleries on tsumino.com"""
    subcategory = "gallery"
    filename_fmt = "{category}_{gallery_id}_{page:>03}.{extension}"
    directory_fmt = ["{category}", "{gallery_id} {title}"]
    archive_fmt = "{gallery_id}_{page}"

    pattern = [r"(?i)(?:https?://)?(?:www\.)?tsumino\.com"
               r"/(?:Book/Info|Read/View)/(\d+)"]
    test = [
        ("https://www.tsumino.com/Book/Info/45834", {
            "url": "ed3e39bc21221fbd21b9a2ba711e8decb6fdc6bc",
            "keyword": {
                "artist": "Itou Life",
                "characters": "Carmilla, Gudako, Gudao, Lancelot, Nightingale",
                "collection": "",
                "count": 42,
                "date": "2019 January 27",
                "gallery_id": 45834,
                "group": "Itou Life",
                "lang": "en",
                "language": "English",
                "page": int,
                "parodies": "Fate/Grand Order",
                "rating": float,
                "tags": str,
                "thumbnail": "http://www.tsumino.com/Image/Thumb/45834",
                "title": r"re:\[Remove\] Shikoshiko Daisuki Nightingale",
                "title_jp": "シコシコ大好きナイチンゲール + 会場限定おまけ本",
                "type": "Doujinshi",
                "uploader": "NHNL1"
            },
        }),
        ("https://www.tsumino.com/Read/View/45834", None),
    ]

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = "{}/Book/Info/{}".format(self.root, self.gallery_id)
        ChapterExtractor.__init__(self, url)

    def get_metadata(self, page):
        extr = text.extract
        title, pos = extr(page, '"og:title" content="', '"')
        thumb, pos = extr(page, '"og:image" content="', '"', pos)
        title_en, _, title_jp = text.unescape(title).partition("/")

        uploader  , pos = extr(page, 'id="Uploader">'  , '</div>', pos)
        date      , pos = extr(page, 'id="Uploaded">'  , '</div>', pos)
        rating    , pos = extr(page, 'id="Rating">'    , '</div>', pos)
        gtype     , pos = extr(page, 'id="Category">'  , '</div>', pos)
        collection, pos = extr(page, 'id="Collection">', '</div>', pos)
        group     , pos = extr(page, 'id="Group">'     , '</div>', pos)
        artist    , pos = extr(page, 'id="Artist">'    , '</div>', pos)
        parody    , pos = extr(page, 'id="Parody">'    , '</div>', pos)
        character , pos = extr(page, 'id="Character">' , '</div>', pos)
        tags      , pos = extr(page, 'id="Tag">'       , '</div>', pos)

        return {
            "gallery_id": text.parse_int(self.gallery_id),
            "title": title_en.strip(),
            "title_jp": title_jp.strip(),
            "thumbnail": thumb,
            "uploader": text.remove_html(uploader),
            "date": date.strip(),
            "rating": text.parse_float(rating.partition(" ")[0]),
            "type": text.remove_html(gtype),
            "collection": text.remove_html(collection),
            "group": text.remove_html(group),
            "artist": ", ".join(text.split_html(artist)),
            "parodies": ", ".join(text.split_html(parody)),
            "characters": ", ".join(text.split_html(character)),
            "tags": ", ".join(text.split_html(tags)),
            "language": "English",
            "lang": "en",
        }

    def get_images(self, page):
        url = "{}/Read/Load/?q={}".format(self.root, self.gallery_id)
        data = self.request(url, headers={"Referer": self.url}).json()
        base = self.root + "/Image/Object?name="

        return [
            (base + text.quote(name), None)
            for name in data["reader_page_urls"]
        ]


class TsuminoSearchExtractor(TsuminoBase, Extractor):
    """Extractor for search results on tsumino.com"""
    subcategory = "search"
    pattern = [r"(?i)(?:https?://)?(?:www\.)?tsumino\.com"
               r"/(?:Books/?)?#(.+)"]
    test = [
        ("https://www.tsumino.com/Books#?Character=Reimu+Hakurei", {
            "pattern": TsuminoGalleryExtractor.pattern[0],
            "range": "1-40",
            "count": 40,
        }),
        (("http://www.tsumino.com/Books#~(Tags~(~"
          "(Type~7~Text~'Reimu*20Hakurei~Exclude~false)~"
          "(Type~'1~Text~'Pantyhose~Exclude~false)))#"), {
            "pattern": TsuminoGalleryExtractor.pattern[0],
            "count": ">= 3",
        }),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.query = match.group(1)

    def items(self):
        yield Message.Version, 1
        for gallery in self.galleries():
            url = "{}/Book/Info/{}".format(self.root, gallery["Id"])
            yield Message.Queue, url, gallery

    def galleries(self):
        """Return all gallery results matching 'self.query'"""
        url = "{}/Books/Operate".format(self.root)
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

            for gallery in info["Data"]:
                yield gallery["Entry"]

            if info["PageNumber"] >= info["PageCount"]:
                return
            data["PageNumber"] += 1

    def _parse(self, query):
        try:
            if query.startswith("?"):
                return self._parse_simple(query)
            return self._parse_jsurl(query)
        except Exception as exc:
            self.log.error("Invalid search query: '%s' (%s)", query, exc)
            raise exception.StopExtraction()

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
