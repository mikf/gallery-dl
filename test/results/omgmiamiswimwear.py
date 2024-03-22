# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shopify


__tests__ = (
{
    "#url"     : "https://www.omgmiamiswimwear.com/collections/fajas",
    "#category": ("shopify", "omgmiamiswimwear", "collection"),
    "#class"   : shopify.ShopifyCollectionExtractor,
},

{
    "#url"     : "https://www.omgmiamiswimwear.com/products/snatch-me-waist-belt",
    "#category": ("shopify", "omgmiamiswimwear", "product"),
    "#class"   : shopify.ShopifyProductExtractor,
    "#pattern" : r"https://cdn\.shopify\.com/s/files/1/1819/6171/",
    "#count"   : 3,
},

)
