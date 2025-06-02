# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import speakerdeck


__tests__ = (
{
    "#url"     : "https://speakerdeck.com/speakerdeck/introduction-to-speakerdeck",
    "#category": ("", "speakerdeck", "presentation"),
    "#class"   : speakerdeck.SpeakerdeckPresentationExtractor,
    "#pattern"     : r"https://files.speakerdeck.com/presentations/50021f75cf1db900020005e7/slide_\d+.jpg",
    "#count"       : 6,
    "#sha1_content": "75c7abf0969b0bcab23e0da9712c95ee5113db3a",

    "author"         : "Speaker Deck",
    "count"          : 6,
    "num"            : range(1, 6),
    "presentation"   : "introduction-to-speakerdeck",
    "presentation_id": "50021f75cf1db900020005e7",
    "title"          : "Introduction to SpeakerDeck",
    "user"           : "speakerdeck",
},

)
