# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wikiart


__tests__ = (
{
    "#url"     : "https://www.wikiart.org/en/thomas-cole",
    "#category": ("", "wikiart", "artist"),
    "#class"   : wikiart.WikiartArtistExtractor,
    "#sha1_url"     : "6844f207a5063c499fc1d5651b03127bc4fe2f73",
    "#sha1_metadata": "09230b5f504697119e267349bf92487e657a7384",
},

{
    "#url"     : "https://www.wikiart.org/en/thomas-cole/the-departure-1838",
    "#category": ("", "wikiart", "image"),
    "#class"   : wikiart.WikiartImageExtractor,
    "#sha1_url"     : "976cc2545f308a650b5dbb35c29d3cee0f4673b3",
    "#sha1_metadata": "8e80cdcb01c1fedb934633d1c4c3ab0419cfbedf",
},

{
    "#url"     : "https://www.wikiart.org/en/huang-shen/summer",
    "#comment" : "no year or '-' in slug",
    "#category": ("", "wikiart", "image"),
    "#class"   : wikiart.WikiartImageExtractor,
    "#sha1_url": "d7f60118c34067b2b37d9577e412dc1477b94207",
},

{
    "#url"     : "https://www.wikiart.org/en/paintings-by-media/grisaille",
    "#category": ("", "wikiart", "artworks"),
    "#class"   : wikiart.WikiartArtworksExtractor,
    "#sha1_url": "36e054fcb3363b7f085c81f4778e6db3994e56a3",
},

{
    "#url"     : "https://www.wikiart.org/en/artists-by-century/12",
    "#category": ("", "wikiart", "artists"),
    "#class"   : wikiart.WikiartArtistsExtractor,
    "#pattern" : wikiart.WikiartArtistExtractor.pattern,
    "#count"   : ">= 8",
},

)
