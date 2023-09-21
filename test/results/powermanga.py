# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import foolslide


__tests__ = (
{
    "#url"     : "https://read.powermanga.org/read/one_piece_digital_colour_comics/en/0/75/",
    "#category": ("foolslide", "powermanga", "chapter"),
    "#class"   : foolslide.FoolslideChapterExtractor,
    "#sha1_url"     : "854c5817f8f767e1bccd05fa9d58ffb5a4b09384",
    "#sha1_metadata": "a60c42f2634b7387899299d411ff494ed0ad6dbe",
},

{
    "#url"     : "https://read.powermanga.org/series/one_piece_digital_colour_comics/",
    "#category": ("foolslide", "powermanga", "manga"),
    "#class"   : foolslide.FoolslideMangaExtractor,
    "#count"   : ">= 1",

    "chapter"       : int,
    "chapter_minor" : str,
    "chapter_string": str,
    "group"         : "PowerManga",
    "lang"          : "en",
    "language"      : "English",
    "manga"         : "One Piece Digital Colour Comics",
    "title"         : str,
    "volume"        : int,
},

)
