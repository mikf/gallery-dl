# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shopify


__tests__ = (
{
    "#url"     : "https://www.unique-vintage.com/collections/flapper-1920s",
    "#category": ("shopify", "unique-vintage", "collection"),
    "#class"   : shopify.ShopifyCollectionExtractor,
},

{
    "#url"     : "https://www.unique-vintage.com/collections/flapper-1920s/products/unique-vintage-plus-size-black-silver-beaded-troyes-flapper-dress",
    "#category": ("shopify", "unique-vintage", "product"),
    "#class"   : shopify.ShopifyProductExtractor,
},

)
