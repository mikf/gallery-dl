# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mangafreak


__tests__ = (
{
    "#url"     : "https://ww2.mangafreak.me/Read1_Onepunch_Man_1",
    "#class"   : mangafreak.MangafreakChapterExtractor,
    "#pattern" : r"https://images\.mangafreak\.me/mangas/onepunch_man/onepunch_man_1/onepunch_man_1_\d+\.jpg",
    "#count"   : 24,

    "chapter"      : 1,
    "chapter_minor": "",
    "chapter_string": "1",
    "lang"         : "en",
    "language"     : "English",
    "manga"        : "Onepunch Man",
    "manga_slug"   : "Onepunch_Man",
},

{
    "#url"     : "https://ww2.mangafreak.me/Read1_Onepunch_Man_167e",
    "#class"   : mangafreak.MangafreakChapterExtractor,

    "chapter"      : 167,
    "chapter_minor": "e",
    "chapter_string": "167e",
},

{
    "#url"     : "https://ww2.mangafreak.me/Read1_Sss_Rank_Dungeon_De_Knife_Ippon_Tewatasare_Tsuihou_Sareta_Shiro_Madoushi_Yggdrasil_No_Noroi_Ni_Yori_Jakuten_De_Aru_Maryoku_Fusoku_Wo_Kokufuku_Shi_Sekai_Saikyou_E_To_Itaru_23c",
    "#class"   : mangafreak.MangafreakChapterExtractor,
    "#pattern" : r"https://images\.mangafreak\.me/mangas/sss_rank_dungeon_de_knife_ippon_tewatasare_tsuihou_sareta_shiro_madoushi_yggdrasil_no_noroi_ni_yori_jakuten_de_aru_maryoku_fusoku_wo_kokufuku_shi_sekai_saikyou_e_to_itaru/sss_rank_dungeon_de_knife_ippon_tewatasare_tsuihou_sareta_shiro_madoushi_yggdrasil_no_noroi_ni_yori_jakuten_de_aru_maryoku_fusoku_wo_kokufuku_shi_sekai_saikyou_e_to_itaru_23c/sss_rank_dungeon_de_knife_ippon_tewatasare_tsuihou_sareta_shiro_madoushi_yggdrasil_no_noroi_ni_yori_jakuten_de_aru_maryoku_fusoku_wo_kokufuku_shi_sekai_saikyou_e_to_itaru_23c_\d+\.jpg",
    "#count"   : 11,

    "chapter"       : 23,
    "chapter_minor" : "c",
    "chapter_string": "23c",
    "count"         : 11,
    "page"          : range(1, 11),
    "filename"      : str,
    "extension"     : "jpg",
    "lang"          : "en",
    "language"      : "English",
    "manga"         : "Sss Rank Dungeon De Knife Ippon Tewatasare Tsuihou Sareta Shiro Madoushi Yggdrasil No Noroi Ni Yori Jakuten De Aru Maryoku Fusoku Wo Kokufuku Shi Sekai Saikyou E To Itaru",
    "manga_slug"    : "Sss_Rank_Dungeon_De_Knife_Ippon_Tewatasare_Tsuihou_Sareta_Shiro_Madoushi_Yggdrasil_No_Noroi_Ni_Yori_Jakuten_De_Aru_Maryoku_Fusoku_Wo_Kokufuku_Shi_Sekai_Saikyou_E_To_Itaru",
    "title"         : "",
},

{
    "#url"     : "https://ww2.mangafreak.me/Read1_Tensei_Shitara_Slime_Datta_Ken_62",
    "#class"   : mangafreak.MangafreakChapterExtractor,
    "#count"   : 19,

    "chapter"  : 62,
    "count"    : 19,
    "manga"    : "Tensei Shitara Slime Datta Ken",
    "title"    : "To be a Monster or Human",
},

{
    "#url"     : "https://ww2.mangafreak.me/Manga/Onepunch_Man",
    "#class"   : mangafreak.MangafreakMangaExtractor,
    "#pattern" : mangafreak.MangafreakChapterExtractor.pattern,
    "#count"   : range(150, 250),

    "lang"       : "en",
    "language"   : "English",
    "manga"      : "Onepunch-Man",
    "manga_slug" : "Onepunch_Man",
    "chapter"    : int,
},

{
    "#url"     : "https://ww2.mangafreak.me/Manga/Sss_Rank_Dungeon_De_Knife_Ippon_Tewatasare_Tsuihou_Sareta_Shiro_Madoushi_Yggdrasil_No_Noroi_Ni_Yori_Jakuten_De_Aru_Maryoku_Fusoku_Wo_Kokufuku_Shi_Sekai_Saikyou_E_To_Itaru",
    "#class"   : mangafreak.MangafreakMangaExtractor,
    "#pattern" : mangafreak.MangafreakChapterExtractor.pattern,
    "#count"   : range(40, 80),

    "chapter"       : int,
    "chapter_minor" : {"", "a", "b", "c"},
    "chapter_string": str,
    "lang"          : "en",
    "language"      : "English",
    "manga"         : "SSS Rank Dungeon de Knife Ippon Tewatasare Tsuihou Sareta Shiro Madoushi: Yggdrasil no Noroi ni yori Jakuten de aru Maryoku Fusoku wo Kokufuku-shi Sekai Saikyou e to Itaru",
    "manga_slug"    : "Sss_Rank_Dungeon_De_Knife_Ippon_Tewatasare_Tsuihou_Sareta_Shiro_Madoushi_Yggdrasil_No_Noroi_Ni_Yori_Jakuten_De_Aru_Maryoku_Fusoku_Wo_Kokufuku_Shi_Sekai_Saikyou_E_To_Itaru",
    "title"         : str,
},

)
