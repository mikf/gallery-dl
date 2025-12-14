# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import comedywildlifephoto


__tests__ = (
{
    "#url"     : "https://www.comedywildlifephoto.com/gallery/finalists/2024_finalists.php",
    "#class"   : comedywildlifephoto.ComedywildlifephotoGalleryExtractor,
    "#pattern" : r"https://www\.comedywildlifephoto\.com/images/gallery/\d/000017\d\d_p\.webp",
    "#count"   : 44,

    "count"      : 44,
    "num"        : range(1, 44),
    "description": "<p>Here are the finalists from the 2024 Comedy Wildlife Photography Awards competition. Winners will be announced on the 10th of December 2024. Voting for the People's Choice Award runs from 26th September until 31st October.</p>",
    "caption"    : str,
    "filename"   : str,
    "extension"  : "webp",
    "width"      : range(750, 1600),
    "height"     : range(750, 1600),
    "section"    : "Gallery of Winners and Finalists",
    "title"      : "2024 Finalists",
},

{
    "#url"     : "https://www.comedywildlifephoto.com/gallery/finalists/2022_finalists.php",
    "#comment" : "empty 'description'",
    "#class"   : comedywildlifephoto.ComedywildlifephotoGalleryExtractor,
    "#range"   : "4",
    "#results" : "https://www.comedywildlifephoto.com/images/gallery/9/00001169_p.jpg",

    "count"      : 43,
    "num"        : 4,
    "description": "",
    "caption"    : "",
    "filename"   : "00001169_p",
    "extension"  : "jpg",
    "width"      : 1600,
    "height"     : 900,
    "section"    : "Gallery of Winners and Finalists",
    "title"      : "2022 Finalists",
},

)
