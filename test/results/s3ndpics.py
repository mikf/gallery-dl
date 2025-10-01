# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import s3ndpics


__tests__ = (
{
    "#url"     : "https://s3nd.pics/post/68dce8098ef7a9effbdbafa1",
    "#class"   : s3ndpics.S3ndpicsPostExtractor,
    "#pattern" : r"https://s3\.s3nd\.pics/s3nd\-pics/uploads/68be9efde7238de1080bbeec/\d+\-\w+\.(jpe?g|mp4)",
    "#count"   : 10,

    "id"             : "68dce8098ef7a9effbdbafa1",
    "title"          : "Little meme dump 'o the mornin'",
    "count"          : 10,
    "num"            : range(1, 10),
    "date"           : "dt:2025-10-01 08:36:25",
    "date_updated"   : "type:datetime",
    "type"           : {"image", "video"},
    "extension"      : {"jpeg", "mp4"},
    "imageProcessed" : True,
    "isPublic"       : True,
    "favorites"      : int,
    "downvotes"      : int,
    "likes"          : int,
    "upvotes"        : int,
    "views"          : int,
    "locked"         : False,
    "lockedAt"       : None,
    "lockedBy"       : None,
    "moderatorTags"  : [],
    "photodnaConfidence": 0,
    "photodnaFlagged": False,
    "pinWeight"      : 0,
    "pinned"         : False,
    "pinnedAt"       : None,
    "suspendReason"  : None,
    "suspended"      : False,
    "suspendedAt"    : None,
    "suspendedBy"    : None,
    "description"    : """\
Did you know that penguins do a thing called "pebbling", where they offer a nice rock or pebble to other penguins they like, to make them feel nice and valued?

Consider then that I am not peddling my stolen memes, but pebbling them to ye wonderful sickos.

Hope you'll like it!\
""",
    "tags"           : [
        "#dump",
        "#meme",
    ],
    "user"           : {
        "_id"          : "68be9efde7238de1080bbeec",
        "avatar"       : "avatars/68be9efde7238de1080bbeec/1758616570175-avatar.jpg",
        "filteredUsers": [],
        "username"     : "wildscarf",
    },
},

{
    "#url"     : "https://s3nd.pics/post/68dce8098ef7a9effbdbafa1?tag=%23dump&context=search",
    "#class"   : s3ndpics.S3ndpicsPostExtractor,
},

{
    "#url"     : "https://s3nd.pics/user/cloacadeepinadragon",
    "#class"   : s3ndpics.S3ndpicsUserExtractor,
    "#pattern" : r"https://s3\.s3nd\.pics/s3nd\-pics/uploads/.+",
    "#count"   : 18,

    "date"           : "type:datetime",
    "date_updated"   : "type:datetime",
    "description"    : str,
    "filename"       : str,
    "extension"      : {"jpg", "jpeg", "png"},
    "id"             : str,
    "title"          : str,
    "total"          : 18,
    "type"           : "image",
    "tags"           : list,
    "user"           : {
        "_id"           : "68ba04803ffea95858f47613",
        "avatar"        : "avatars/68ba04803ffea95858f47613/1757021580703-avatar.jpg",
        "createdAt"     : "2025-09-04T21:28:32.452Z",
        "email"         : "egk251@gmail.com",
        "role"          : "user",
        "username"      : "cloacadeepinadragon",
    },
},

{
    "#url"     : "https://s3nd.pics/search?tag=%23memes",
    "#class"   : s3ndpics.S3ndpicsSearchExtractor,
    "#pattern" : r"https://s3\.s3nd\.pics/s3nd\-pics/uploads/\w+/.+\.(jpe?g|png|mp4)$",
    "#range"   : "1-50",
    "#count"   : 50,

    "search_tags": "#memes",
},

)
