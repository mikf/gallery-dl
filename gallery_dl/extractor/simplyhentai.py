# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract hentai-manga from https://www.simply-hentai.com/"""

from .common import ChapterExtractor
from .. import text, util, exception


class SimplyhentaiGalleryExtractor(ChapterExtractor):
    """Extractor for image galleries from simply-hentai.com"""
    category = "simplyhentai"
    subcategory = "gallery"
    directory_fmt = ["{category}", "{gallery_id} {title}"]
    filename_fmt = "{category}_{gallery_id}_{page:>03}.{extension}"
    archive_fmt = "{image_id}"
    pattern = [r"(?:https?://)?(?!videos)[^.]+\.simply-hentai\.com"
               r"(?:/(?!page|series|album|all-pages)[^/?&#]+)+"]
    test = [
        (("https://original-work.simply-hentai.com"
          "/amazon-no-hiyaku-amazon-elixir"), {
            "url": "35f3843d0ea83e6a618df7afaebd2b03f3628db9",
            "keyword": "1e22ccbe66412eab844f135ad9cd3424b8b064e8",
        }),
        ("https://www.simply-hentai.com/notfound", {
            "exception": exception.GalleryDLException,
        }),
        # custom subdomain
        ("https://pokemon.simply-hentai.com/mao-friends-9bc39", None),
        # www subdomain, two path segments
        ("https://www.simply-hentai.com/vocaloid/black-magnet", None),
    ]

    def __init__(self, match):
        ChapterExtractor.__init__(self, match.group(0))
        self.session.headers["Referer"] = match.group(0)

    def get_metadata(self, page):
        extr = text.extract
        title , pos = extr(page, '<meta property="og:title" content="', '"')
        if not title:
            raise exception.NotFoundError("gallery")
        gid   , pos = extr(page, '/Album/', '/', pos)
        series, pos = extr(page, 'box-title">Series</div>', '</div>', pos)
        lang  , pos = extr(page, 'box-title">Language</div>', '</div>', pos)
        chars , pos = extr(page, 'box-title">Characters</div>', '</div>', pos)
        tags  , pos = extr(page, 'box-title">Tags</div>', '</div>', pos)
        artist, pos = extr(page, 'box-title">Artists</div>', '</div>', pos)
        date  , pos = extr(page, 'Uploaded', '</div>', pos)
        lang = text.remove_html(lang) if lang else None

        return {
            "gallery_id": text.parse_int(gid),
            "title": text.unescape(title),
            "series": text.remove_html(series),
            "characters": ", ".join(text.split_html(chars)),
            "tags": ", ".join(text.split_html(tags)),
            "artist": ", ".join(text.split_html(artist)),
            "lang": util.language_to_code(lang),
            "language": lang,
            "date": text.remove_html(date),
        }

    def get_images(self, _):
        images = self.request(self.url + "/all-pages.json").json()
        return [
            (urls["full"], {"image_id": text.parse_int(image_id)})
            for image_id, urls in sorted(images.items())
        ]
