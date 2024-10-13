# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import facebook
import datetime


__tests__ = (
{
    "#url"     : "https://www.facebook.com/facebook/photos",
    "#category": ("", "facebook", "profile"),
    "#class"   : facebook.FacebookProfileExtractor,
    "#range"   : "1-3",
    "#count"   : 3,
},

{
    "#url"     : "https://www.facebook.com/media/set/?set=a.10152716010956729&type=3",
    "#category": ("", "facebook", "set"),
    "#class"   : facebook.FacebookSetExtractor,
    "#count"   : 6,
},

{
    "#url"     : "https://www.facebook.com/photo/?fbid=10160743390456729",
    "#category": ("", "facebook", "photo"),
    "#class"   : facebook.FacebookPhotoExtractor,
    "#count"   : 1,

    "caption"  : "They were on a break... #FriendsReunion #MoreTogether",
    "date"     : datetime.datetime(2021, 5, 27, 21, 55, 19),
    "filename" : "191053255_10160743390471729_9001965649022744000_n.jpg",
    "id"       : "10160743390456729",
    "set_id"   : "a.494827881728",
    "url"      : str,
    "user_id"  : "100064860875397",
    "username" : "Facebook",
},

{
    "#url"     : "https://www.facebook.com/Facebook/photos/a.10152716010956729/10152716011076729",
    "#category": ("", "facebook", "photo"),
    "#class"   : facebook.FacebookPhotoExtractor,
    "#count"   : 1,

    "caption"  : "",
    "date"     : datetime.datetime(2014, 5, 3, 0, 44, 47),
    "filename" : "10334445_10152716011076729_6502314875328401420_n.png",
    "id"       : "10152716011076729",
    "set_id"   : "a.10152716010956729",
    "url"      : str,
    "user_id"  : "100064860875397",
    "username" : "Facebook",
},

{
    "#url"     : "https://www.facebook.com/Facebook/posts/10152716011101729",
    "#category": ("", "facebook", "photo"),
    "#class"   : facebook.FacebookPhotoExtractor,
    "#count"   : 1,

    "caption"  : "",
    "date"     : datetime.datetime(2014, 5, 3, 0, 44, 47),
    "filename" : "10154418_10152716011101729_3247649165160407848_n.png",
    "id"       : "10152716011101729",
    "set_id"   : "a.10152716010956729",
    "url"      : str,
    "user_id"  : "100064860875397",
    "username" : "Facebook",
},

{
    "#url"     : "https://www.facebook.com/watch/?v=1165557851291824",
    "#category": ("", "facebook", "video"),
    "#class"   : facebook.FacebookVideoExtractor,
    "#count"   : 1,

    "date"     : datetime.datetime(2024, 4, 19, 17, 25, 48),
    "name"     : "451734618_986951969754568_3078978443536682653_n",
    "id"       : "1165557851291824",
    "url"      : str,
    "user_id"  : "100064860875397",
    "username" : "Facebook",
},

{
    "#url"     : "https://www.facebook.com/100064860875397/videos/644342003942740",
    "#category": ("", "facebook", "video"),
    "#class"   : facebook.FacebookVideoExtractor,
    "#count"   : 2,

    "date"     : datetime.datetime(2022, 10, 14, 16, 45, 27),
    "name"     : "1514198129001376",
    "id"       : "644342003942740",
    "url"      : str,
    "user_id"  : "100064860875397",
    "username" : "Facebook",
},

)
