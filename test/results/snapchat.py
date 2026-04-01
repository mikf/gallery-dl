# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import snapchat

BASE_DOMAIN_PATTERN = r"https://(?:cf-st|bolt-gcdn)"
AVATAR_PATTERN = BASE_DOMAIN_PATTERN + r".sc-cdn.net/(?:aps/bolt|3d/render)/[^/?#.]+\.[^/?#.]+"
SNAP_PATTERN = BASE_DOMAIN_PATTERN + r".sc-cdn.net/[dju]/[^/?#]+\?mo=[^/?#.]+&uc=\d+"


__tests__ = (
{
    "#url"      : "https://www.snapchat.com/@snackattackshow/avatar",
    "#comment"  : "Avatar",
    "#category" : ("", "snapchat", "avatar"),
    "#class"    : snapchat.SnapchatAvatarExtractor,
    "#pattern"  : AVATAR_PATTERN,
    "user"      : "snackattackshow",
},
{
    "#url"      : "https://www.snapchat.com/@idontexistabc123xyz/avatar",
    "#comment"  : "Avatar (Non-Existent)",
    "#category" : ("", "snapchat", "avatar"),
    "#class"    : snapchat.SnapchatAvatarExtractor,
    "#exception": "HttpError",
},

{
    "#url"      : "https://www.snapchat.com/@snackattackshow/PnJFM8uuTRWo90OsrEH5pwAAgeGZvd2RrZGxxAZ1I2NonAZ1I2NmfAAAAAA",
    "#comment"  : '"Timed" Story (difficult to test; if the user does not have a story with a purple-outline, this test will fail)',
    "#category" : ("", "snapchat", "story"),
    "#class"    : snapchat.SnapchatStoryExtractor,
    "#pattern"  : SNAP_PATTERN,
    "user"      : "snackattackshow",
},
{
    "#url"      : "https://www.snapchat.com/@snackattackshow/highlight/c3050cba-2f43-4e06-8ac4-d79069bac22f",
    "#comment"  : 'Story/Highlight (also difficult to test, as the website will only know about the latest stories)',
    "#category" : ("", "snapchat", "story"),
    "#class"    : snapchat.SnapchatStoryExtractor,
    "#pattern"  : SNAP_PATTERN,
    "#count"    : 1,
    "id"        : "c3050cba-2f43-4e06-8ac4-d79069bac22f",
    "user"      : "snackattackshow",
},
{
    "#url"      : "https://www.snapchat.com/@snackattackshow/highlight/020d67db-8779-497c-ae95-06371c42c11d",
    "#comment"  : 'Story/Highlight Multiple Items (also difficult to test, as the website will only know about the latest stories)',
    "#category" : ("", "snapchat", "story"),
    "#class"    : snapchat.SnapchatStoryExtractor,
    "#pattern"  : SNAP_PATTERN,
    "#count"    : 2,
    "id"        : "020d67db-8779-497c-ae95-06371c42c11d",
    "user"      : "snackattackshow",
},
{
    "#url"      : "https://www.snapchat.com/@idontexistabc123xyz/highlight/020d67db-8779-497c-ae95-06371c42c11d",
    "#comment"  : "Story/Highlight (Non-Existent)",
    "#category" : ("", "snapchat", "story"),
    "#class"    : snapchat.SnapchatStoryExtractor,
    "#exception": "HttpError",
},

{
    "#url"      : "https://www.snapchat.com/@manahil33922/spotlight/W7_EDlXWTBiXAEEniNoMPwAAYaGZnZm5tcXBsAZsRADeyAZsRADecAAAAAQ",
    "#comment"  : "Spotlight (with Username)",
    "#category" : ("", "snapchat", "spotlight"),
    "#class"    : snapchat.SnapchatSpotlightExtractor,
    "#pattern"  : SNAP_PATTERN,
    "#count"    : 1,
    "id"        : "W7_EDlXWTBiXAEEniNoMPwAAYaGZnZm5tcXBsAZsRADeyAZsRADecAAAAAQ",
    "user"      : "manahil33922",
},
{
    "#url"      : "https://www.snapchat.com/spotlight/W7_EDlXWTBiXAEEniNoMPwAAYaGZnZm5tcXBsAZsRADeyAZsRADecAAAAAQ",
    "#comment"  : "Spotlight (without Username)",
    "#category" : ("", "snapchat", "spotlight"),
    "#class"    : snapchat.SnapchatSpotlightExtractor,
    "#pattern"  : SNAP_PATTERN,
    "#count"    : 1,
    "id"        : "W7_EDlXWTBiXAEEniNoMPwAAYaGZnZm5tcXBsAZsRADeyAZsRADecAAAAAQ",
    "user"      : "manahil33922",
},
{
    "#url"      : "https://www.snapchat.com/spotlight/W7_EDlXWTBiXAEEniNoMPwAAYaGZnZm5tcAAQ",
    "#comment"  : "Spotlight (Non-Existent)",
    "#category" : ("", "snapchat", "spotlight"),
    "#class"    : snapchat.SnapchatSpotlightExtractor,
    "#exception": "HttpError",
},

{
    "#url"      : "https://www.snapchat.com/@drkashmalahussa/stories",
    "#comment"  : "User Stories",
    "#category" : ("", "snapchat", "stories"),
    "#class"    : snapchat.SnapchatStoriesExtractor,
    "#pattern"  : SNAP_PATTERN,
    "#count"    : 4,
    "user"      : "drkashmalahussa",
},
{
    "#url"      : "https://www.snapchat.com/@drkashmalahussa/highlights",
    "#comment"  : "User Highlights",
    "#category" : ("", "snapchat", "stories"),
    "#class"    : snapchat.SnapchatStoriesExtractor,
    "#pattern"  : SNAP_PATTERN,
    "#count"    : 4,
    "user"      : "drkashmalahussa",
},
{
    "#url"      : "https://www.snapchat.com/@abc123123123123zzzzzzzgh/stories",
    "#comment"  : "User Stories (Non-Existent)",
    "#category" : ("", "snapchat", "stories"),
    "#class"    : snapchat.SnapchatStoriesExtractor,
    "#exception": "HttpError",
},

{
    "#url"      : "https://www.snapchat.com/@drkashmalahussa/spotlights",
    "#comment"  : "User Spotlights",
    "#category" : ("", "snapchat", "spotlights"),
    "#class"    : snapchat.SnapchatSpotlightsExtractor,
    "#pattern"  : SNAP_PATTERN,
    "#count"    : 13,
    "user"      : "drkashmalahussa",
},
{
    "#url"      : "https://www.snapchat.com/@abc123123123123zzzzzzzgh/spotlights",
    "#comment"  : "User Spotlights (Non-Existent)",
    "#category" : ("", "snapchat", "spotlights"),
    "#class"    : snapchat.SnapchatSpotlightsExtractor,
    "#exception": "HttpError",
},

{
    "#url"      : "https://www.snapchat.com/@drkashmalahussa",
    "#comment"  : "User",
    "#category" : ("", "snapchat", "user"),
    "#class"    : snapchat.SnapchatUserExtractor,
    "#pattern"  : r"(?:" + AVATAR_PATTERN + r"|" + SNAP_PATTERN + r")",
    "#count"    : 18,
    "user"      : "drkashmalahussa",
},

{
    "#url"      : "https://www.snapchat.com/add/drkashmalahussa",
    "#comment"  : "User (/add/ Variant)",
    "#category" : ("", "snapchat", "user"),
    "#class"    : snapchat.SnapchatUserExtractor,
    "#pattern"  : r"(?:" + AVATAR_PATTERN + r"|" + SNAP_PATTERN + r")",
    "#count"    : 18,
    "user"      : "drkashmalahussa",
},
{
    "#url"      : "https://www.snapchat.com/@abc123123123123zzzzzzzgh",
    "#comment"  : "User (Non-Existent)",
    "#category" : ("", "snapchat", "user"),
    "#class"    : snapchat.SnapchatUserExtractor,
    "#exception": "HttpError",
},
)
