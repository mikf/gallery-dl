# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shopify


__tests__ = (
{
    "#url"     : "https://pinupgirlclothing.com/collections/evening",
    "#category": ("shopify", "pinupgirlclothing", "collection"),
    "#class"   : shopify.ShopifyCollectionExtractor,
},

{
    "#url"     : "https://pinupgirlclothing.com/collections/evening/products/clarice-coat-dress-in-olive-green-poly-crepe-laura-byrnes-design",
    "#category": ("shopify", "pinupgirlclothing", "product"),
    "#class"   : shopify.ShopifyProductExtractor,
},

)
