# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shopify


__tests__ = (
{
    "#url"     : "https://www.windsorstore.com/collections/dresses-ball-gowns",
    "#category": ("shopify", "windsorstore", "collection"),
    "#class"   : shopify.ShopifyCollectionExtractor,
},

{
    "#url"     : "https://www.windsorstore.com/collections/accessories-belts/products/rhine-buckle-dbl-o-ring-pu-strap-belt-073010158001",
    "#category": ("shopify", "windsorstore", "product"),
    "#class"   : shopify.ShopifyProductExtractor,
},

)
