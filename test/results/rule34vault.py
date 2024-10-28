# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import rule34vault


__tests__ = (
{
    "#url"  : "https://rule34vault.com/sfw",
    "#class": rule34vault.Rule34vaultTagExtractor,
    "#pattern": r"https://r34xyz\.b-cdn\.net/posts/\d+/\d+/\d+\.(jpg|mp4)",
    "#range"  : "1-10",
    "#count"  : 10,
},

{
    "#url"  : "https://rule34vault.com/post/486545",
    "#class": rule34vault.Rule34vaultPostExtractor,
    "#pattern"     : r"https://r34xyz\.b-cdn.net/posts/486/486545/486545\.jpg",
    "#sha1_content": "8f53c4c9d049842d23b51fb3cf8ce11bcbe21f07",
},

{
    "#url"    : "https://rule34vault.com/post/382937",
    "#comment": "video",
    "#class"  : rule34vault.Rule34vaultPostExtractor,
    "#pattern"     : r"https://r34xyz\.b-cdn.net/posts/382/382937/382937\.mp4",
    "#sha1_content": "b962e3e2304139767c3792508353e6e83a85a2af",
},

{
    "#url"  : "https://rule34vault.com/playlists/view/20164",
    "#class": rule34vault.Rule34vaultPlaylistExtractor,
    "#pattern": r"https://r34xyz\.b-cdn\.net/posts/\d+/\d+/\d+\.(jpg|mp4)",
    "#count"  : 55,
},

)
