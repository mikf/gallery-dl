# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import dynastyscans


__tests__ = (
{
    "#url"     : "http://dynasty-scans.com/chapters/hitoribocchi_no_oo_seikatsu_ch33",
    "#category": ("", "dynastyscans", "chapter"),
    "#class"   : dynastyscans.DynastyscansChapterExtractor,
    "#sha1_url"     : "3cafa527fecec27a66f35e038c0c53e35d5e4317",
    "#sha1_metadata": "7b134f2093813d45774cc68a3cd199ffce3e6fd3",
},

{
    "#url"     : "http://dynasty-scans.com/chapters/new_game_the_spinoff_special_13",
    "#category": ("", "dynastyscans", "chapter"),
    "#class"   : dynastyscans.DynastyscansChapterExtractor,
    "#sha1_url"     : "047fa6d58f90272883157a80fbf1e6f03ea5bbab",
    "#sha1_metadata": "62dc42e9025c79bdd3e26e026a690f4c28548fd4",
},

{
    "#url"     : "https://dynasty-scans.com/series/hitoribocchi_no_oo_seikatsu",
    "#category": ("", "dynastyscans", "manga"),
    "#class"   : dynastyscans.DynastyscansMangaExtractor,
    "#pattern" : dynastyscans.DynastyscansChapterExtractor.pattern,
    "#count"   : ">= 100",
},

{
    "#url"     : "https://dynasty-scans.com/images?with[]=4930&with[]=5211",
    "#category": ("", "dynastyscans", "search"),
    "#class"   : dynastyscans.DynastyscansSearchExtractor,

    "#sha1_metadata": "67690b4e21f59746f112803cba4c4d81fcbb9dbd",
    "#results"      : (
        "https://dynasty-scans.com/system/images_images/000/032/932/full/66051624_p0.webp",
        "https://dynasty-scans.com/system/images_images/000/021/368/full/KEIGI_32-1467964487873486851-img1.webp",
        "https://dynasty-scans.com/system/images_images/000/004/596/full/tortoise.webp",
        "https://dynasty-scans.com/system/images_images/000/003/206/full/1f01f72e19b98bf0083d323e3c28e4bf.webp",
        "https://dynasty-scans.com/system/images_images/000/000/535/full/8564987.webp",
    ),
},

{
    "#url"     : "https://dynasty-scans.com/images",
    "#category": ("", "dynastyscans", "search"),
    "#class"   : dynastyscans.DynastyscansSearchExtractor,
    "#range"   : "1",
    "#count"   : 1,
},

{
    "#url"     : "https://dynasty-scans.com/images/1245",
    "#category": ("", "dynastyscans", "image"),
    "#class"   : dynastyscans.DynastyscansImageExtractor,
    "#sha1_url"     : "877054defac8ea2bbaeb632db176037668c73eea",
    "#sha1_metadata": "9f6fd139c372203dcf7237e662a80963ab070cb0",
},

{
    "#url"     : "https://dynasty-scans.com/anthologies/%C3%A9clair",
    "#class"   : dynastyscans.DynastyscansAnthologyExtractor,
    "#pattern" : dynastyscans.DynastyscansChapterExtractor.pattern,
    "#options" : {"metadata": True},
    "#count"   : 8,

    "alert": [
        "This manga has been licensed",
        "Content licensed for English release has been removed from the reader. You can support the author by purchasing the title when it becomes available.",
    ],
    "anthology"     : "Éclair",
    "author"        : {"Canno", "Kawanami Izumi", "Kagero", "Mekimeki Oukoku", "Itou Hachi", "Isaki Uta", "Nakatani Nio", "Kitao Taki"},
    "date"          : "type:datetime",
    "date_updated"  : "type:datetime",
    "description"   : "<p>A compilation of one-shots from some of the best and most popular recent Yuri mangaka, including Canno (A Kiss and a White Lily for my Dearest Girl), Nakatani Nio (Bloom into you), Amano Shunita (Ayame 14), Itou Hachi (Isn't the Moon Beautiful?/Sayuri's Sister is an Angel) and many more.</p>\n\n<p>A must have for any collection, in my opinion, and a great chance to support all of the fabulous artists at once by buying yourself a copy! - Estherlea</p>",
    "scanlator"     : {"Estherlea", "/u/ Scanlations"},
    "status"        : "Licensed",
    "title"         : str,
    "tags"          : list,
},

{
    "#url"     : "https://dynasty-scans.com/anthologies/aashi_to_watashi_gyaru_yuri_anthology",
    "#class"   : dynastyscans.DynastyscansAnthologyExtractor,
    "#results" : "https://dynasty-scans.com/chapters/dont_call_me_senpai",

    "!alert"        : (),
    "!description"  : """<p><a href="https://dynasty-scans.com/anthologies/aashi_to_watashi_gyaru_yuri_anthology_volume_2">Volume 2</a></p>""",
    "!status"       : "",
    "anthology"     : "Aashi to Watashi - Gyaru Yuri Anthology",
    "author"        : "keyyan",
    "date"          : "dt:2024-03-30 04:07:10",
    "date_updated"  : "dt:2025-04-04 20:21:36",
    "scanlator"     : "Arka",
    "title"         : '''Don't Call Me "Senpai"''',
    "tags"          : [
        "big breasts",
        "childhood friends",
        "ecchi",
        "gyaru",
        "height gap",
        "prequel",
        "romance",
        "school girl",
        "yuri",
    ],
},

)
