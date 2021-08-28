# -*- coding: utf-8 -*-

# Copyright 2019-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Shopify instances"""

from .common import BaseExtractor, Message
from .. import text


class ShopifyExtractor(BaseExtractor):
    """Base class for Shopify extractors"""
    basecategory = "shopify"
    filename_fmt = "{product[title]}_{num:>02}_{id}.{extension}"
    archive_fmt = "{id}"

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        self.item_url = self.root + match.group(match.lastindex)

    def items(self):
        data = self.metadata()
        yield Message.Directory, data

        for product in self.products():
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


BASE_PATTERN = ShopifyExtractor.update({
    "fashionnova": {
        "root": "https://www.fashionnova.com",
        "pattern": r"(?:www\.)?fashionnova\.com",
    },
    "omgmiamiswimwear": {
        "root": "https://www.omgmiamiswimwear.com",
    },
    "windsorstore": {
        "root": "https://www.windsorstore.com",
    },
})


class ShopifyCollectionExtractor(ShopifyExtractor):
    """Base class for collection extractors for Shopify based sites"""
    subcategory = "collection"
    directory_fmt = ("{category}", "{collection[title]}")
    pattern = BASE_PATTERN + r"(/collections/[\w-]+)/?(?:$|[?#])"
    test = (
        ("https://www.fashionnova.com/collections/mini-dresses", {
            "range": "1-20",
            "count": 20,
        }),
        ("https://www.fashionnova.com/collections/mini-dresses/?page=1"),
        ("https://www.fashionnova.com/collections/mini-dresses#1"),
        ("https://www.omgmiamiswimwear.com/collections/fajas"),
        ("https://www.windsorstore.com/collections/dresses-ball-gowns"),
    )

    def metadata(self):
        return self.request(self.item_url + ".json").json()

    def products(self):
        url = self.item_url + "/products.json"

        while url:
            response = self.request(url)
            yield from response.json()["products"]

            url = response.links.get("next")
            if not url:
                return
            url = url["url"]


class ShopifyProductExtractor(ShopifyExtractor):
    """Base class for product extractors for Shopify based sites"""
    subcategory = "product"
    directory_fmt = ("{category}", "Products")
    pattern = BASE_PATTERN + r"((?:/collections/[\w-]+)?/products/[\w-]+)"
    test = (
        ("https://www.fashionnova.com/products/essential-slide-red", {
            "pattern": r"https?://cdn\d*\.shopify.com/",
            "count": 3,
        }),
        ("https://www.omgmiamiswimwear.com/products/la-medusa-maxi-dress", {
            "pattern": r"https://cdn\.shopify\.com/s/files/1/1819/6171/",
            "count": 5,
        }),
        ("https://www.fashionnova.com/collections/flats/products/name"),
        ("https://www.windsorstore.com/collections/accessories-belts/products"
         "/rhine-buckle-dbl-o-ring-pu-strap-belt-073010158001"),
    )

    def products(self):
        product = self.request(self.item_url + ".json").json()["product"]
        del product["image"]
        return (product,)
