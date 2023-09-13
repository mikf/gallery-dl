# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import soundgasm


__tests__ = (
{
    "#url"     : "https://soundgasm.net/u/ClassWarAndPuppies2/687-Otto-von-Toontown-12822",
    "#category": ("", "soundgasm", "audio"),
    "#class"   : soundgasm.SoundgasmAudioExtractor,
    "#pattern" : r"https://media\.soundgasm\.net/sounds/26cb2b23b2f2c6094b40ee3a9167271e274b570a\.m4a",

    "description": "We celebrate today’s important prisoner swap, and finally bring the 2022 mid-terms to a close with Raphael Warnock’s defeat of Herschel Walker in Georgia. Then, we take a look at the Qanon-addled attempt to overthrow the German government and install Heinrich XIII Prince of Reuss as kaiser.",
    "extension"  : "m4a",
    "filename"   : "26cb2b23b2f2c6094b40ee3a9167271e274b570a",
    "slug"       : "687-Otto-von-Toontown-12822",
    "title"      : "687 - Otto von Toontown (12/8/22)",
    "user"       : "ClassWarAndPuppies2",
},

{
    "#url"     : "https://www.soundgasm.net/user/ClassWarAndPuppies2/687-Otto-von-Toontown-12822",
    "#category": ("", "soundgasm", "audio"),
    "#class"   : soundgasm.SoundgasmAudioExtractor,
},

{
    "#url"     : "https://soundgasm.net/u/fierce-aphrodite",
    "#category": ("", "soundgasm", "user"),
    "#class"   : soundgasm.SoundgasmUserExtractor,
    "#pattern" : r"https://media\.soundgasm\.net/sounds/[0-9a-f]{40}\.m4a",
    "#count"   : ">= 15",

    "description": str,
    "extension"  : "m4a",
    "filename"   : r"re:^[0-9a-f]{40}$",
    "slug"       : str,
    "title"      : str,
    "url"        : str,
    "user"       : "fierce-aphrodite",
},

)
