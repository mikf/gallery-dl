# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import ao3


__tests__ = (
{
    "#url"     : "https://archiveofourown.org/works/47802076",
    "#category": ("", "ao3", "work"),
    "#class"   : ao3.Ao3WorkExtractor,
    "#urls"    : "https://archiveofourown.org/downloads/47802076/The_Wildcard.pdf?updated_at=1720398424",

    "author"   : "Flowers_for_ghouls",
    "bookmarks": range(100, 300),
    "chapters" : 27,
    "comments" : range(800, 2000),
    "date"     : "dt:2023-06-11 00:00:00",
    "extension": "pdf",
    "filename" : "The_Wildcard",
    "id"       : 47802076,
    "lang"     : "en",
    "language" : "English",
    "likes"    : range(1000, 2000),
    "title"    : "The Wildcard",
    "views"    : range(34000, 50000),
    "words"    : 217549,

    "categories": [
        "Gen",
        "M/M",
    ],
    "characters": [
        "Dewdrop Ghoul | Fire Ghoul",
        "Aether | Quintessence Ghoul",
        "Multi Ghoul | Swiss Army Ghoul",
        "Rain | Water Ghoul",
        "Cirrus | Air Ghoulette",
        "Cumulus | Air Ghoulette",
        "Sunshine Ghoulette",
        "Mountain | Earth Ghoul",
        "Cardinal Copia",
        "Phantom Ghoul",
        "Aurora Ghoulette",
        "Sister Imperator (Ghost Sweden Band)",
    ],
    "fandom": [
        "Ghost (Sweden Band)",
    ],
    "rating": [
        "Mature",
    ],
    "relationships": [
        "Aether | Quintessence Ghoul/Dewdrop Ghoul | Fire Ghoul",
        "Multi Ghoul | Swiss Army Ghoul/Rain | Water Ghoul",
    ],
    "summary": [
        "Aether has been asked to stay at the ministry to manage the renovation of the new infirmary. It couldn’t have been worse timing. Barely days into the new tour, Dew realizes he’s carrying their first kit.",
    ],
    "tags": [
        "Domestic Fluff",
        "Pack Dynamics",
        "gratuitous fluff",
        "How do ghouls work?",
        "they don't even know",
        "but it's cute",
        "Pregnant Dewdrop",
        "Recreational Drug Use",
        "Cowbell!",
        "Protective Ghouls",
        "no beta we die like Nihil",
        "sick dewdrop",
        "TW: Vomiting",
        "Aether really loves Dew",
        "Nesting",
        "Ghoul Piles (Ghost Sweden Band)",
        "Angst",
        "Hurt/Comfort",
        "Original Ghoul Kit(s) (Ghost Sweden Band)",
        "Kit fic",
    ],
    "warnings": [
        "No Archive Warnings Apply",
    ],
},

{
    "#url"     : "https://archiveofourown.org/works/47802076",
    "#category": ("", "ao3", "work"),
    "#class"   : ao3.Ao3WorkExtractor,
    "#options" : {"formats": ["epub", "mobi", "azw3", "pdf", "html"]},
    "#urls"    : (
        "https://archiveofourown.org/downloads/47802076/The_Wildcard.epub?updated_at=1720398424",
        "https://archiveofourown.org/downloads/47802076/The_Wildcard.mobi?updated_at=1720398424",
        "https://archiveofourown.org/downloads/47802076/The_Wildcard.azw3?updated_at=1720398424",
        "https://archiveofourown.org/downloads/47802076/The_Wildcard.pdf?updated_at=1720398424",
        "https://archiveofourown.org/downloads/47802076/The_Wildcard.html?updated_at=1720398424",
    ),
},

{
    "#url"     : "https://archiveofourown.org/series/1903930",
    "#category": ("", "ao3", "series"),
    "#class"   : ao3.Ao3SeriesExtractor,
    "#urls"    : (
        "https://archiveofourown.org/works/26131546",
        "https://archiveofourown.org/works/26291101",
        "https://archiveofourown.org/works/26325292",
    ),
},

{
    "#url"     : "https://archiveofourown.org/tags/Sunshine%20(Ghost%20Sweden%20Band)/works",
    "#category": ("", "ao3", "tag"),
    "#class"   : ao3.Ao3TagExtractor,
    "#pattern" : ao3.Ao3WorkExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://archiveofourown.org/works/search?work_search%5Bquery%5D=air+fire+ice+water",
    "#category": ("", "ao3", "search"),
    "#class"   : ao3.Ao3SearchExtractor,
    "#pattern" : ao3.Ao3WorkExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://archiveofourown.org/users/Fyrelass",
    "#category": ("", "ao3", "user"),
    "#class"   : ao3.Ao3UserExtractor,
    "#urls"    : (
        "https://archiveofourown.org/users/Fyrelass/works",
        "https://archiveofourown.org/users/Fyrelass/series",
    ),
},

{
    "#url"     : "https://archiveofourown.org/users/Fyrelass/profile",
    "#category": ("", "ao3", "user"),
    "#class"   : ao3.Ao3UserExtractor,
},

{
    "#url"     : "https://archiveofourown.org/users/Fyrelass/pseuds/Aileen%20Autarkeia",
    "#category": ("", "ao3", "user"),
    "#class"   : ao3.Ao3UserExtractor,
},

{
    "#url"     : "https://archiveofourown.org/users/Fyrelass/works",
    "#category": ("", "ao3", "user-works"),
    "#class"   : ao3.Ao3UserWorksExtractor,
    "#urls"    : (
        "https://archiveofourown.org/works/55035061",
        "https://archiveofourown.org/works/52704457",
        "https://archiveofourown.org/works/52502743",
        "https://archiveofourown.org/works/52170409",
        "https://archiveofourown.org/works/52078558",
        "https://archiveofourown.org/works/51699982",
        "https://archiveofourown.org/works/51975193",
        "https://archiveofourown.org/works/51633877",
        "https://archiveofourown.org/works/51591436",
        "https://archiveofourown.org/works/50860891",
    ),
},

{
    "#url"     : "https://archiveofourown.org/users/Fyrelass/series",
    "#category": ("", "ao3", "user-series"),
    "#class"   : ao3.Ao3UserSeriesExtractor,
    "#urls"    : (
        "https://archiveofourown.org/series/3821575",
    ),
},

{
    "#url"     : "https://archiveofourown.org/users/Fyrelass/bookmarks",
    "#category": ("", "ao3", "user-bookmark"),
    "#class"   : ao3.Ao3UserBookmarkExtractor,
    "#pattern" : ao3.Ao3WorkExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

)
