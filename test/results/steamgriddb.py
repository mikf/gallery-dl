# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import steamgriddb
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.steamgriddb.com/grid/368023",
    "#comment" : "deleted",
    "#category": ("", "steamgriddb", "asset"),
    "#class"   : steamgriddb.SteamgriddbAssetExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.steamgriddb.com/grid/132605",
    "#category": ("", "steamgriddb", "asset"),
    "#class"   : steamgriddb.SteamgriddbAssetExtractor,
    "#count"   : 2,
    "#sha1_url"    : "4ff9158c008a1f01921d7553bcabf5e6204cdc79",
    "#sha1_content": "bc16c5eebf71463abdb33cfbf4b45a2fe092a2b2",

    "game": {
        "id"  : 5247997,
        "name": "OMORI",
    },
},

{
    "#url"     : "https://www.steamgriddb.com/grid/132605",
    "#category": ("", "steamgriddb", "asset"),
    "#class"   : steamgriddb.SteamgriddbAssetExtractor,
    "#options" : {"download-fake-png": False},
    "#count"   : 1,
    "#sha1_url"    : "f6819c593ff65f15864796fb89581f05d21adddb",
    "#sha1_content": "0d9e6114dd8bb9699182fbb7c6bd9064d8b0b6cd",

    "game": {
        "id"  : 5247997,
        "name": "OMORI",
    },
},

{
    "#url"     : "https://www.steamgriddb.com/hero/61104",
    "#category": ("", "steamgriddb", "asset"),
    "#class"   : steamgriddb.SteamgriddbAssetExtractor,
},

{
    "#url"     : "https://www.steamgriddb.com/logo/9610",
    "#category": ("", "steamgriddb", "asset"),
    "#class"   : steamgriddb.SteamgriddbAssetExtractor,
},

{
    "#url"     : "https://www.steamgriddb.com/icon/173",
    "#category": ("", "steamgriddb", "asset"),
    "#class"   : steamgriddb.SteamgriddbAssetExtractor,
},

{
    "#url"     : "https://www.steamgriddb.com/game/5259324/grids",
    "#category": ("", "steamgriddb", "grids"),
    "#class"   : steamgriddb.SteamgriddbGridsExtractor,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://www.steamgriddb.com/game/5259324/grids",
    "#category": ("", "steamgriddb", "grids"),
    "#class"   : steamgriddb.SteamgriddbGridsExtractor,
    "#options" : {"humor": False, "epilepsy": False, "untagged": False},
    "#range"   : "1-33",
    "#count"   : 33,
},

{
    "#url"     : "https://www.steamgriddb.com/game/5331605/heroes",
    "#category": ("", "steamgriddb", "heroes"),
    "#class"   : steamgriddb.SteamgriddbHeroesExtractor,
},

{
    "#url"     : "https://www.steamgriddb.com/game/5255394/logos",
    "#category": ("", "steamgriddb", "logos"),
    "#class"   : steamgriddb.SteamgriddbLogosExtractor,
},

{
    "#url"     : "https://www.steamgriddb.com/game/5279790/icons",
    "#category": ("", "steamgriddb", "icons"),
    "#class"   : steamgriddb.SteamgriddbIconsExtractor,
},

{
    "#url"     : "https://www.steamgriddb.com/collection/332/grids",
    "#category": ("", "steamgriddb", "grids"),
    "#class"   : steamgriddb.SteamgriddbGridsExtractor,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://www.steamgriddb.com/collection/332/heroes",
    "#category": ("", "steamgriddb", "heroes"),
    "#class"   : steamgriddb.SteamgriddbHeroesExtractor,
    "#options" : {"animated": False},
    "#count"   : 0,
},

)
