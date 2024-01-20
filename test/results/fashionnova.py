# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shopify


__tests__ = (
{
    "#url"     : "https://www.fashionnova.com/collections/mini-dresses",
    "#category": ("shopify", "fashionnova", "collection"),
    "#class"   : shopify.ShopifyCollectionExtractor,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://www.fashionnova.com/collections/mini-dresses/?page=1",
    "#category": ("shopify", "fashionnova", "collection"),
    "#class"   : shopify.ShopifyCollectionExtractor,
},

{
    "#url"     : "https://www.fashionnova.com/collections/mini-dresses#1",
    "#category": ("shopify", "fashionnova", "collection"),
    "#class"   : shopify.ShopifyCollectionExtractor,
},

{
    "#url"     : "https://www.fashionnova.com/products/all-my-life-legging-black",
    "#category": ("shopify", "fashionnova", "product"),
    "#class"   : shopify.ShopifyProductExtractor,
    "#pattern" : r"https?://cdn\d*\.shopify\.com/s/files/",
    "#count"   : 8,
},

{
    "#url"     : "https://www.fashionnova.com/collections/flats/products/name",
    "#category": ("shopify", "fashionnova", "product"),
    "#class"   : shopify.ShopifyProductExtractor,
},

)
