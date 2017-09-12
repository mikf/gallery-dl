# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://luscious.net/"""

from .common import AsynchronousExtractor, Message
from .. import text, util, exception


class LusciousAlbumExtractor(AsynchronousExtractor):
    """Extractor for image albums from luscious.net"""
    category = "luscious"
    subcategory = "album"
    directory_fmt = ["{category}", "{gallery_id} {title}"]
    filename_fmt = "{category}_{gallery_id}_{num:>03}.{extension}"
    pattern = [(r"(?:https?://)?(?:www\.)?luscious\.net/"
                r"(?:c/[^/]+/)?(?:pictures/album|albums)/([^/]+_(\d+))")]
    test = [
        (("https://luscious.net/c/hentai_manga/albums/"
          "okinami-no-koigokoro_277031/view/"), {
            "url": "7e4984a271a1072ac6483e4228a045895aff86f3",
            "keyword": "76e099479b180420fd5cf820f00c52fe07fda884",
            "content": "b3a747a6464509440bd0ff6d1267e6959f8d6ff3",
        }),
        ("https://luscious.net/albums/virgin-killer-sweater_282582/", {
            "url": "01e2d7dd6eecea0152610f2446a6b1d60519c8bd",
            "keyword": "02624ff1097260e2a3c1b220afc92ea4c6b109b3",
        }),
        ("https://luscious.net/albums/okinami-no-koigokoro_277031/", None),
    ]

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.gpart, self.gid = match.groups()

    def items(self):
        url = "https://luscious.net/albums/" + self.gpart + "/"
        page = self.request(url).text
        data = self.get_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for url, image in self.get_images(page):
            image.update(data)
            yield Message.Url, url, image

    def get_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = text.extract_all(page, (
            ("tags"    , '<meta name="keywords" content="', '"'),
            ("title"   , '"og:title" content="', '"'),
            (None      , '<li class="user_info">', ''),
            ("count"   , '<p>', ' '),
            (None      , '<p>Section:', ''),
            ("section" , '>', '<'),
            ("language", '<p>Language:', ' '),
        ), values={"gallery_id": self.gid})[0]
        data["lang"] = util.language_to_code(data["language"])
        try:
            data["artist"] = text.extract(data["tags"], "rtist: ", ",")[0]
        except AttributeError:
            data["artist"] = None
        return data

    def get_images(self, page):
        """Collect image-urls and -metadata"""
        extr = text.extract
        num = 1
        pos = page.find('<div class="album_cover_item">')
        url = extr(page, '<a href="', '"', pos)[0]
        self._check_high_load(page, url)
        while url and not url.endswith("/more_like_this/"):
            page = self.request("https://luscious.net" + url).text
            imgid, pos = extr(url , '/id/', '/')
            url  , pos = extr(page, '<link rel="next" href="', '"')
            self._check_high_load(page, url)
            name , pos = extr(page, '<h1 id="picture_title">', '</h1>', pos)
            _    , pos = extr(page, '<ul class="image_option_icons">', '', pos)
            iurl , pos = extr(page, '<li><a href="', '"', pos+100)

            yield iurl, {
                "num": num,
                "name": name,
                "extension": iurl.rpartition(".")[2],
                "image_id": imgid,
            }
            num += 1

    def _check_high_load(self, page, url):
        if not url and "<h1>High Load</h1>" in page:
            self.log.error('"High Load!" - unable to continue')
            raise exception.StopExtraction()
