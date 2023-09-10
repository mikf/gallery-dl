# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shopify


__tests__ = (
{
    "#url"     : "https://www.ohpolly.com/collections/dresses-mini-dresses",
    "#category": ("shopify", "ohpolly", "collection"),
    "#class"   : shopify.ShopifyCollectionExtractor,
},

{
    "#url"     : "https://www.ohpolly.com/products/edonia-ruched-triangle-cup-a-line-mini-dress-brown",
    "#category": ("shopify", "ohpolly", "product"),
    "#class"   : shopify.ShopifyProductExtractor,
},

)
