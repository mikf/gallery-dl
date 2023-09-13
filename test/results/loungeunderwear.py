# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shopify


__tests__ = (
{
    "#url"     : "https://loungeunderwear.com/collections/apparel",
    "#category": ("shopify", "loungeunderwear", "collection"),
    "#class"   : shopify.ShopifyCollectionExtractor,
},

{
    "#url"     : "https://de.loungeunderwear.com/products/ribbed-crop-top-black",
    "#category": ("shopify", "loungeunderwear", "product"),
    "#class"   : shopify.ShopifyProductExtractor,
},

)
