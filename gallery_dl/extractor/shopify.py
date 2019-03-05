# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Shopify instances"""

from .common import Extractor, Message, SharedConfigMixin
from .. import text, config
import re


class ShopifyExtractor(SharedConfigMixin, Extractor):
    """Base class for shopify extractors"""
    basecategory = "shopify"
    filename_fmt = "{product[title]}_{num:>02}_{id}.{extension}"
    archive_fmt = "{id}"
    root = ""

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.item_url = self.root + match.group(1)

    def items(self):
        data = self.metadata()
        yield Message.Version, 1
        yield Message.Directory, data

        headers = {"X-Requested-With": "XMLHttpRequest"}
        for url in self.products():
            product = self.request(
                url + ".json", headers=headers).json()["product"]
            del product["image"]

            for num, image in enumerate(product.pop("images"), 1):
                text.nameext_from_url(image["src"], image)
                image.update(data)
                image["product"] = product
                image["num"] = num
                yield Message.Url, image["src"], image

    def metadata(self):
        """Return general metadata"""
        return {}

    def products(self):
        """Return an iterable with all relevant product URLs"""
        return ()


class ShopifyCollectionExtractor(ShopifyExtractor):
    """Base class for collection extractors for Shopify based sites"""
    subcategory = "collection"
    directory_fmt = ("{category}", "{collection[title]}")

    def __init__(self, match):
        ShopifyExtractor.__init__(self, match)
        self.params = match.group(2)

    def metadata(self):
        return self.request(self.item_url + ".json").json()

    def products(self):
        params = text.parse_query(self.params)
        params["page"] = text.parse_int(params.get("page"), 1)
        search_re = re.compile(r"/collections/[\w-]+/products/[\w-]+")

        while True:
            page = self.request(self.item_url, params=params).text
            urls = search_re.findall(page)

            if not urls:
                return
            for path in urls:
                yield self.root + path
            params["page"] += 1


class ShopifyProductExtractor(ShopifyExtractor):
    """Base class for product extractors for Shopify based sites"""
    subcategory = "product"
    directory_fmt = ("{category}", "Products")

    def products(self):
        return (self.item_url,)


def generate_extractors():
    """Dynamically generate Extractor classes for FoOlSlide instances"""
    symtable = globals()
    extractors = config.get(("extractor", "shopify"))

    if extractors:
        EXTRACTORS.update(extractors)

    for category, info in EXTRACTORS.items():

        if not isinstance(info, dict):
            continue

        root = info["root"]
        domain = root[root.index(":") + 3:]
        pattern = info.get("pattern") or re.escape(domain)
        name = (info.get("name") or category).capitalize()

        class CoExtr(ShopifyCollectionExtractor):
            pass

        CoExtr.__name__ = CoExtr.__qualname__ = name + "CollectionExtractor"
        CoExtr.__doc__ = "Extractor for product collections from " + domain
        CoExtr.category = category
        CoExtr.pattern = (r"(?:https?://)?" + pattern +
                          r"(/collections/[\w-]+)/?(?:\?([^#]+))?(?:$|#)")
        CoExtr.test = info.get("test-collection")
        CoExtr.root = root
        symtable[CoExtr.__name__] = CoExtr

        class PrExtr(ShopifyProductExtractor):
            pass

        PrExtr.__name__ = PrExtr.__qualname__ = name + "ProductExtractor"
        PrExtr.__doc__ = "Extractor for individual products from " + domain
        PrExtr.category = category
        PrExtr.pattern = (r"(?:https?://)?" + pattern +
                          r"((?:/collections/[\w-]+)?/products/[\w-]+)")
        PrExtr.test = info.get("test-product")
        PrExtr.root = root
        symtable[PrExtr.__name__] = PrExtr


EXTRACTORS = {
    "fashionnova": {
        "root": "https://www.fashionnova.com",
        "pattern": r"(?:www\.)?fashionnova\.com",
        "test-collection": (
            ("https://www.fashionnova.com/collections/mini-dresses", {
                "range": "1-20",
                "count": 20,
            }),
            ("https://www.fashionnova.com/collections/mini-dresses/?page=1"),
            ("https://www.fashionnova.com/collections/mini-dresses#1"),
        ),
        "test-product": (
            ("https://www.fashionnova.com/products"
             "/only-here-tonight-cut-out-dress-black"),
            ("https://www.fashionnova.com/collections/mini-dresses/products"
             "/only-here-tonight-cut-out-dress-black"),
        )
    },
}

generate_extractors()
