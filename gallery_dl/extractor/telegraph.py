# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractor for https://telegra.ph/"""

from urllib.parse import urlparse

from .common import GalleryExtractor, Message
from .. import text


class TelegraphGalleryExtractor(GalleryExtractor):
    """Extractor for articles from telegra.ph"""

    category = "telegraph"
    root = "https://telegra.ph"
    directory_fmt = ("{category}", "{id}")
    filename_fmt = "{number_formatted}_{filename}.{extension}"
    pattern = r"((?:https?://)(?:www\.)??telegra\.ph/.+)"

    def __init__(self, match):
        super().__init__(match, match.group(1))

    def metadata(self, page):
        return {
            "title": text.extract(page, "<h1>", "</h1>")[0],
            "id": urlparse(self.url).path.split("/")[-1],
        }

    def items(self):
        page = self.request(self.url).text

        data = self.metadata(page)
        yield Message.Directory, data

        figures = tuple(text.extract_iter(page, "<figure>", "</figure>"))
        num_zeroes = len(str(len(figures)))

        for i, figure in enumerate(figures):
            image_url = text.extract(figure, '<img src="', '">')
            caption = text.extract(figure, ">", "</figcaption>", image_url[1])

            image = {
                "url": self.root + image_url[0],
                "caption": caption[0],
                "number": i + 1,
                "number_formatted": str(i + 1).zfill(num_zeroes),
            }
            image.update(data)
            image = text.nameext_from_url(image["url"], image)

            yield Message.Url, image["url"], image
