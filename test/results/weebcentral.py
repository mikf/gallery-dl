# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import weebcentral


__tests__ = (
{
    "#url"     : "https://weebcentral.com/chapters/01J76XZ4PC3VW91BYFBQJA44C3",
    "#class"   : weebcentral.WeebcentralChapterExtractor,
    "#pattern" : r"https://official\.lowee\.us/manga/Aria/0067\.5-0\d\d\.png",
    "#count"   : 17,

    "author"       : ["AMANO Kozue"],
    "chapter"      : 67,
    "chapter_id"   : "01J76XZ4PC3VW91BYFBQJA44C3",
    "chapter_minor": ".5",
    "chapter_type" : "Navigation",
    "count"        : 17,
    "description"  : "On the planet Aqua, a world once known as Mars, Mizunashi Akari has just made her home in the town of Neo-VENEZIA, a futuristic imitation of the ancient city of Venice. The technology of \"Man Home\" (formerly Earth) has not entirely reached this planet, and Akari is alone, having no contact with family or friends. Nonetheless, the town, with its charming labyrinths of rivers and canals, becomes Akari's new infatuation, along with the dream of becoming a full-fledged gondolier. Reverting to a more \"primitive\" lifestyle and pursuing a new trade, the character of Akari becomes both adventurous and heartwarming all at once.",
    "extension"    : "png",
    "filename"     : r"re:0067\.5-0\d\d",
    "width"        : {1129, 2133},
    "height"       : {1511, 1600},
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "Aria",
    "manga_id"     : "01J76XY8G1GK8EJ9VQG92C3DKM",
    "official"     : True,
    "page"         : range(1, 17),
    "release"      : "2002",
    "status"       : "Complete",
    "type"         : "Manga",
    "tags"         : [
        "Adventure",
        "Comedy",
        "Drama",
        "Sci-fi",
        "Shounen",
        "Slice of Life",
    ],
},

{
    "#url"     : "https://weebcentral.com/series/01J76XY8G1GK8EJ9VQG92C3DKM/Aria",
    "#class"   : weebcentral.WeebcentralMangaExtractor,
    "#pattern" : weebcentral.WeebcentralChapterExtractor.pattern,
    "#count"   : 75,

    "author"       : ["AMANO Kozue"],
    "chapter"      : range(1, 70),
    "chapter_id"   : r"re:01J\w{23}",
    "chapter_minor": {"", ".5"},
    "chapter_type" : "Navigation",
    "date"         : "type:datetime",
    "description"  : "On the planet Aqua, a world once known as Mars, Mizunashi Akari has just made her home in the town of Neo-VENEZIA, a futuristic imitation of the ancient city of Venice. The technology of \"Man Home\" (formerly Earth) has not entirely reached this planet, and Akari is alone, having no contact with family or friends. Nonetheless, the town, with its charming labyrinths of rivers and canals, becomes Akari's new infatuation, along with the dream of becoming a full-fledged gondolier. Reverting to a more \"primitive\" lifestyle and pursuing a new trade, the character of Akari becomes both adventurous and heartwarming all at once.",
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "Aria",
    "manga_id"     : "01J76XY8G1GK8EJ9VQG92C3DKM",
    "official"     : True,
    "release"      : "2002",
    "status"       : "Complete",
    "type"         : "Manga",
    "tags"         : [
        "Adventure",
        "Comedy",
        "Drama",
        "Sci-fi",
        "Shounen",
        "Slice of Life",
    ],
},

)
