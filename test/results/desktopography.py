# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import desktopography


__tests__ = (
{
    "#url"     : "https://desktopography.net/",
    "#category": ("", "desktopography", "site"),
    "#class"   : desktopography.DesktopographySiteExtractor,
},

{
    "#url"     : "https://desktopography.net/exhibition-2020/",
    "#category": ("", "desktopography", "exhibition"),
    "#class"   : desktopography.DesktopographyExhibitionExtractor,
},

{
    "#url"     : "https://desktopography.net/portfolios/new-era/",
    "#category": ("", "desktopography", "entry"),
    "#class"   : desktopography.DesktopographyEntryExtractor,
},

)
