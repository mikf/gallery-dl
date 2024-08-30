# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import facebook
import datetime


__tests__ = (
{
    "#url"     : "https://www.facebook.com/facebook",
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
    "#url"     : "https://www.facebook.com/photo/?fbid=10152716011096729",
    "#category": ("", "facebook", "photo"),
    "#class"   : facebook.FacebookPhotoExtractor,
    "#count"   : 1,

    "caption"  : str,
    "comments" : int,
    "date"     : datetime.datetime(2014, 5, 3, 0, 44, 47),
    "filename" : "10268581_10152716011096729_8785818270101685508_n.png",
    "id"       : "10152716011096729",
    "reactions": int,
    "set_id"   : "a.10152716010956729",
    "shares"   : int,
},

{
    "#url"     : "https://www.facebook.com/watch/?v=1165557851291824",
    "#category": ("", "facebook", "video"),
    "#class"   : facebook.FacebookVideoExtractor,
    "#count"   : 1,

    "comments" : int,
    "date"     : datetime.datetime(2024, 4, 19, 17, 25, 48),
    "name"     : "451872212_1144847833414253_8993539189674481418_n",
    "id"       : "1165557851291824",
    "reactions": int,
    "username" : "Facebook",
    "views"    : int,
},

{
    "#url"     : "https://www.facebook.com/watch/?v=738162178127348",
    "#category": ("", "facebook", "video"),
    "#class"   : facebook.FacebookVideoExtractor,
    "#count"   : 2,

    "comments" : int,
    "date"     : datetime.datetime(2023, 12, 2, 20, 16, 2),
    "name"     : "D2412EBD0F6CE0B7F8D314E41517F8BA_video_dashinit",
    "id"       : "738162178127348",
    "reactions": int,
    "username" : "Facebook",
    "views"    : int,
},

)
