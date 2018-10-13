# -*- coding: utf-8 -*-

# Copyright 2016-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://luscious.net/"""

from .common import AsynchronousExtractor, Message
from .. import text, util


class LusciousAlbumExtractor(AsynchronousExtractor):
    """Extractor for image albums from luscious.net"""
    category = "luscious"
    subcategory = "album"
    directory_fmt = ["{category}", "{gallery_id} {title}"]
    filename_fmt = "{category}_{gallery_id}_{num:>03}.{extension}"
    archive_fmt = "{gallery_id}_{image_id}"
    pattern = [(r"(?:https?://)?(?:www\.|members\.)?luscious\.net/"
                r"(?:c/[^/?&#]+/)?(?:pictures/album|albums)/([^/?&#]+_(\d+))")]
    test = [
        (("https://luscious.net/c/hentai_manga/albums/"
          "okinami-no-koigokoro_277031/view/"), {
            "url": "7e4984a271a1072ac6483e4228a045895aff86f3",
            "keyword": "5ab53959f25a468455f79149461d26547669e50e",
            "content": "b3a747a6464509440bd0ff6d1267e6959f8d6ff3",
        }),
        ("https://luscious.net/albums/virgin-killer-sweater_282582/", {
            "url": "21cc68a7548f4d71dfd67d8caf96349dde7e791c",
            "keyword": "3de82f61ad4afd0f546ab5ae5bf9c5388cc9c3db",
        }),
        ("https://luscious.net/albums/okinami-no-koigokoro_277031/", None),
        ("https://www.luscious.net/albums/okinami_277031/", None),
        ("https://members.luscious.net/albums/okinami_277031/", None),
    ]
    root = "https://luscious.net"

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.gpart, self.gid = match.groups()

    def items(self):
        url = "{}/albums/{}/".format(self.root, self.gpart)
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

    def get_images(self, page, extr=text.extract):
        """Collect image-urls and -metadata"""
        num = 1

        if 'class="search_filter' in page:
            url = "{}/pictures/album/x_{}/sorted/oldest/page/1/".format(
                self.root, self.gid)
            page = self.request(url).text
            pos = page.find('<div id="picture_page_')
        else:
            pos = page.find('<div class="album_cover_item">')
        url = extr(page, '<a href="', '"', pos)[0]

        while url and not url.endswith("/more_like_this/"):
            page = self.request(self.root + url).text

            if num == 1:
                current = extr(page, '"pj_current_page" value="', '"')[0]
                if current and current != "1":
                    url = "{}/albums/{}/jump_to_page/1/".format(
                        self.root, self.gid)
                    page = self.request(url, method="POST").text

            imgid, pos = extr(url , '/id/', '/')
            url  , pos = extr(page, '<link rel="next" href="', '"')
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
