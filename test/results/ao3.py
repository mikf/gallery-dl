# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import ao3


__tests__ = (
{
    "#url"     : "https://archiveofourown.org/works/47802076",
    "#class"   : ao3.Ao3WorkExtractor,
    "#results" : "https://archiveofourown.org/downloads/47802076/The_Wildcard.pdf?updated_at=1720398424",

    "author"   : "Flowers_for_ghouls",
    "bookmarks": range(100, 300),
    "chapters": {
        "120506833": "1. Showtime",
        "120866506": "2. A Comedy of Errors",
        "121739140": "3. Gifts",
        "121941313": "4. Date Night",
        "123054364": "5. Breaking the News",
        "123579898": "6. Isolated Events",
        "124258153": "7. The Home Stretch",
        "124886536": "8. Domestic Bliss",
        "125335270": "9. The Offer",
        "125871166": "10. The Promise",
        "126223879": "11. Gifts II",
        "126692398": "12. On the Move",
        "127471375": "13. The Fruit Vignettes",
        "128496448": "14. Respite",
        "128994919": "15. Changes",
        "129492154": "16. Halloween",
        "130379002": "17. GIfts III",
        "131066743": "18. R.A.S.B.E.W.",
        "131884072": "19. The Longest Night",
        "132730264": "20. Meeting the Pack",
        "133714876": "21. A Mystery",
        "134663854": "22. Growing Pains",
        "135499822": "23. Presentation Day",
        "136500946": "24. Revelations",
        "137857876": "25. The Retirement Plan",
        "139463056": "26. Two Birds, One Stone",
        "141697141": "27. New Management",
    },
    "comments" : range(800, 2000),
    "date"     : "dt:2023-06-11 00:00:00",
    "date_completed": "dt:2024-05-10 00:00:00",
    "date_updated"  : "dt:2024-07-08 00:27:04",
    "extension": "pdf",
    "filename" : "The_Wildcard",
    "id"       : 47802076,
    "lang"     : "en",
    "language" : "English",
    "likes"    : range(1000, 2000),
    "series"   : {
        "id"   : "4237024",
        "prev" : "",
        "next" : "57205801",
        "index": "1",
        "name" : "The Wildcard Universe",
    },
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
    "#class"   : ao3.Ao3WorkExtractor,
    "#options" : {"formats": ["epub", "mobi", "azw3", "pdf", "html"]},
    "#results" : (
        "https://archiveofourown.org/downloads/47802076/The_Wildcard.epub?updated_at=1720398424",
        "https://archiveofourown.org/downloads/47802076/The_Wildcard.mobi?updated_at=1720398424",
        "https://archiveofourown.org/downloads/47802076/The_Wildcard.azw3?updated_at=1720398424",
        "https://archiveofourown.org/downloads/47802076/The_Wildcard.pdf?updated_at=1720398424",
        "https://archiveofourown.org/downloads/47802076/The_Wildcard.html?updated_at=1720398424",
    ),
},

{
    "#url"     : "https://archiveofourown.org/works/12345",
    "#comment" : "restricted work / login required",
    "#class"   : ao3.Ao3WorkExtractor,
    "#auth"    : True,
    "#results" : "https://archiveofourown.org/downloads/12345/Unquenchable.pdf?updated_at=1716029699",
},

{
    "#url"     : "https://archiveofourown.org/series/1903930",
    "#class"   : ao3.Ao3SeriesExtractor,
    "#results" : (
        "https://archiveofourown.org/works/26131546",
        "https://archiveofourown.org/works/26291101",
        "https://archiveofourown.org/works/26325292",
    ),
},

{
    "#url"     : "https://archiveofourown.org/tags/Sunshine%20(Ghost%20Sweden%20Band)/works",
    "#class"   : ao3.Ao3TagExtractor,
    "#pattern" : ao3.Ao3WorkExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://archiveofourown.org/works/search?work_search%5Bquery%5D=air+fire+ice+water",
    "#class"   : ao3.Ao3SearchExtractor,
    "#pattern" : ao3.Ao3WorkExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://archiveofourown.org/users/Fyrelass",
    "#class"   : ao3.Ao3UserExtractor,
    "#results" : (
        "https://archiveofourown.org/users/Fyrelass/works",
        "https://archiveofourown.org/users/Fyrelass/series",
    ),
},
{
    "#url"     : "https://archiveofourown.com/users/Fyrelass",
    "#class"   : ao3.Ao3UserExtractor,
},
{
    "#url"     : "https://archiveofourown.net/users/Fyrelass",
    "#class"   : ao3.Ao3UserExtractor,
},
{
    "#url"     : "https://ao3.org/users/Fyrelass",
    "#class"   : ao3.Ao3UserExtractor,
},

{
    "#url"     : "https://archiveofourown.org/users/Fyrelass/profile",
    "#class"   : ao3.Ao3UserExtractor,
},

{
    "#url"     : "https://archiveofourown.org/users/Fyrelass/pseuds/Aileen%20Autarkeia",
    "#class"   : ao3.Ao3UserExtractor,
},

{
    "#url"     : "https://archiveofourown.org/users/Fyrelass/works",
    "#class"   : ao3.Ao3UserWorksExtractor,
    "#auth"    : False,
    "#results" : (
        "https://archiveofourown.org/works/55035061",
        "https://archiveofourown.org/works/58979287",
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
    "#class"   : ao3.Ao3UserSeriesExtractor,
    "#auth"    : False,
    "#results" : (
        "https://archiveofourown.org/series/3821575",
    ),
},

{
    "#url"     : "https://archiveofourown.org/users/Fyrelass/bookmarks",
    "#class"   : ao3.Ao3UserBookmarkExtractor,
    "#pattern" : r"https://archiveofourown\.org/(work|serie)s/\d+",
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://archiveofourown.org/users/mikf/subscriptions",
    "#class"   : ao3.Ao3SubscriptionsExtractor,
    "#auth"    : True,
    "#pattern" : r"https://archiveofourown\.org/(work|serie|user)s/\w+",
    "#count"   : range(20, 30),
},

)
