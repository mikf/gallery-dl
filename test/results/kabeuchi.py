# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import kabeuchi
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://kabe-uchiroom.com/mypage/?id=919865303848255493",
    "#category": ("", "kabeuchi", "user"),
    "#class"   : kabeuchi.KabeuchiUserExtractor,
    "#pattern" : r"https://kabe-uchiroom\.com/accounts/upfile/3/919865303848255493/\w+\.jpe?g",
    "#count"   : ">= 24",
},

{
    "#url"     : "https://kabe-uchiroom.com/mypage/?id=123456789",
    "#category": ("", "kabeuchi", "user"),
    "#class"   : kabeuchi.KabeuchiUserExtractor,
    "#exception": exception.NotFoundError,
},

)
