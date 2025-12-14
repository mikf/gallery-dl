# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import audiochan


__tests__ = (
{
    "#url"     : "https://audiochan.com/a/pBP1V1ODEV2od9CjLu",
    "#class"   : audiochan.AudiochanAudioExtractor,
    "#pattern" : r"https://stream.audiochan.com/v\?token=YXVkaW9zL2Q4YjA1ZWEzLWU0ZGItNGU2NC05MzZiLTQzNmI3MmM4OTViMS9sOTBCOFI0ajhjS0NFSmNwa2kubXAz&exp=\d+&st=.+",
    "#count"   : 1,

    "description": [
        "author summary: ",
        "You wake up in the middle of the night, noticing that your boyfriend is still awake and restlessly moving around. Work-related worries are making him anxious and keeping him from falling asleep so you do your best to take care of him, calm him down, and help him get some rest."
    ],
    "user": {
        "username": "lil-lovergirl",
    },
},

{
    "#url"     : "https://audiochan.com/u/lil-lovergirl",
    "#class"   : audiochan.AudiochanUserExtractor,
    "#pattern" : r"https://stream\.audiochan\.com/v\?token=\w+\&exp=\d+\&st=.+",
    "#count"   : range(35, 50),

    "user": {
        "username": "lil-lovergirl",
    },
},

{
    "#url"     : "https://audiochan.com/c/qzrByaXAwTLVXRgC9m",
    "#class"   : audiochan.AudiochanCollectionExtractor,
    "#results" : (
        "https://content.audiochan.com/audios/d8b05ea3-e4db-4e64-936b-436b72c895b1/l90B8R4j8cKCEJcpki.mp3",
        "https://content.audiochan.com/audios/d8b05ea3-e4db-4e64-936b-436b72c895b1/IPI4XoXS1Z1Qn7oEiN.mp3",
        "https://content.audiochan.com/audios/d8b05ea3-e4db-4e64-936b-436b72c895b1/6kwizqnvUHttvUkXm6.mp3",
        "https://content.audiochan.com/audios/d8b05ea3-e4db-4e64-936b-436b72c895b1/zn81mtgXslfDd20Tu8.wav",
        "https://content.audiochan.com/audios/d8b05ea3-e4db-4e64-936b-436b72c895b1/Q33gP6yAg8jEM1C4Ic.mp3",
        "https://content.audiochan.com/audios/d8b05ea3-e4db-4e64-936b-436b72c895b1/Fwy5YxgK4zc7sQ9xx3.mp3",
        "https://content.audiochan.com/audios/d8b05ea3-e4db-4e64-936b-436b72c895b1/P3YrtAdKVekYb3BTgy.mp3",
        "https://content.audiochan.com/audios/d8b05ea3-e4db-4e64-936b-436b72c895b1/kWYsadsb4XgVh7YPVW.mp3",
    ),

    "collection": {
        "id": "6d7a89a4-e752-4772-923d-65783aee332e",
        "slug": "qzrByaXAwTLVXRgC9m",
        "title": "💗SFW",
    },
    "user": {
        "username": "lil-lovergirl",
    },
},

{
    "#url"     : "https://audiochan.com/search?q=Cozy&sort=trending&timeRange=all",
    "#class"   : audiochan.AudiochanSearchExtractor,
    "#count"   : range(15, 40),

    "search_tags": "Cozy",
    "description": list,
    "user": dict,
    "tags": list,
},

)
