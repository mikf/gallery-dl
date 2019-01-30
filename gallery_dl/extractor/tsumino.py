# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.tsumino.com/"""

from .common import ChapterExtractor
from .. import text, exception
from ..cache import cache


class TsuminoGalleryExtractor(ChapterExtractor):
    """Extractor for image galleries on tsumino.com"""
    category = "tsumino"
    subcategory = "gallery"
    filename_fmt = "{category}_{gallery_id}_{page:>03}.{extension}"
    directory_fmt = ["{category}", "{gallery_id} {title}"]
    archive_fmt = "{gallery_id}_{page}"
    cookiedomain = "www.tsumino.com"
    pattern = [r"(?i)(?:https?://)?(?:www\.)?tsumino\.com"
               r"/(?:Book/Info|Read/View)/(\d+)"]
    test = [
        ("https://www.tsumino.com/Book/Info/45834", {
            "url": "ed3e39bc21221fbd21b9a2ba711e8decb6fdc6bc",
            "keyword": "5acc43f67c61f5312e0b5d6c9d6b1276cda438fc",
        }),
        ("https://www.tsumino.com/Read/View/45834", None),
    ]
    root = "https://www.tsumino.com"

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = "{}/Book/Info/{}".format(self.root, self.gallery_id)
        ChapterExtractor.__init__(self, url)

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
