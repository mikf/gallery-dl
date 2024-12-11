# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import lofter


__tests__ = (
{
    "#url"  : "https://gengar563.lofter.com/post/1e82da8c_1c98dae1b",
    "#class": lofter.LofterPostExtractor,
    "#urls" : (
        "https://imglf3.lf127.net/img/S1d2QlVsWkJhSW1qcnpIS0ZSa3ZJQ1RxY0lYaU1UUE9tQ0NvUE9rVXFpOFFEVzMwbnQ4aEFnPT0.jpg",
        "https://imglf3.lf127.net/img/S1d2QlVsWkJhSW1qcnpIS0ZSa3ZJRWlXYTRVOEpXTU9TSGt3TjBDQ0JFZVpZMEJtWjFneVNBPT0.png",
        "https://imglf6.lf127.net/img/S1d2QlVsWkJhSW1qcnpIS0ZSa3ZJR1d3Y2VvbTNTQlIvdFU1WWlqZHEzbjI4MFVNZVdoN3VBPT0.png",
        "https://imglf6.lf127.net/img/S1d2QlVsWkJhSW1qcnpIS0ZSa3ZJTi83NDRDUjNvd3hySGxEZFovd2hwbi9oaG9NQ1hOUkZ3PT0.png",
        "https://imglf4.lf127.net/img/S1d2QlVsWkJhSW1qcnpIS0ZSa3ZJUFczb2RKSVlpMHJkNy9kc3BSQVQvQm5DNzB4eVhxay9nPT0.png",
        "https://imglf4.lf127.net/img/S1d2QlVsWkJhSW1qcnpIS0ZSa3ZJSStJZE9RYnJURktHazdIVHNNMjQ5eFJldHVTQy9XbDB3PT0.png",
        "https://imglf3.lf127.net/img/S1d2QlVsWkJhSW1qcnpIS0ZSa3ZJSzFCWFlnUWgzb01DcUdpT1lreG5yQjJVMkhGS09HNGR3PT0.png",
    ),

    "blog_name": "gengar563",
    "content"  : "<p>发了三次发不出有毒……</p> \n<p>二部运动au&nbsp;&nbsp;性转ac注意</p> \n<p>失去耐心.jpg</p>",
    "date"     : "dt:2020-06-04 12:51:42",
    "id"       : 7676472859,
},

{
    "#url"    : "https://wooden-brain.lofter.com/post/1e60de5b_1c9bf8efb",
    "#comment": "video",
    "#class"  : lofter.LofterPostExtractor,
    "#urls"   : (
        "https://vodm2lzexwq.vod.126.net/vodm2lzexwq/Pc5jg1nL_3039990631_sd.mp4?resId=254486990bfa2cd7aa860229db639341_3039990631_1&sign=4j02HTHXqNfhaF%2B%2FO14Ny%2F9SMNZj%2FIjpJDCqXfYa4aM%3D",
    ),

    "blog_name": "wooden-brain",
    "date"     : "dt:2020-06-24 11:01:59",
    "id"       : 7679741691,
},

{
    "#url"  : "https://gengar563.lofter.com/",
    "#class": lofter.LofterBlogPostsExtractor,
    "#range": "1-25",
    "#count": 25,

    "blog_name": "gengar563",
    "date"     : "type:datetime",
    "id"       : int,
},

{
    "#url"  : "https://www.lofter.com/front/blog/home-page/gengar563",
    "#class": lofter.LofterBlogPostsExtractor,
},

)
