# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import tcbscans
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://tcbscans.me/chapters/4708/chainsaw-man-chapter-108",
    "#category": ("", "tcbscans", "chapter"),
    "#class"   : tcbscans.TcbscansChapterExtractor,
    "#pattern" : r"https://cdn\.[^/]+/(file|attachments/[^/]+)/[^/]+/[^.]+\.\w+",
    "#count"   : 17,

    "manga"        : "Chainsaw Man",
    "chapter"      : 108,
    "chapter_minor": "",
    "lang"         : "en",
    "language"     : "English",
},

{
    "#url"     : "https://onepiecechapters.com/chapters/4716/one-piece-chapter-1065",
    "#category": ("", "tcbscans", "chapter"),
    "#class"   : tcbscans.TcbscansChapterExtractor,
    "#pattern" : r"https://cdn\.[^/]+/(file|attachments/[^/]+)/[^/]+/[^.]+\.\w+",
    "#count"   : 18,

    "manga"        : "One Piece",
    "chapter"      : 1065,
    "chapter_minor": "",
    "lang"         : "en",
    "language"     : "English",
    "#exception"   : exception.HttpError,
},

{
    "#url"     : "https://onepiecechapters.com/chapters/44/ace-novel-manga-adaptation-chapter-1",
    "#category": ("", "tcbscans", "chapter"),
    "#class"   : tcbscans.TcbscansChapterExtractor,
    "#exception": exception.HttpError,
},

{
    "#url"     : "https://tcbscans.me/chapters/7719/jujutsu-kaisen-chapter-258",
    "#category": ("", "tcbscans", "chapter"),
    "#class"   : tcbscans.TcbscansChapterExtractor,
    "#pattern" : r"https://cdn\.[^/]+/(file|attachments/[^/]+)/[^/]+/[^.]+\.\w+",
    "#count"   : 15,

    "manga"        : "Jujutsu Kaisen",
    "chapter"      : 258,
    "chapter_minor": "",
    "lang"         : "en",
    "language"     : "English",
},

{
    "#url"     : "https://tcbscans.me/mangas/13/chainsaw-man",
    "#category": ("", "tcbscans", "manga"),
    "#class"   : tcbscans.TcbscansMangaExtractor,
    "#pattern" : tcbscans.TcbscansChapterExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://onepiecechapters.com/mangas/4/jujutsu-kaisen",
    "#category": ("", "tcbscans", "manga"),
    "#class"   : tcbscans.TcbscansMangaExtractor,
    "#pattern" : tcbscans.TcbscansChapterExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
    "#exception": exception.HttpError,
},

{
    "#url"     : "https://onepiecechapters.com/mangas/15/hunter-x-hunter",
    "#category": ("", "tcbscans", "manga"),
    "#class"   : tcbscans.TcbscansMangaExtractor,
    "#exception": exception.HttpError,
},

{
    "#url"     : "https://tcbscans.com/mangas/4/jujutsu-kaisen",
    "#class"   : tcbscans.TcbscansMangaExtractor,
},

{
    "#url"     : "https://tcb-backup.bihar-mirchi.com/chapters/7719/jujutsu-kaisen-chapter-258",
    "#class"   : tcbscans.TcbscansChapterExtractor,
},

)
