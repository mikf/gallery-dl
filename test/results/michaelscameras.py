# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shopify


__tests__ = (
{
    "#url"     : "https://michaels.com.au/collections/microphones",
    "#category": ("shopify", "michaelscameras", "collection"),
    "#class"   : shopify.ShopifyCollectionExtractor,
},

{
    "#url"     : "https://michaels.com.au/collections/audio/products/boya-by-wm4-pro-k5-2-4ghz-mic-android-1-1-101281",
    "#category": ("shopify", "michaelscameras", "product"),
    "#class"   : shopify.ShopifyProductExtractor,
},

)
