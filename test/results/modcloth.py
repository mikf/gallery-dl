# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shopify


__tests__ = (
{
    "#url"     : "https://modcloth.com/collections/shoes",
    "#category": ("shopify", "modcloth", "collection"),
    "#class"   : shopify.ShopifyCollectionExtractor,
},

{
    "#url"     : "https://modcloth.com/collections/shoes/products/heidii-brn",
    "#category": ("shopify", "modcloth", "product"),
    "#class"   : shopify.ShopifyProductExtractor,
},

)
