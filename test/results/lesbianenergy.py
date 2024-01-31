# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import misskey


__tests__ = (
{
    "#url"     : "https://lesbian.energy/@rerorero",
    "#category": ("misskey", "lesbian.energy", "user"),
    "#class"   : misskey.MisskeyUserExtractor,
    "#pattern" : r"https://(lesbian.energy/files/\w+|.+/media_attachments/files/.+)",
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://lesbian.energy/@nano@mk.yopo.work",
    "#category": ("misskey", "lesbian.energy", "user"),
    "#class"   : misskey.MisskeyUserExtractor,
},

{
    "#url"     : "https://lesbian.energy/notes/995ig09wqy",
    "#category": ("misskey", "lesbian.energy", "note"),
    "#class"   : misskey.MisskeyNoteExtractor,
    "#count"   : 1,
},

{
    "#url"     : "https://lesbian.energy/notes/96ynd9w5kc",
    "#category": ("misskey", "lesbian.energy", "note"),
    "#class"   : misskey.MisskeyNoteExtractor,
},

{
    "#url"     : "https://lesbian.energy/my/favorites",
    "#category": ("misskey", "lesbian.energy", "favorite"),
    "#class"   : misskey.MisskeyFavoriteExtractor,
},

)
