# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract hentai-manga from https://www.simply-hentai.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util, exception


class SimplyhentaiGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from simply-hentai.com"""
    category = "simplyhentai"
    archive_fmt = "{image_id}"
    pattern = (r"(?:https?://)?(?!videos\.)([\w-]+\.simply-hentai\.com"
               r"(?!/(?:album|gifs?|images?|series)(?:/|$))"
               r"(?:/(?!(?:page|all-pages)(?:/|\.|$))[^/?&#]+)+)")
    test = (
        (("https://original-work.simply-hentai.com"
          "/amazon-no-hiyaku-amazon-elixir"), {
            "url": "258289249990502c3138719cb89e995a60861e49",
            "keyword": "18ab9defca53dbb2aeb7965193e93e0ea125b76b",
        }),
        ("https://www.simply-hentai.com/notfound", {
            "exception": exception.GalleryDLException,
        }),
        # custom subdomain
        ("https://pokemon.simply-hentai.com/mao-friends-9bc39"),
        # www subdomain, two path segments
        ("https://www.simply-hentai.com/vocaloid/black-magnet"),
    )

    def __init__(self, match):
        url = "https://" + match.group(1)
        GalleryExtractor.__init__(self, match, url)
        self.session.headers["Referer"] = url

    def metadata(self, page):
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
            "title"     : text.unescape(title),
            "artist"    : text.split_html(artist),
            "parody"    : text.split_html(series),
            "characters": text.split_html(chars),
            "tags"      : text.split_html(tags),
            "lang"      : util.language_to_code(lang),
            "language"  : lang,
            "date"      : text.remove_html(date),
        }

    def images(self, _):
        url = self.chapter_url + "/all-pages"
        headers = {"Accept": "application/json"}
        images = self.request(url, headers=headers).json()
        return [
            (urls["full"], {"image_id": text.parse_int(image_id)})
            for image_id, urls in sorted(images.items())
        ]


class SimplyhentaiImageExtractor(Extractor):
    """Extractor for individual images from simply-hentai.com"""
    category = "simplyhentai"
    subcategory = "image"
    directory_fmt = ("{category}", "{type}s")
    filename_fmt = "{category}_{token}{title:?_//}.{extension}"
    archive_fmt = "{token}"
    pattern = (r"(?:https?://)?(?:www\.)?(simply-hentai\.com"
               r"/(image|gif)/[^/?&#]+)")
    test = (
        (("https://www.simply-hentai.com/image"
          "/pheromomania-vol-1-kanzenban-isao-3949d8b3-400c-4b6"), {
            "url": "0338eb137830ab6f81e5f410d3936ef785d063d9",
            "keyword": "e10e5588481cab68329ef6ec1e5325206b2079a2",
        }),
        ("https://www.simply-hentai.com/gif/8915dfcf-0b6a-47c", {
            "url": "11c060d7ec4dfd0bd105300b6e1fd454674a5af1",
            "keyword": "dd97a4bb449c397d6fec9f43a1303c0fb168ae65",
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.page_url = "https://www." + match.group(1)
        self.type = match.group(2)

    def items(self):
        page = self.request(self.page_url).text
        url_search = 'data-src="' if self.type == "image" else '<source src="'

        title, pos = text.extract(page, '"og:title" content="', '"')
        descr, pos = text.extract(page, '"og:description" content="', '"', pos)
        url  , pos = text.extract(page, url_search, '"', pos)

        tags = text.extract(descr, " tagged with ", " online for free ")[0]
        if tags:
            tags = tags.split(", ")
            tags[-1] = tags[-1].partition(" ")[2]
        else:
            tags = []

        data = text.nameext_from_url(url, {
            "title": text.unescape(title) if title else "",
            "tags": tags,
            "type": self.type,
        })
        data["token"] = data["filename"].rpartition("_")[2]

        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data


class SimplyhentaiVideoExtractor(Extractor):
    """Extractor for hentai videos from simply-hentai.com"""
    category = "simplyhentai"
    subcategory = "video"
    directory_fmt = ("{category}", "{type}s")
    filename_fmt = "{title}{episode:?_//>02}.{extension}"
    archive_fmt = "{title}_{episode}"
    pattern = r"(?:https?://)?(videos\.simply-hentai\.com/[^/?&#]+)"
    test = (
        ("https://videos.simply-hentai.com/creamy-pie-episode-02", {
            "pattern": r"https://www\.googleapis\.com/drive/v3/files"
                       r"/0B1ecQ8ZVLm3JcHZzQzBnVy1ZUmc\?alt=media&key=[\w-]+",
            "keyword": "29d63987fed33f0a9f4b3786d1d71b03d793250a",
            "count": 1,
        }),
        (("https://videos.simply-hentai.com"
          "/1715-tifa-in-hentai-gang-bang-3d-movie"), {
            "url": "ad9a36ae06c601b6490e3c401834b4949d947eb0",
            "keyword": "c561341aa3c6999f615abf1971d28fb2a83da2a7",
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.page_url = "https://" + match.group(1)

    def items(self):
        page = self.request(self.page_url).text

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
            "tags": text.split_html(tags)[::2],
            "date": text.remove_html(date),
            "type": "video",
        })

        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, video_url, data
