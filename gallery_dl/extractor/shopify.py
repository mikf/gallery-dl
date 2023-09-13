# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
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
    "chelseacrew": {
        "root": "https://chelseacrew.com",
        "pattern": r"(?:www\.)?chelseacrew\.com",
    },
    "fashionnova": {
        "root": "https://www.fashionnova.com",
        "pattern": r"(?:www\.)?fashionnova\.com",
    },
    "loungeunderwear": {
        "root": "https://loungeunderwear.com",
        "pattern": r"(?:[a-z]+\.)?loungeunderwear\.com",
    },
    "michaelscameras": {
        "root": "https://michaels.com.au",
        "pattern": r"michaels\.com\.au",
    },
    "modcloth": {
        "root": "https://modcloth.com",
        "pattern": r"modcloth\.com",
    },
    "ohpolly": {
        "root": "https://www.ohpolly.com",
        "pattern": r"(?:www\.)?ohpolly\.com",
    },
    "omgmiamiswimwear": {
        "root": "https://www.omgmiamiswimwear.com",
        "pattern": r"(?:www\.)?omgmiamiswimwear\.com",
    },
    "pinupgirlclothing": {
        "root": "https://pinupgirlclothing.com",
        "pattern": r"pinupgirlclothing\.com",
    },
    "raidlondon": {
        "root": "https://www.raidlondon.com",
        "pattern": r"(?:www\.)?raidlondon\.com",
    },
    "unique-vintage": {
        "root": "https://www.unique-vintage.com",
        "pattern": r"(?:www\.)?unique\-vintage\.com",
    },
    "windsorstore": {
        "root": "https://www.windsorstore.com",
        "pattern": r"(?:www\.)?windsorstore\.com",
    },
})


class ShopifyCollectionExtractor(ShopifyExtractor):
    """Base class for collection extractors for Shopify based sites"""
    subcategory = "collection"
    directory_fmt = ("{category}", "{collection[title]}")
    pattern = BASE_PATTERN + r"(/collections/[\w-]+)/?(?:$|[?#])"
    example = "https://www.fashionnova.com/collections/TITLE"

    def metadata(self):
        return self.request(self.item_url + ".json").json()

    def products(self):
        url = self.item_url + "/products.json"
        params = {"page": 1}

        while True:
            data = self.request(url, params=params).json()["products"]
            if not data:
                return
            yield from data
            params["page"] += 1


class ShopifyProductExtractor(ShopifyExtractor):
    """Base class for product extractors for Shopify based sites"""
    subcategory = "product"
    directory_fmt = ("{category}", "Products")
    pattern = BASE_PATTERN + r"((?:/collections/[\w-]+)?/products/[\w-]+)"
    example = "https://www.fashionnova.com/collections/TITLE/products/NAME"

    def products(self):
        product = self.request(self.item_url + ".json").json()["product"]
        del product["image"]
        return (product,)
