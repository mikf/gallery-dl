# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import googledrive


__tests__ = (
{
    "#url"              : "https://drive.google.com/drive/folders/1J67pW33Y4o74DmZPh87SOcbz8xft8A-w",
    "#category"         : ("", "googledrive", "folder"),
    "#class"            : googledrive.GoogledriveFolderExtractor,
    "#files_count"      : int,
    "#folders_count"    : int,
    "#google_docs_count": int,

    "extension": "jpeg",
    "filename" : "Alexandre_Cabanel_-_Fallen_Angel.jpeg",
    "id"       : "1F_izQmNyL7Lj__jPww-QsXCZbinU4i7e",
    "url"      : "https://drive.google.com/uc?export=download&id=1F_izQmNyL7Lj__jPww-QsXCZbinU4i7e"
},
)
