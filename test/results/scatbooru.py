# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import scatbooru


__tests__ = (
{
    "#url"     : "https://scatbooru.co.uk/?page=post&s=view&id=70576",
    "#category": ("gelbooru_v01", "scatbooru", "post"),
    "#class"   : scatbooru.ScatbooruPostExtractor,
    "#results" : "https://scatbooru.co.uk/images/23/792c5f1ebc1976cdbb782eb72e4816fa407ead05.png",

    "date"     : "dt:2026-03-17 18:16:16",
    "extension": "png",
    "file_url" : "https://scatbooru.co.uk/images/23/792c5f1ebc1976cdbb782eb72e4816fa407ead05.png",
    "filename" : "792c5f1ebc1976cdbb782eb72e4816fa407ead05",
    "width"    : "617",
    "height"   : "1599",
    "id"       : "70576",
    "md5"      : "792c5f1ebc1976cdbb782eb72e4816fa407ead05",
    "rating"   : "s",
    "score"    : "0",
    "size"     : "2.3MB",
    "source"   : '''https://x.com/paisley2themax/status/2027170112940216543/''',
    "tags"     : "2boys 2girls 4koma apologizing blonde_hair blue_eyes blue_overalls brown_hair brown_shoes bun_(food) castle comic crown cup dirty dirty_ass dress eating facial_hair fart farting_girl flower food gassy gassy_female gloves grape_juice green_hat green_shirt hat holding_fart indoors juice jumping luigi lunch mario mario_(series) meatballs multiple_boys multiple_girls mustache nervous_smile nintendo overalls paisley2themax pasta pink_dress plate princess princess_daisy princess_peach red_hat red_shirt ruuning shirt shoes smell smelly_anus smile spaghetti surprised sweatdrop table tomboy white_gloves yellow_dress",
    "uploader" : "Mr._Fart",
},

{
    "#url"     : "https://scatbooru.co.uk/?page=post&s=list&tags=4koma",
    "#category": ("gelbooru_v01", "scatbooru", "tag"),
    "#class"   : scatbooru.ScatbooruTagExtractor,
    "#results" : (
        "https://scatbooru.co.uk/images/23/792c5f1ebc1976cdbb782eb72e4816fa407ead05.png",
        "https://scatbooru.co.uk/images/20/3f84bc507e24cb764174c009e81adeba0f6f2092.png",
        "https://scatbooru.co.uk/images/20/c0a54c311e004c3cb916ef9e558d777cf8fcd949.png",
    ),

    "date"       : "type:datetime",
    "extension"  : "png",
    "file_url"   : str,
    "filename"   : "hash:sha1",
    "height"     : r"re:\d+",
    "id"         : {"70576", "66877", "66872"},
    "md5"        : "hash:sha1",
    "rating"     : {"s", "e"},
    "score"      : "0",
    "search_tags": "4koma",
    "size"       : str,
    "source"     : str,
    "tags"       : str,
    "uploader"   : "Mr._Fart",
    "width"      : r"re:\d+",
},

{
    "#url"     : "https://scatbooru.co.uk/?page=favorites&s=view&id=1",
    "#category": ("gelbooru_v01", "scatbooru", "favorite"),
    "#class"   : scatbooru.ScatbooruFavoriteExtractor,
},

)
