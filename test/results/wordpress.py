# -*- coding: utf-8 -*-

from gallery_dl.extractor import wordpress

__tests__ = (
{
    "#url"     : "wp:https://example.wordpress.com",
    "#category": ("", "wordpress", "posts"),
    "#class"   : wordpress.WordpressPostsExtractor,
},
{
    "#url"     : "wordpress:https://example.wordpress.com",
    "#category": ("", "wordpress", "posts"),
    "#class"   : wordpress.WordpressPostsExtractor,
},
{
    "#url"     : "wp:example.wordpress.com",
    "#category": ("", "wordpress", "posts"),
    "#class"   : wordpress.WordpressPostsExtractor,
},
)
