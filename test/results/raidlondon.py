# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shopify


__tests__ = (
{
    "#url"     : "https://www.raidlondon.com/collections/flats",
    "#category": ("shopify", "raidlondon", "collection"),
    "#class"   : shopify.ShopifyCollectionExtractor,
},

{
    "#url"     : "https://www.raidlondon.com/collections/flats/products/raid-addyson-chunky-flat-shoe-in-white",
    "#category": ("shopify", "raidlondon", "product"),
    "#class"   : shopify.ShopifyProductExtractor,
},

)
