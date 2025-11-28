# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import audiochan


__tests__ = (
{
    "#url"     : "https://audiochan.com/a/pBP1V1ODEV2od9CjLu",
    "#class"   : audiochan.AudiochanAudioExtractor,
    "#pattern" : r"https://stream.audiochan.com/v\?token=YXVkaW9zL2Q4YjA1ZWEzLWU0ZGItNGU2NC05MzZiLTQzNmI3MmM4OTViMS9sOTBCOFI0ajhjS0NFSmNwa2kubXAz&exp=\d+&st=\w+",
    "#count"   : 1,
},

{
    "#url"     : "https://audiochan.com/u/lil_lovergirl",
    "#class"   : audiochan.AudiochanUserExtractor,
    "#pattern" : r"https://stream\.audiochan\.com/v\?token=\w+\&exp=\d+\&st=\w+",
    "#count"   : 35,
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
    ),
},

)
