# -*- coding: utf-8 -*-

# Copyright 2018-2023 Mike Fährmann
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
    pattern = (r"(?:https?://)?(?!videos\.)([\w-]+\.)?simply-hentai\.com"
               r"(?!/(?:album|gifs?|images?|series)(?:/|$))"
               r"((?:/(?!(?:page|all-pages)(?:/|\.|$))[^/?#]+)+)")
    example = "https://www.simply-hentai.com/TITLE"

    def __init__(self, match):
        subdomain, path = match.groups()
        if subdomain and subdomain not in ("www.", "old."):
            path = "/" + subdomain.rstrip(".") + path
        url = "https://old.simply-hentai.com" + path
        GalleryExtractor.__init__(self, match, url)

    def _init(self):
        self.session.headers["Referer"] = self.gallery_url

    def metadata(self, page):
        extr = text.extract_from(page)
        split = text.split_html

        title = extr('<meta property="og:title" content="', '"')
        image = extr('<meta property="og:image" content="', '"')
        if not title:
            raise exception.NotFoundError("gallery")
        data = {
            "title"     : text.unescape(title),
            "gallery_id": text.parse_int(image.split("/")[-2]),
            "parody"    : split(extr('box-title">Series</div>', '</div>')),
            "language"  : text.remove_html(extr(
                'box-title">Language</div>', '</div>')) or None,
            "characters": split(extr('box-title">Characters</div>', '</div>')),
            "tags"      : split(extr('box-title">Tags</div>', '</div>')),
            "artist"    : split(extr('box-title">Artists</div>', '</div>')),
            "date"      : text.parse_datetime(text.remove_html(
                extr('Uploaded', '</div>')), "%d.%m.%Y"),
        }
        data["lang"] = util.language_to_code(data["language"])
        return data

    def images(self, _):
        url = self.gallery_url + "/all-pages"
        headers = {"Accept": "application/json"}
        images = self.request(url, headers=headers).json()
        return [
            (
                urls["full"].replace("/giant_thumb_", "/"),
                {"image_id": text.parse_int(image_id)},
            )
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
               r"/(image|gif)/[^/?#]+)")
    example = "https://www.simply-hentai.com/image/NAME"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.page_url = "https://old." + match.group(1)
        self.type = match.group(2)

    def items(self):
        extr = text.extract_from(self.request(self.page_url).text)
        title = extr('"og:title" content="'      , '"')
        descr = extr('"og:description" content="', '"')
        url = extr('&quot;image&quot;:&quot;'  , '&')
        url = extr("&quot;content&quot;:&quot;", "&") or url

        tags = text.extr(descr, " tagged with ", " online for free ")
        if tags:
            tags = tags.split(", ")
            tags[-1] = tags[-1].partition(" ")[2]
        else:
            tags = []

        if url.startswith("//"):
            url = "https:" + url

        data = text.nameext_from_url(url, {
            "title": text.unescape(title) if title else "",
            "tags": tags,
            "type": self.type,
        })
        data["token"] = data["filename"].rpartition("_")[2]

        yield Message.Directory, data
        yield Message.Url, url, data


class SimplyhentaiVideoExtractor(Extractor):
    """Extractor for hentai videos from simply-hentai.com"""
    category = "simplyhentai"
    subcategory = "video"
    directory_fmt = ("{category}", "{type}s")
    filename_fmt = "{title}{episode:?_//>02}.{extension}"
    archive_fmt = "{title}_{episode}"
    pattern = r"(?:https?://)?(videos\.simply-hentai\.com/[^/?#]+)"
    example = "https://videos.simply-hentai.com/TITLE"

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
            video_url = text.extr(embed_page, '"file":"', '"')
            title, _, episode = title.rpartition(" Episode ")

        if video_url.startswith("//"):
            video_url = "https:" + video_url

        data = text.nameext_from_url(video_url, {
            "title": text.unescape(title),
            "episode": text.parse_int(episode),
            "tags": text.split_html(tags)[::2],
            "type": "video",
            "date": text.parse_datetime(text.remove_html(
                date), "%B %d, %Y %H:%M"),
        })

        yield Message.Directory, data
        yield Message.Url, video_url, data
