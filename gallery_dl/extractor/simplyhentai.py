# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract hentai-manga from https://www.simply-hentai.com/"""

from .common import Extractor, ChapterExtractor, Message
from .. import text, util, exception


class SimplyhentaiGalleryExtractor(ChapterExtractor):
    """Extractor for image galleries from simply-hentai.com"""
    category = "simplyhentai"
    subcategory = "gallery"
    directory_fmt = ["{category}", "{gallery_id} {title}"]
    filename_fmt = "{category}_{gallery_id}_{page:>03}.{extension}"
    archive_fmt = "{image_id}"
    pattern = [r"(?:https?://)?(?!videos\.)([\w-]+\.simply-hentai\.com"
               r"(?!/(?:album|gifs?|images?|series)(?:/|$))"
               r"(?:/(?!(?:page|all-pages)(?:/|\.|$))[^/?&#]+)+)"]
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
        url = "https://" + match.group(1)
        ChapterExtractor.__init__(self, url)
        self.session.headers["Referer"] = url

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
        headers = {"Accept": "application/json"}
        images = self.request(self.url + "/all-pages", headers=headers).json()
        return [
            (urls["full"], {"image_id": text.parse_int(image_id)})
            for image_id, urls in sorted(images.items())
        ]


class SimplyhentaiImageExtractor(Extractor):
    """Extractor for individual images from simply-hentai.com"""
    category = "simplyhentai"
    subcategory = "image"
    directory_fmt = ["{category}", "{type}s"]
    filename_fmt = "{category}_{token}{title:?_//}.{extension}"
    archive_fmt = "{token}"
    pattern = [r"(?:https?://)?(?:www\.)?(simply-hentai\.com"
               r"/(image|gif)/[^/?&#]+)"]
    test = [
        (("https://www.simply-hentai.com/image"
          "/pheromomania-vol-1-kanzenban-isao-3949d8b3-400c-4b6"), {
            "url": "0338eb137830ab6f81e5f410d3936ef785d063d9",
            "keyword": "2f673a424cf06e946685660ff5ca5b0e7cf685cc",
        }),
        ("https://www.simply-hentai.com/gif/8915dfcf-0b6a-47c", {
            "url": "11c060d7ec4dfd0bd105300b6e1fd454674a5af1",
            "keyword": "fbfd5c418f3d9d7d0b0ba0cda0602240820da693",
        }),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = "https://www." + match.group(1)
        self.type = match.group(2)

    def items(self):
        page = self.request(self.url).text
        url_search = 'data-src="' if self.type == "image" else '<source src="'

        title, pos = text.extract(page, 'property="og:title" content="', '"')
        url  , pos = text.extract(page, url_search, '"', pos)
        tags , pos = text.extract(page, '<div class="tags">', '</div>', pos)

        data = text.nameext_from_url(url, {
            "title": text.unescape(title) if title else "",
            "tags": ", ".join(text.split_html(tags)),
            "type": self.type,
        })
        data["token"] = data["name"].rpartition("_")[2]

        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data


class SimplyhentaiVideoExtractor(Extractor):
    """Extractor for hentai videos from simply-hentai.com"""
    category = "simplyhentai"
    subcategory = "video"
    directory_fmt = ["{category}", "{type}s"]
    filename_fmt = "{title}{episode:?_//>02}.{extension}"
    archive_fmt = "{title}_{episode}"
    pattern = [r"(?:https?://)?(videos\.simply-hentai\.com/[^/?&#]+)"]
    test = [
        ("https://videos.simply-hentai.com/creamy-pie-episode-02", {
            "pattern": r"https://www\.googleapis\.com/drive/v3/files"
                       r"/0B1ecQ8ZVLm3JcHZzQzBnVy1ZUmc\?alt=media&key=[\w-]+",
            "keyword": "315201bd4f3ce6bff57f4fbc631788c004d0eb7d",
            "count": 1,
        }),
        (("https://videos.simply-hentai.com"
          "/1715-tifa-in-hentai-gang-bang-3d-movie"), {
            "url": "ad9a36ae06c601b6490e3c401834b4949d947eb0",
            "keyword": "fef03513d5e1a9958d63e45a1d583e2f658b1168",
        }),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = "https://" + match.group(1)

    def items(self):
        page = self.request(self.url).text

        title, pos = text.extract(page, "<title>", "</title>")
        tags , pos = text.extract(page, ">Tags</div>", "</div>", pos)
        date , pos = text.extract(page, ">Upload Date</div>", "</div>", pos)
        title = title.rpartition(" - ")[0]

        if "<video" in page:
            video_url = text.extract(page, '<source src="', '"', pos)[0]
            episode = 0
        else:
            # video url from myhentai.tv embed
            pos = page.index('<div class="video-frame-container">', pos)
            embed_url = text.extract(page, 'src="', '"', pos)[0].replace(
                "embedplayer.php?link=", "embed.php?name=")
            embed_page = self.request(embed_url).text
            video_url = text.extract(embed_page, '"file":"', '"')[0]
            title, _, episode = title.rpartition(" Episode ")

        data = text.nameext_from_url(video_url, {
            "title": text.unescape(title),
            "episode": text.parse_int(episode),
            "tags": "".join(text.split_html(tags)),
            "date": text.remove_html(date),
            "type": "video",
        })

        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, video_url, data
