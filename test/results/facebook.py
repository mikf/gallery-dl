# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import facebook
from gallery_dl import exception
import datetime


__tests__ = (
{
    "#url"     : "https://www.facebook.com/facebook",
    "#class"   : facebook.FacebookUserExtractor,
    "#results" : "https://www.facebook.com/facebook/photos"
},

{
    "#url"     : "https://www.facebook.com/people/facebook/100064860875397/?sk=photos",
    "#class"   : facebook.FacebookUserExtractor,
    "#results" : "https://www.facebook.com/100064860875397/photos"
},

{
    "#url"     : "https://www.facebook.com/profile.php?id=100064860875397",
    "#class"   : facebook.FacebookUserExtractor,
    "#results" : "https://www.facebook.com/100064860875397/photos"
},

{
    "#url"     : "https://www.facebook.com/facebook/photos",
    "#class"   : facebook.FacebookPhotosExtractor,

    "#range"   : "1-3",
    "#count"   : 3,
},

{
    "#url"     : "https://www.facebook.com/100064860875397/photos",
    "#class"   : facebook.FacebookPhotosExtractor,

    "#range"   : "1-3",
    "#count"   : 3,
},

{
    "#url"     : "https://www.facebook.com/profile.php?id=100074229772340/photos",
    "#comment" : "pfbid user ID (#7953)",
    "#class"   : facebook.FacebookPhotosExtractor,
    "#range"   : "1",

    "user_id"   : "100074229772340",
    "user_pfbid": r"re:pfbid0x\w{64}",
},

{
    "#url"     : "https://www.facebook.com/facebook/photos_by",
    "#class"   : facebook.FacebookPhotosExtractor,
},

{
    "#url"     : "https://www.facebook.com/brando.cha.3/photos",
    "#comment" : "empty '/photos' page / missing 'set_id' value (#7962)",
    "#class"   : facebook.FacebookPhotosExtractor,
    "#count"   : 0,
},

{
    "#url"      : "https://www.facebook.com/Forgetmen0w/photos",
    "#comment"  : "'This content isn't available right now'",
    "#class"    : facebook.FacebookPhotosExtractor,
    "#exception": exception.AuthRequired,
},

{
    "#url"     : "https://www.facebook.com/facebook/avatar",
    "#class"   : facebook.FacebookAvatarExtractor,
    "#pattern" : r"https://scontent-[^7?#]+\.fbcdn\.net/v/t39.30808-6/380700650_10162533193146729_2379134611963304810_n.jpg?.+",
    "#count"   : 1,

    "caption"  : "",
    "count"    : 1,
    "date"     : "dt:2023-10-06 21:13:59",
    "extension": "jpg",
    "filename" : str,
    "id"       : "736550615183628",
    "num"      : 1,
    "set_id"   : "a.736550601850296",
    "type"     : "avatar",
    "url"      : str,
    "user_id"  : "100064860875397",
    "username" : "Facebook",
},

{
    "#url"     : "https://www.facebook.com/brando.cha.3/avatar",
    "#comment" : "empty '/photos_of' page (#7962)",
    "#class"   : facebook.FacebookAvatarExtractor,
    "#count"   : 1,

    "date"      : "dt:2020-01-23 17:54:22",
    "id"        : "104622291093002",
    "set_id"    : "a.104622317759666",
    "type"      : "avatar",
    "user_id"   : "100046356937542",
    "user_pfbid": r"re:pfbid0x\w{64}",
    "username"  : "Throwaway Idk",
},

{
    "#url"     : "https://www.facebook.com/media/set/?set=a.10152716010956729&type=3",
    "#class"   : facebook.FacebookSetExtractor,
    "#count"   : 6,
},

{
    "#url"     : "https://www.facebook.com/joho.press.jp/posts/pfbid02mfFRpVkErLQxQ8cpD2f1hwXEVsFzK8kfNBKdK2Jndnx6AkmMQZuXhovwDgwvoDNil",
    "#class"   : facebook.FacebookSetExtractor,
    "#range"   : "1-3",
    "#count"   : 3,

    "set_id"   : "pcb.1160563418981189",
    "user_id"  : "100050826247807",
    "username" : "情報プレスα",
},

{
    "#url"     : "https://www.facebook.com/photo/?fbid=10152716011076729&set=a.10152716010956729&setextract",
    "#class"   : facebook.FacebookSetExtractor,
    "#count"   : 4,
},

{
    "#url"     : "https://www.facebook.com/photo.php?fbid=10165113568399554&set=t.100064860875397&type=3",
    "#class"   : facebook.FacebookPhotoExtractor,
},

{
    "#url"     : "https://www.facebook.com/photo/?fbid=10160743390456729",
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
    "#class"   : facebook.FacebookPhotoExtractor,
},

{
    "#url"     : "https://www.facebook.com/Facebook/photos/a.10152716010956729/10152716011076729",
    "#class"   : facebook.FacebookPhotoExtractor,
    "#count"   : 1,

    "caption"  : "",
    "date"     : datetime.datetime(2014, 5, 3, 0, 44, 47),
    "filename" : str,
    "extension": "png",
    "id"       : "10152716011076729",
    "set_id"   : "a.10152716010956729",
    "url"      : str,
    "user_id"  : "100064860875397",
    "user_pfbid": "",
    "username" : "Facebook",
},

{
    "#url"     : "https://www.facebook.com/photo.php?fbid=1143447107814264&set=pb.100064469571787.-2207520000&type=3",
    "#class"   : facebook.FacebookPhotoExtractor,
    "#count"   : 1,

    "caption"  : "Wanting to post a pic on Stories but it’s too small? 😡❌\n\nTry using Meta AI to make the pic fit your screen 😇✅\n\n(Available in most of the US)",
    "date"     : "dt:2025-05-30 18:47:34",
    "extension": "jpg",
    "id"       : "1143447107814264",
    "set_id"   : "a.596799269145720",
    "user_id"  : "100064469571787",
    "user_pfbid": "",
    "username" : "Instagram",
},

{
    "#url"     : "https://www.facebook.com/photo/?fbid=221820450302279",
    "#comment" : "pfbid user ID (#7953)",
    "#class"   : facebook.FacebookPhotoExtractor,

    "date"    : "dt:2023-02-05 22:41:02",
    "id"      : "221820450302279",
    "set_id"  : "a.109762038174788",
    "user_id" : "100074229772340",
    "user_pfbid": r"re:pfbid0x\w{64}",
    "username": "Throwaway Kwon",
},

{
    "#url"     : "https://www.facebook.com/photo.php?fbid=1156625586261770",
    "#comment" : "surrogate pair in 'caption' data (#6599)",
    "#class"   : facebook.FacebookPhotoExtractor,

    "caption"  : "A century of innovation parked side by side.\n\n📸: Vocabutesla via X",
},

{
    "#url"     : "https://www.facebook.com/photo.php?fbid=989340003138066&set=pb.100061862277212.-2207520000&type=3",
    "#comment" : "no 'publish_time' (#7151)",
    "#class"   : facebook.FacebookPhotoExtractor,

    "date"     : "dt:2025-02-25 15:00:09",
},

{
    "#url"     : "https://www.facebook.com/watch/?v=1165557851291824",
    "#class"   : facebook.FacebookVideoExtractor,
    "#count"   : 1,

    "date"     : datetime.datetime(2024, 4, 19, 17, 25, 48),
    "filename" : str,
    "id"       : "1165557851291824",
    "url"      : str,
    "user_id"  : "100064860875397",
    "username" : "Facebook",
},

{
    "#url"     : "https://www.facebook.com/100064860875397/videos/644342003942740",
    "#class"   : facebook.FacebookVideoExtractor,
    "#count"   : 2,

    "filename" : str,
    "extension": {"mp4", "m4a"},
    "id"       : "644342003942740",
    "url"      : str,
    "user_id"  : "100064860875397",
    "username" : "Facebook",
},

)
