# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hiperdex


__tests__ = (
{
    "#url"     : "https://hipertoon.com/manga/domestic-na-kanojo/154-5/",
    "#category": ("", "hiperdex", "chapter"),
    "#class"   : hiperdex.HiperdexChapterExtractor,
    "#pattern" : r"https://(1st)?hiper(dex|toon)\d?.(com|net|info|top)/wp-content/uploads/WP-manga/data/manga_\w+/[0-9a-f]{32}/\d+\.webp",
    "#count"   : 9,

    "artist"       : "Sasuga Kei",
    "author"       : "Sasuga Kei",
    "chapter"      : 154,
    "chapter_minor": ".5",
    "description"  : "Natsuo Fujii is in love with his teacher, Hina. Attempting to forget his feelings towards her, Natsuo goes to a mixer with his classmates where he meets an odd girl named Rui Tachibana. In a strange turn of events, Rui asks Natsuo to sneak out with her and do her a favor. To his surprise, their destination is Rui’s house—and her request is for him to have sex with her. There’s no love behind the act; she just wants to learn from the experience. Thinking that it might help him forget about Hina, Natsuo hesitantly agrees. After this unusual encounter Natsuo now faces a new problem. With his father remarrying, he ends up with a new pair of stepsisters; unfortunately, he knows these two girls all too well. He soon finds out his new siblings are none other than Hina and Rui! Now living with both the teacher he loves and the girl with whom he had his “first time,” Natsuo finds himself in an unexpected love triangle as he climbs ever closer towards adulthood.",
    "genre"        : list,
    "manga"        : "Domestic na Kanojo",
    "release"      : 2014,
    "score"        : float,
    "type"         : "Manga",
},

{
    "#url"     : "https://hiperdex.com/mangas/domestic-na-kanojo/154-5/",
    "#category": ("", "hiperdex", "chapter"),
    "#class"   : hiperdex.HiperdexChapterExtractor,
},

{
    "#url"     : "https://1sthiperdex.com/manga/domestic-na-kanojo/154-5/",
    "#category": ("", "hiperdex", "chapter"),
    "#class"   : hiperdex.HiperdexChapterExtractor,
},

{
    "#url"     : "https://hiperdex2.com/manga/domestic-na-kanojo/154-5/",
    "#category": ("", "hiperdex", "chapter"),
    "#class"   : hiperdex.HiperdexChapterExtractor,
},

{
    "#url"     : "https://hiperdex.net/manga/domestic-na-kanojo/154-5/",
    "#category": ("", "hiperdex", "chapter"),
    "#class"   : hiperdex.HiperdexChapterExtractor,
},

{
    "#url"     : "https://hiperdex.info/manga/domestic-na-kanojo/154-5/",
    "#category": ("", "hiperdex", "chapter"),
    "#class"   : hiperdex.HiperdexChapterExtractor,
},

{
    "#url"     : "https://hiperdex.top/manga/domestic-na-kanojo/154-5/",
    "#category": ("", "hiperdex", "chapter"),
    "#class"   : hiperdex.HiperdexChapterExtractor,
},

{
    "#url"     : "https://hiperdex.com/manga/1603231576-youre-not-that-special/",
    "#category": ("", "hiperdex", "manga"),
    "#class"   : hiperdex.HiperdexMangaExtractor,
    "#pattern" : hiperdex.HiperdexChapterExtractor.pattern,
    "#count"   : 51,

    "artist"       : "Bolp",
    "author"       : "Abyo4",
    "chapter"      : int,
    "chapter_minor": "",
    "description"  : r"re:I didn’t think much of the creepy girl in ",
    "genre"        : list,
    "manga"        : "You’re Not That Special!",
    "release"      : 2019,
    "score"        : float,
    "status"       : "Completed",
    "type"         : "Manhwa",
},

{
    "#url"     : "https://hiperdex.com/manga/youre-not-that-special/",
    "#category": ("", "hiperdex", "manga"),
    "#class"   : hiperdex.HiperdexMangaExtractor,
},

{
    "#url"     : "https://1sthiperdex.com/manga/youre-not-that-special/",
    "#category": ("", "hiperdex", "manga"),
    "#class"   : hiperdex.HiperdexMangaExtractor,
},

{
    "#url"     : "https://hiperdex2.com/manga/youre-not-that-special/",
    "#category": ("", "hiperdex", "manga"),
    "#class"   : hiperdex.HiperdexMangaExtractor,
},

{
    "#url"     : "https://hiperdex.net/manga/youre-not-that-special/",
    "#category": ("", "hiperdex", "manga"),
    "#class"   : hiperdex.HiperdexMangaExtractor,
},

{
    "#url"     : "https://hiperdex.info/manga/youre-not-that-special/",
    "#category": ("", "hiperdex", "manga"),
    "#class"   : hiperdex.HiperdexMangaExtractor,
},

{
    "#url"     : "https://1sthiperdex.com/manga-artist/beck-ho-an/",
    "#category": ("", "hiperdex", "artist"),
    "#class"   : hiperdex.HiperdexArtistExtractor,
},

{
    "#url"     : "https://hiperdex.net/manga-artist/beck-ho-an/",
    "#category": ("", "hiperdex", "artist"),
    "#class"   : hiperdex.HiperdexArtistExtractor,
},

{
    "#url"     : "https://hiperdex2.com/manga-artist/beck-ho-an/",
    "#category": ("", "hiperdex", "artist"),
    "#class"   : hiperdex.HiperdexArtistExtractor,
},

{
    "#url"     : "https://hiperdex.info/manga-artist/beck-ho-an/",
    "#category": ("", "hiperdex", "artist"),
    "#class"   : hiperdex.HiperdexArtistExtractor,
},

{
    "#url"     : "https://hiperdex.com/manga-author/viagra/",
    "#category": ("", "hiperdex", "artist"),
    "#class"   : hiperdex.HiperdexArtistExtractor,
    "#pattern" : hiperdex.HiperdexMangaExtractor.pattern,
    "#count"   : ">= 6",
},

)
