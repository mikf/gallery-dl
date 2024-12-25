# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import weasyl


__tests__ = (
{
    "#url"     : "https://www.weasyl.com/~fiz/submissions/2031/a-wesley",
    "#category": ("", "weasyl", "submission"),
    "#class"   : weasyl.WeasylSubmissionExtractor,
    "#pattern" : "https://cdn.weasyl.com/~fiz/submissions/2031/41ebc1c2940be928532785dfbf35c37622664d2fbb8114c3b063df969562fc51/fiz-a-wesley.png",

    "comments"    : int,
    "date"        : "dt:2012-04-20 00:38:04",
    "description" : """<p>(flex)</p>
""",
    "favorites"   : int,
    "folder_name" : "Wesley Stuff",
    "folderid"    : 2081,
    "friends_only": False,
    "owner"       : "Fiz",
    "owner_login" : "fiz",
    "rating"      : "general",
    "submitid"    : 2031,
    "subtype"     : "visual",
    "tags"        : list,
    "title"       : "A Wesley!",
    "type"        : "submission",
    "views"       : int,
},

{
    "#url"     : "https://www.weasyl.com/submission/2031/a-wesley",
    "#category": ("", "weasyl", "submission"),
    "#class"   : weasyl.WeasylSubmissionExtractor,
},

{
    "#url"     : "https://www.weasyl.com/~tanidareal",
    "#category": ("", "weasyl", "submissions"),
    "#class"   : weasyl.WeasylSubmissionsExtractor,
    "#count"   : ">= 200",
},

{
    "#url"     : "https://www.weasyl.com/submissions/tanidareal",
    "#category": ("", "weasyl", "submissions"),
    "#class"   : weasyl.WeasylSubmissionsExtractor,
},

{
    "#url"     : "https://www.weasyl.com/~aro~so",
    "#category": ("", "weasyl", "submissions"),
    "#class"   : weasyl.WeasylSubmissionsExtractor,
},

{
    "#url"     : "https://www.weasyl.com/submissions/tanidareal?folderid=7403",
    "#category": ("", "weasyl", "folder"),
    "#class"   : weasyl.WeasylFolderExtractor,
    "#count"   : ">= 12",
},

{
    "#url"     : "https://www.weasyl.com/journal/17647/bbcode",
    "#category": ("", "weasyl", "journal"),
    "#class"   : weasyl.WeasylJournalExtractor,

    "title"  : "BBCode",
    "date"   : "dt:2013-09-19 23:11:23",
    "content": """<p><a>javascript:alert(42);</a></p>

<p>No more of that!</p>
""",
},

{
    "#url"     : "https://www.weasyl.com/journals/charmander",
    "#category": ("", "weasyl", "journals"),
    "#class"   : weasyl.WeasylJournalsExtractor,
    "#count"   : ">= 2",
},

{
    "#url"     : "https://www.weasyl.com/favorites?userid=184616&feature=submit",
    "#category": ("", "weasyl", "favorite"),
    "#class"   : weasyl.WeasylFavoriteExtractor,
    "#count"   : ">= 5",
},

{
    "#url"     : "https://www.weasyl.com/favorites/furoferre",
    "#category": ("", "weasyl", "favorite"),
    "#class"   : weasyl.WeasylFavoriteExtractor,
    "#count"   : ">= 5",
}

)
