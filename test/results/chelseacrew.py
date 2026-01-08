# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shopify


__tests__ = (
{
    "#url"     : "https://chelseacrew.com/collections/flats",
    "#category": ("shopify", "chelseacrew", "collection"),
    "#class"   : shopify.ShopifyCollectionExtractor,
},

{
    "#url"     : "https://chelseacrew.com/collections/flats/products/dora",
    "#category": ("shopify", "chelseacrew", "product"),
    "#class"   : shopify.ShopifyProductExtractor,
},

{
    "#url"     : "https://chelseacrew.com/en-de/collections/bridalcrew/products/gloria",
    "#category": ("shopify", "chelseacrew", "product"),
    "#class"   : shopify.ShopifyProductExtractor,
},

)
