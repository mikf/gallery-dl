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
    "#url"     : "https://www.facebook.com/facebook/photos",
    "#category": ("", "facebook", "profile"),
    "#class"   : facebook.FacebookProfileExtractor,
},

{
    "#url"     : "https://www.facebook.com/facebook/photos_by",
    "#category": ("", "facebook", "profile"),
    "#class"   : facebook.FacebookProfileExtractor,
},

{
    "#url"     : "https://www.facebook.com/people/facebook/100064860875397/?sk=photos",
    "#category": ("", "facebook", "profile"),
    "#class"   : facebook.FacebookProfileExtractor,
},

{
    "#url"     : "https://www.facebook.com/profile.php?id=100064860875397",
    "#category": ("", "facebook", "profile"),
    "#class"   : facebook.FacebookProfileExtractor,
},

{
    "#url"     : "https://www.facebook.com/media/set/?set=a.10152716010956729&type=3",
    "#category": ("", "facebook", "set"),
    "#class"   : facebook.FacebookSetExtractor,
    "#count"   : 6,
},

{
    "#url"     : "https://www.facebook.com/joho.press.jp/posts/pfbid02mfFRpVkErLQxQ8cpD2f1hwXEVsFzK8kfNBKdK2Jndnx6AkmMQZuXhovwDgwvoDNil",
    "#category": ("", "facebook", "set"),
    "#class"   : facebook.FacebookSetExtractor,
    "#range"   : "1-3",
    "#count"   : 3,

    "set_id"   : "pcb.1160563418981189",
    "user_id"  : "100050826247807",
    "username" : "情報プレスα",
},

{
    "#url"     : "https://www.facebook.com/photo/?fbid=10152716011076729&set=a.10152716010956729&setextract",
    "#category": ("", "facebook", "set"),
    "#class"   : facebook.FacebookSetExtractor,
    "#count"   : 4,
},

{
    "#url"     : "https://www.facebook.com/photo.php?fbid=10165113568399554&set=t.100064860875397&type=3",
    "#category": ("", "facebook", "photo"),
    "#class"   : facebook.FacebookPhotoExtractor,
},

{
    "#url"     : "https://www.facebook.com/photo/?fbid=10160743390456729",
    "#category": ("", "facebook", "photo"),
    "#class"   : facebook.FacebookPhotoExtractor,
    "#count"   : 1,

    "caption"  : "They were on a break... #FriendsReunion #MoreTogether",
    "date"     : datetime.datetime(2021, 5, 27, 21, 55, 19),
    "filename" : "191053255_10160743390471729_9001965649022744000_n",
    "extension": "jpg",
    "id"       : "10160743390456729",
    "set_id"   : "a.494827881728",
    "url"      : str,
    "user_id"  : "100064860875397",
    "username" : "Facebook",
},

{
    "#url"     : "https://www.facebook.com/photo/?fbs=home&fbid=10160743390456729",
    "#category": ("", "facebook", "photo"),
    "#class"   : facebook.FacebookPhotoExtractor,
},

{
    "#url"     : "https://www.facebook.com/Facebook/photos/a.10152716010956729/10152716011076729",
    "#category": ("", "facebook", "photo"),
    "#class"   : facebook.FacebookPhotoExtractor,
    "#count"   : 1,

    "caption"  : "",
    "date"     : datetime.datetime(2014, 5, 3, 0, 44, 47),
    "filename" : "10334445_10152716011076729_6502314875328401420_n",
    "extension": "png",
    "id"       : "10152716011076729",
    "set_id"   : "a.10152716010956729",
    "url"      : str,
    "user_id"  : "100064860875397",
    "username" : "Facebook",
},

{
    "#url"     : "https://www.facebook.com/photo.php?fbid=1156625586261770",
    "#comment" : "surrogate pair in 'caption' data (#6599)",
    "#category": ("", "facebook", "photo"),
    "#class"   : facebook.FacebookPhotoExtractor,

    "caption"  : "A century of innovation parked side by side.\n\n📸: Vocabutesla via X",
},

{
    "#url"     : "https://www.facebook.com/watch/?v=1165557851291824",
    "#category": ("", "facebook", "video"),
    "#class"   : facebook.FacebookVideoExtractor,
    "#count"   : 1,

    "date"     : datetime.datetime(2024, 4, 19, 17, 25, 48),
    "filename" : "462125225_400524393116630_7457168924362807384_n",
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
    "#archive": False,

    "filename" : "1514198129001376",
    "id"       : "644342003942740",
    "url"      : str,
    "user_id"  : "100064860875397",
    "username" : "Facebook",
},

)
