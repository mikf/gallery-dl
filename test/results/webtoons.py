# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import webtoons
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.webtoons.com/en/comedy/safely-endangered/ep-572-earth/viewer?title_no=352&episode_no=572",
    "#category": ("", "webtoons", "episode"),
    "#class"   : webtoons.WebtoonsEpisodeExtractor,
    "#count"   : 5,
    "#results" : (
        "https://swebtoon-phinf.pstatic.net/20200513_191/1589322488148XfdRr_PNG/15893224850013525720.png?type=opti",
        "https://swebtoon-phinf.pstatic.net/20200513_143/1589322489499KJLvU_PNG/15893224866183525723.png?type=opti",
        "https://swebtoon-phinf.pstatic.net/20200513_281/15893224881499wbH7_PNG/15893224865073525729.png?type=opti",
        "https://swebtoon-phinf.pstatic.net/20200513_155/1589322489501Kuczb_PNG/15893224866533525729.png?type=opti",
        "https://swebtoon-phinf.pstatic.net/20200513_122/1589322489499nS1t2_PNG/15893224863973525726.png?type=opti",
    ),
    "#sha1_url"    : "55bec5d7c42aba19e3d0d56db25fdf0b0b13be38",
    "#sha1_content": [
        "1748c7e82b6db910fa179f6dc7c4281b0f680fa7",
        "42055e44659f6ffc410b3fb6557346dfbb993df3",
        "49e1f2def04c6f7a6a3dacf245a1cd9abe77a6a9",
    ],

    "author_name" : "Chris McCoy",
    "comic"       : "safely-endangered",
    "comic_name"  : "Safely Endangered",
    "count"       : 5,
    "description" : "Silly comics for silly people.",
    "episode"     : "572",
    "episode_name": "Ep. 572 - Earth",
    "episode_no"  : "572",
    "genre"       : "comedy",
    "lang"        : "en",
    "language"    : "English",
    "num"         : range(1, 5),
    "title"       : "Safely Endangered - Ep. 572 - Earth",
    "title_no"    : "352",
    "username"    : "safelyendangered",
},

{
    "#url"     : "https://www.webtoons.com/en/comedy/safely-endangered/ep-572-earth/viewer?title_no=352&episode_no=572",
    "#comment" : "thumbnails (#6468 #7441)",
    "#class"   : webtoons.WebtoonsEpisodeExtractor,
    "#options" : {"thumbnails": True},
    "#range"   : "1",
    "#results" : "https://swebtoon-phinf.pstatic.net/20200513_37/1589322553469E5p76_PNG/thumb_15893224866533525729.png",
    "#sha1_content": "e01e70610821df6ece601393eb6fd7d80fc42f9a",

    "count": 5,
    "num"  : 0,
    "type" : "thumbnail",
},

{
    "#url"     : "https://www.webtoons.com/en/challenge/punderworld/happy-earth-day-/viewer?title_no=312584&episode_no=40",
    "#category": ("", "webtoons", "episode"),
    "#class"   : webtoons.WebtoonsEpisodeExtractor,
    "#exception": exception.NotFoundError,

    "comic"      : "punderworld",
    "description": str,
    "episode"    : "36",
    "episode_no" : "40",
    "genre"      : "challenge",
    "title"      : r"re:^Punderworld - .+",
    "title_no"   : "312584",
},

{
    "#url"     : "https://www.webtoons.com/en/canvas/i-want-to-be-a-cute-anime-girl/209-the-storys-story/viewer?title_no=349416&episode_no=214",
    "#category": ("", "webtoons", "episode"),
    "#class"   : webtoons.WebtoonsEpisodeExtractor,
    "#results" : (
        "https://swebtoon-phinf.pstatic.net/20220121_262/1642763563000TUsiC_JPEG/7ddc535a-0bde-40df-ab62-f912aed1c751.jpg",
        "https://swebtoon-phinf.pstatic.net/20220121_152/1642763564219c8T9I_JPEG/73ccdf9f-c46c-4760-8553-799713300fd7.jpg",
        "https://swebtoon-phinf.pstatic.net/20220121_80/16427635653964Eh5i_JPEG/1bd3c498-656b-4b1f-bf22-e25c01a01679.jpg",
        "https://swebtoon-phinf.pstatic.net/20220121_224/1642763566551Rx6e2_JPEG/6e61cddc-0af5-4e2a-b3b4-67fdd258feac.jpg",
    ),

    "comic_name"  : "I want to be a cute anime girl",
    "episode_name": "209 - The story's story",
    "episode"     : "214",
    "username"    : "m9huj",
    "author_name" : "Azul Crescent",
},

{
    "#url"     : "https://www.webtoons.com/en/canvas/i-want-to-be-a-cute-anime-girl/174-not-194-it-was-a-typo-later/viewer?title_no=349416&episode_no=179",
    "#category": ("", "webtoons", "episode"),
    "#class"   : webtoons.WebtoonsEpisodeExtractor,
    "#options" : {"quality": 50},
    "#results" : (
        "https://swebtoon-phinf.pstatic.net/20210629_102/1624911944660PIYD2_JPEG/27c5312d-7b9b-4b75-8026-526e9a55331a.jpg?type=q50",
        "https://swebtoon-phinf.pstatic.net/20210629_295/1624911951107dhQEw_JPEG/fc4bd86a-effc-4f0e-88d5-8c48d6ec3902.jpg?type=q50",
        "https://swebtoon-phinf.pstatic.net/20210629_293/16249119579830kbnl_JPEG/96203608-31e7-4f1c-a9e0-db5d43457884.jpg?type=q50",
        "https://swebtoon-phinf.pstatic.net/20210629_152/1624911964359nWSlj_JPEG/510e1c7e-2d13-4757-b215-8fbd1883e81e.jpg?type=q50",
    ),

    "comic_name"  : "I want to be a cute anime girl",
    "episode_name": "174 (not 194, it was a typo) - Later",
    "episode"     : "179",
    "username"    : "m9huj",
    "author_name" : "Azul Crescent",
},

{
    "#url"     : "https://www.webtoons.com/en/canvas/us-over-here/1-the-wheel/viewer?title_no=919536&episode_no=1",
    "#category": ("", "webtoons", "episode"),
    "#class"   : webtoons.WebtoonsEpisodeExtractor,
    "#options" : {"quality": {"jpg": "q0", "jpeg": "q100", "png": False}},
    "#results" : (
        "https://swebtoon-phinf.pstatic.net/20240125_32/17061125731244mMCw_JPEG/0001.JPEG?type=q100",
        "https://swebtoon-phinf.pstatic.net/20240125_290/1706112575827OXqUk_JPEG/0059.JPEG?type=q100",
        "https://swebtoon-phinf.pstatic.net/20240125_211/1706112575860p6rEU_JPEG/0060.JPEG?type=q100",
    ),

    "comic_name"  : "(news soon)",
    "episode_name": "1. The Wheel",
    "episode"     : "1",
    "username"    : "i94q8",
    "author_name" : "spin.ani",
},

{
    "#url"     : "https://www.webtoons.com/en/super-hero/unordinary/episode-20/viewer?title_no=679&episode_no=21",
    "#comment" : "background music (#8733)",
    "#class"   : webtoons.WebtoonsEpisodeExtractor,
    "#options" : {"bgm": True},
    "#range"   : "1",
    "#pattern" : r"ytdl:https://apis.naver.com/audioc/audiocplay/play/audio/4A10DDE1B92388DA164C48B0356AA442/hls/manifest\.m3u8\?apigw-routing-key=KR&codec=AAC&kbps=64&tt=\d+&tv=.+",

    "audioId"         : "4A10DDE1B92388DA164C48B0356AA442",
    "author_name"     : "uru-chan",
    "codec"           : "AAC",
    "comic"           : "unordinary",
    "comic_name"      : "unOrdinary",
    "count"           : 63,
    "cpContentId"     : None,
    "cpNo"            : 5,
    "description"     : "Nobody paid much attention to John – just a normal teenager at a high school where the social elite happen to possess unthinkable powers and abilities. But John’s got a secret past that threatens to bring down the school’s whole social order – and much more. Fulfilling his destiny won’t be easy though, because there are battles, frenemies and deadly conspiracies around every corner.",
    "duration"        : 90.096692,
    "encodingTargetYn": False,
    "episode"         : "21",
    "episodeNo"       : 21,
    "episode_name"    : "Episode 20",
    "episode_no"      : "21",
    "expireTime"      : int,
    "extension"       : "mp3",
    "filePath"        : "679_21/1475723621351drama7.mp3",
    "genre"           : "super-hero",
    "kbps"            : 64,
    "lang"            : "en",
    "language"        : "English",
    "num"             : 0,
    "num_play"        : 17,
    "num_stop"        : 0,
    "filename_play"   : "1475724249934679214",
    "filename_stop"   : "",
    "objectType"      : "mp4a.40.2",
    "originalFileSize": 0,
    "playImageUrl"    : "/20161006_271/1475724249957QlGUF_JPEG/1475724249934679214.jpg",
    "region"          : "KR",
    "registerYmdt"    : "2016-10-06 12:25:09",
    "sortOrder"       : 1,
    "stopImageUrl"    : "",
    "title"           : "unOrdinary - Episode 20",
    "titleNo"         : 679,
    "title_no"        : "679",
    "type"            : "bgm",
    "username"        : "62610",
},

{
    "#url"     : "https://www.webtoons.com/en/comedy/live-with-yourself/list?title_no=919",
    "#comment" : "english",
    "#category": ("", "webtoons", "comic"),
    "#class"   : webtoons.WebtoonsComicExtractor,
    "#pattern" : webtoons.WebtoonsEpisodeExtractor.pattern,
    "#range"   : "1-15",
    "#count"   : ">= 14",

    "page"      : range(1, 2),
    "title_no"  : 919,
    "episode_no": range(1, 14),
},

{
    "#url"     : "https://www.webtoons.com/en/comedy/live-with-yourself/list?title_no=919",
    "#comment" : "banner (#6468)",
    "#category": ("", "webtoons", "comic"),
    "#class"   : webtoons.WebtoonsComicExtractor,
    "#options" : {"banners": True},
    "#range"   : "1-3",
    "#results" : (
        "https://swebtoon-phinf.pstatic.net/20190126_226/1548461599138G7THv_PNG/03_EC9E91ED9288EC8381EC84B8_PC_ECBA90EBA6ADED84B0.png",
        "https://www.webtoons.com/en/comedy/live-with-yourself/ep-12-aint-gonna-face-no-defeat/viewer?title_no=919&episode_no=14",
        "https://www.webtoons.com/en/comedy/live-with-yourself/interlude-2/viewer?title_no=919&episode_no=13",
        "https://www.webtoons.com/en/comedy/live-with-yourself/ep-11-can-barely-stand-on-my-feet/viewer?title_no=919&episode_no=12",
    ),

    "?type"      : "banner",
    "title_no"   : 919,
    "?episode_no": range(12, 14),
},

{
    "#url"     : "https://www.webtoons.com/fr/romance/subzero/list?title_no=1845&page=7",
    "#comment" : "french",
    "#category": ("", "webtoons", "comic"),
    "#class"   : webtoons.WebtoonsComicExtractor,
    "#count"   : ">= 15",

    "page"      : range(7, 25),
    "title_no"  : 1845,
    "episode_no": int,
},

{
    "#url"     : "https://www.webtoons.com/en/challenge/scoob-and-shag/list?title_no=210827&page=9",
    "#comment" : "(#820)",
    "#category": ("", "webtoons", "comic"),
    "#class"   : webtoons.WebtoonsComicExtractor,
    "#count"   : ">= 18",

    "page"      : int,
    "title_no"  : 210827,
    "episode_no": int,
},

{
    "#url"     : "https://www.webtoons.com/es/romance/lore-olympus/list?title_no=1725",
    "#comment" : "(#1643)",
    "#category": ("", "webtoons", "comic"),
    "#class"   : webtoons.WebtoonsComicExtractor,
},

{
    "#url"     : "https://www.webtoons.com/p/community/en/u/g6vj8",
    "#class"   : webtoons.WebtoonsArtistExtractor,
    "#results" : (
        "https://www.webtoons.com/en/canvas/scoob-and-shag/list?title_no=210827",
        "https://www.webtoons.com/en/canvas/sparkle-kid/list?title_no=205304",
    ),

    "id"     : {"210827", "205304"},
    "subject": {"Scoob and Shag", "Sparkle Kid"},
    "authors": [
        {
            "nickname": "Misterie Krew",
        },
    ],

},

)
