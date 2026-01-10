# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import bellazon


__tests__ = (
{
    "#url"     : "https://www.bellazon.com/main/topic/57872-millie-brady/#findComment-4351049",
    "#class"   : bellazon.BellazonPostExtractor,
    "#results" : (
        "https://www.bellazon.com/main/uploads/monthly_2017_06/595482b77fd89_millieb280617BZNImage101.jpg.10b91b9141b374e657a1a4c3d0c96b64.jpg",
        "https://www.bellazon.com/main/uploads/monthly_2017_06/595482c3f2fa0_millieb280617BZNImage102.jpg.1b706048fc525151775cf4b7c734b283.jpg",
        "https://www.bellazon.com/main/uploads/monthly_2017_06/595482cdc66ad_millieb280617BZNImage103.jpg.6fa2226a314d0f0e9f9426e7f90f4808.jpg",
        "https://www.bellazon.com/main/uploads/monthly_2017_06/595482dac786c_millieb280617BZNImage104.jpg.e579be6b585cef90b965d4d09969a66a.jpg",
        "https://www.bellazon.com/main/uploads/monthly_2017_06/595482e772acd_millieb280617BZNImage105.jpg.428df8a841957b48452a6a6ab64ddacb.jpg",
    ),

    "id"       : r"re:55\d+",
    "filename" : str,
    "extension": "jpg",
    "count"    : 5,
    "num"         : range(1, 5),
    "num_internal": range(1, 5),
    "num_external": 0,
    "post"     : {
        "author_id"  : "72476",
        "author_slug": "shepherd",
        "author_url" : "https://www.bellazon.com/main/profile/72476-shepherd/",
        "count"      : 5,
        "date"       : "dt:2017-06-29 04:32:43",
        "id"         : "4351049",
        "content"    : """\
<p>
\tSerpentine Galleries Summer Party, London, Jun 28 '17
</p>

<p>
\t 
</p>

<p>
\t<a class="ipsAttachLink ipsAttachLink_image" href="https://www.bellazon.com/main/uploads/monthly_2017_06/595482b77fd89_millieb280617BZNImage101.jpg.10b91b9141b374e657a1a4c3d0c96b64.jpg" data-fileid="5550073" rel=""><img alt="millieb280617BZNImage101.jpg" class="ipsImage ipsImage_thumbnailed" data-fileid="5550073" src="https://www.bellazon.com/main/uploads/monthly_2017_06/595482b7c4730_millieb280617BZNImage101.thumb.jpg.5b5240deead09ec5546a6bbf68aff724.jpg" data-ratio="66.56" loading="lazy"></a> <a class="ipsAttachLink ipsAttachLink_image" href="https://www.bellazon.com/main/uploads/monthly_2017_06/595482c3f2fa0_millieb280617BZNImage102.jpg.1b706048fc525151775cf4b7c734b283.jpg" data-fileid="5550074" rel=""><img alt="millieb280617BZNImage102.jpg" class="ipsImage ipsImage_thumbnailed" data-fileid="5550074" src="https://www.bellazon.com/main/uploads/monthly_2017_06/595482c4529af_millieb280617BZNImage102.thumb.jpg.1b9f9ec5f002eaaaa80a174d1a7853d0.jpg" data-ratio="150" loading="lazy"></a> <a class="ipsAttachLink ipsAttachLink_image" href="https://www.bellazon.com/main/uploads/monthly_2017_06/595482cdc66ad_millieb280617BZNImage103.jpg.6fa2226a314d0f0e9f9426e7f90f4808.jpg" data-fileid="5550075" rel=""><img alt="millieb280617BZNImage103.jpg" class="ipsImage ipsImage_thumbnailed" data-fileid="5550075" src="https://www.bellazon.com/main/uploads/monthly_2017_06/595482ce268f7_millieb280617BZNImage103.thumb.jpg.580d38335424d6fa65bd5d476625864b.jpg" data-ratio="150.23" loading="lazy"></a>
</p>

<p>
\t<a class="ipsAttachLink ipsAttachLink_image" href="https://www.bellazon.com/main/uploads/monthly_2017_06/595482dac786c_millieb280617BZNImage104.jpg.e579be6b585cef90b965d4d09969a66a.jpg" data-fileid="5550076" rel=""><img alt="millieb280617BZNImage104.jpg" class="ipsImage ipsImage_thumbnailed" data-fileid="5550076" src="https://www.bellazon.com/main/uploads/monthly_2017_06/595482db10e03_millieb280617BZNImage104.thumb.jpg.958eba72b585110a4b8c08f1efd9cfc8.jpg" title="" data-ratio="150.26" loading="lazy"></a> <a class="ipsAttachLink ipsAttachLink_image" href="https://www.bellazon.com/main/uploads/monthly_2017_06/595482e772acd_millieb280617BZNImage105.jpg.428df8a841957b48452a6a6ab64ddacb.jpg" data-fileid="5550077" rel=""><img alt="millieb280617BZNImage105.jpg" class="ipsImage ipsImage_thumbnailed" data-fileid="5550077" src="https://www.bellazon.com/main/uploads/monthly_2017_06/595482e7e6bc1_millieb280617BZNImage105.thumb.jpg.1e5ce2b85f7ceed7446d7f13caa9ce2b.jpg" data-ratio="150.22" loading="lazy"></a>
</p>\
""",
    },
    "thread"   : {
        "author"      : "Shepherd",
        "author_id"   : "72476",
        "author_slug" : "shepherd",
        "author_url"  : "https://www.bellazon.com/main/profile/72476-shepherd/",
        "date"        : "dt:2015-06-20 21:34:31",
        "date_updated": "dt:2017-06-29 04:32:43",
        "description" : "Previously featured in the popular TV series, Mr Selfridge, emerging British born actress Millie Brady is set for huge success. \nMillie has just been confirmed as the lead role in ‘The Clan of the Cave Bear’ which will begin filming in May 2015. The drama pilot is from Imagine TV, Allison Shearmur Productions, Fox 21 TV and Lionsgate TV. Millie is also due to appear in the eagerly awaited black comedy, 'Pride and Prejudice and Zombies', staring alongside Matt Smith, Sally Philiips, Douglas Booth, Lily james and Sam Riley. She is currently filming 'Knights of the Roundtable: King Arthur' directed by Guy Ritchie. \n  \n  \nFarfetch, Jun 2015 \nLinda Brownlee photos",
        "id"          : "57872",
        "posts"       : 1,
        "section"     : "Actresses",
        "slug"        : "millie-brady",
        "title"       : "Millie Brady",
        "url"         : "https://www.bellazon.com/main/topic/57872-millie-brady/",
        "views"       : range(3_800, 5_000),
        "path"        : [
            "Females",
            "Actresses",
            "Millie Brady",
        ],
    },
},

{
    "#url"     : "https://www.bellazon.com/main/topic/57872-millie-brady/#comment-4351049",
    "#class"   : bellazon.BellazonPostExtractor,
},

{
    "#url"     : "https://www.bellazon.com/main/topic/3556-bipasha-basu/#findComment-2134610",
    "#class"   : bellazon.BellazonPostExtractor,
    "#results" : "https://www.bellazon.com/main/uploads/monthly_04_2010/post-35864-1270985307.jpg",

    "id"       : "1002749",
    "filename" : "post-35864-1270985307",
    "extension": "jpg",
    "count"    : 1,
    "num"      : 1,
    "post"     : {
        "author_id"  : "35864",
        "author_slug": "egluze",
        "author_url" : "https://www.bellazon.com/main/profile/35864-egluze/",
        "count"      : 1,
        "date"       : "dt:2010-04-11 11:28:43",
        "id"         : "2134610",
        "content"    : """\
<p><strong>Marie Claire India April 2010</strong></p>
<p><a class="ipsAttachLink ipsAttachLink_image" href="https://www.bellazon.com/main/uploads/monthly_04_2010/post-35864-1270985307.jpg" rel="external nofollow"><img class="ipsImage ipsImage_thumbnailed" src="https://www.bellazon.com/main/uploads/monthly_04_2010/post-35864-1270985307_thumb.jpg" data-fileid="1002749" alt="post-35864-1270985307_thumb.jpg" data-ratio="133.67" loading="lazy"></a></p>\
""",
    },
    "thread"   : {
        "author"      : "SaBrIaNa",
        "author_id"   : "1324",
        "author_slug" : "sabriana",
        "author_url"  : "https://www.bellazon.com/main/profile/1324-sabriana/",
        "date"        : "dt:2005-12-26 20:31:33",
        "date_updated": "dt:2017-06-17 05:19:09",
        "description" : str,
        "id"          : "3556",
        "posts"       : 44,
        "section"     : "Actresses",
        "slug"        : "bipasha-basu",
        "title"       : "Bipasha Basu",
        "url"         : "https://www.bellazon.com/main/topic/3556-bipasha-basu/",
        "views"       : range(20_000, 50_000),
        "path"        : [
            "Females",
            "Actresses",
            "Bipasha Basu",
        ],
    },
},

{
    "#url"     : "https://www.bellazon.com/main/topic/66334-charly-jordan/page/3/#findComment-4576614",
    "#comment" : "video attachments (#8239)",
    "#class"   : bellazon.BellazonPostExtractor,
    "#pattern" : r"https://www\.bellazon\.com/main/applications/core/interface/file/attachment\.php\?id=\d+$",
    "#range"   : "2-",
    "#count"   : 10,

    "count"    : 12,
    "extension": "mp4",
    "filename" : r"re:^\d+$",
    "id"       : r"re:6361\d\d\d",
    "num"      : range(2, 12),
    "post"     : {
        "author_id"  : "101807",
        "author_slug": "rogerdanish",
        "author_url" : "https://www.bellazon.com/main/profile/101807-rogerdanish/",
        "count"      : 12,
        "date"       : "dt:2018-04-06 19:06:06",
        "id"         : "4576614",
        "content"    : str
    },
    "thread"   : {
        "author"      : "gtemt",
        "author_id"   : "29506",
        "author_slug" : "gtemt",
        "author_url"  : "https://www.bellazon.com/main/profile/29506-gtemt/",
        "date"        : "dt:2017-12-19 12:18:46",
        "date_updated": "type:datetime",
        "description" : "VID",
        "id"          : "66334",
        "posts"       : range(750, 999),
        "section"     : "Other Females of Interest",
        "slug"        : "charly-jordan",
        "title"       : "Charly Jordan",
        "url"         : "https://www.bellazon.com/main/topic/66334-charly-jordan/",
        "views"       : int,
        "path"        : [
            "Females",
            "Other Females of Interest",
            "Charly Jordan",
        ],
    },
},

{
    "#url"     : "https://www.bellazon.com/main/topic/66334-charly-jordan/page/3/#findComment-4571129",
    "#comment" : "video attachment with '//www.bellazon.com/main/' as URL (#8239)",
    "#class"   : bellazon.BellazonPostExtractor,
    "#results" : (
        "https://www.bellazon.com/main/uploads/monthly_2018_03/charlyjordan10_Bg6mLKlFBuU.jpg.07b89fe216300157ff5dad0652df11cb.jpg",
        "https://www.bellazon.com/main/uploads/monthly_2018_03/charlyjordan10_Bg6mLRzlFPz.jpg.3c846bc3d7a2ec4854012ca3bab0af99.jpg",
        "https://www.bellazon.com/main/uploads/monthly_2018_03/charlyjordan10_Bg6mLVYlQUL.jpg.7e32ef45d5ba5270a330b250f83639dd.jpg",
        "https://www.bellazon.com/main/applications/core/interface/file/attachment.php?id=6341394",
    ),
},

{
    "#url"     : "https://www.bellazon.com/main/topic/66334-charly-jordan/page/31/#comment-5317926",
    "#comment" : "video embed (#8239)",
    "#class"   : bellazon.BellazonPostExtractor,
    "#results" : "https://www.bellazon.com/main/uploads/monthly_2021_07/215731864_146910617534875_8340126104113274819_n.mp4.2f3cd5cd8cac6bf04c51d511892f187b.mp4",

    "extension": "mp4",
    "filename" : "215731864_146910617534875_8340126104113274819_n.mp4.2f3cd5cd8cac6bf04c51d511892f187b",
    "id"       : "10919171",
},

{
    "#url"     : "https://www.bellazon.com/main/topic/66334-charly-jordan/page/3/#findComment-4602714",
    "#comment" : "'/profile/' link",
    "#class"   : bellazon.BellazonPostExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://www.bellazon.com/main/topic/66334-charly-jordan/page/3/#findComment-4603172",
    "#comment" : "'inline' image",
    "#class"   : bellazon.BellazonPostExtractor,
    "#results" : "https://www.bellazon.com/main/uploads/monthly_2018_04/30602369_1891291154222843_1650952189830496256_n.jpg.33e6ab78dd0e8723f790ad4f58f3761a.jpg",
},

{
    "#url"     : "https://www.bellazon.com/main/topic/70367-elyzaveta-kovalenko/page/5/#comment-5464973",
    "#comment" : "(#8392)",
    "#class"   : bellazon.BellazonPostExtractor,
    "#results" : (
        "https://www.bellazon.com/main/uploads/monthly_2022_05/917305269_LizaKovalenko-Instagram2021_04_19.mp4.467d190a54e1bcabc50767a69706501d.mp4",
        "https://www.bellazon.com/main/uploads/monthly_2022_05/2027180206_LizaKovalenko-Instagram2021_04_23.mp4.2eae87d7e9d6f1a993611fa1f73e8e7b.mp4",
    ),
},

{
    "#url"     : "https://www.bellazon.com/main/topic/70367-elyzaveta-kovalenko/page/7/#comment-5506079",
    "#comment" : "links to other threads (#8392)",
    "#class"   : bellazon.BellazonPostExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://www.bellazon.com/main/topic/4322-candids/page/1852/#comment-5902385",
    "#comment" : "attachment 'id' with query parameters (#8544)",
    "#class"   : bellazon.BellazonPostExtractor,
    "#range"   : "4",
    "#results" : "https://www.bellazon.com/main/applications/core/interface/file/attachment.php?id=14418097&key=491d27ee2482b1808483f1d544873b06",

    "count"       : 4,
    "num"         : 4,
    "filename"    : "download",
    "extension"   : "jfif",
    "id"          : "14418097",
},

{
    "#url"     : "https://www.bellazon.com/main/topic/4322-candids/page/1066/#comment-3956772",
    "#comment" : "weird/wrong 'filename' & 'extension' (#8544)",
    "#class"   : bellazon.BellazonPostExtractor,
    "#count"   : 16,

    "extension"   : "jpg",
    "filename"    : r"re:^[^.]+$",
    "id"          : r"re:^\d+$",
},

{
    "#url"     : "https://www.bellazon.com/main/topic/79152-sydney-sweeney/page/42/#comment-6113627",
    "#comment" : "'data-full-image' URLs (#8833)",
    "#class"   : bellazon.BellazonPostExtractor,
    "#results" : (
        "https://www.wmagazine.com/culture/sydney-sweeney-cover-interview-the-housemaid-christy",
        "https://www.bellazon.com/main/uploads/monthly_2026_01/1222250126covershrinstagram2.jpg.9bca664c750694127c5c77c0e99db770.jpg",
        "https://www.bellazon.com/main/uploads/monthly_2026_01/1222250126covershrcms2.jpg.a4d33f2e157aec446f9e268cce576ddc.jpg",
        "https://www.bellazon.com/main/uploads/monthly_2026_01/1-0126broadsheetcmslo13-14.jpg.21f087b58d0d3cc5c7d03ea2bb62a979.jpg",
    ),

    "post"        : {
        "author_id"  : "145049",
        "author_slug": "matt",
        "author_url" : "https://www.bellazon.com/main/profile/145049-matt/",
        "content"    : """<p style="text-align:center;">W Magazine's 2026 Best Performances issue</p><p style="text-align:center;">Sydney Sweeney Talks The Housemaid, Christy, and Bonding With Amanda Seyfried</p><p style="text-align:center;">Ph. Tyrone Lebon</p><p style="text-align:center;"><a rel="external nofollow" href="https://www.wmagazine.com/culture/sydney-sweeney-cover-interview-the-housemaid-christy">https://www.wmagazine.com/culture/sydney-sweeney-cover-interview-the-housemaid-christy</a></p><p style="text-align:center;"></p><p style="text-align:center;"><img class="ipsImage ipsImage_thumbnailed ipsRichText__align--block" data-fileid="15813191" src="https://www.bellazon.com/main/uploads/monthly_2026_01/1222250126covershrinstagram2.thumb.jpg.7bfbdc57ebcbfd61e4ba72c2b55dfbf3.jpg" alt="1222250126covershrinstagram2.jpg" title="" width="230" height="300" data-full-image="https://www.bellazon.com/main/uploads/monthly_2026_01/1222250126covershrinstagram2.jpg.9bca664c750694127c5c77c0e99db770.jpg" loading="lazy"><img class="ipsImage ipsImage_thumbnailed ipsRichText__align--block" data-fileid="15813196" src="https://www.bellazon.com/main/uploads/monthly_2026_01/1222250126covershrcms2.thumb.jpg.4ae359d3f0927aca1f7ab6a4d44b47cf.jpg" alt="1222250126covershrcms2.jpg" title="" width="231" height="300" data-full-image="https://www.bellazon.com/main/uploads/monthly_2026_01/1222250126covershrcms2.jpg.a4d33f2e157aec446f9e268cce576ddc.jpg" loading="lazy"><img class="ipsImage ipsImage_thumbnailed ipsRichText__align--block" data-fileid="15813194" src="https://www.bellazon.com/main/uploads/monthly_2026_01/1-0126broadsheetcmslo13-14.thumb.jpg.904162a4ebd4a340d5a595df82e7c982.jpg" alt="1-0126broadsheetcmslo13-14.jpg" title="" width="300" height="194" data-full-image="https://www.bellazon.com/main/uploads/monthly_2026_01/1-0126broadsheetcmslo13-14.jpg.21f087b58d0d3cc5c7d03ea2bb62a979.jpg" loading="lazy"></p>""",
        "count"      : 4,
        "date"       : "dt:2026-01-06 16:34:53",
        "id"         : "6113627",
    },
},

{
    "#url"     : "https://www.bellazon.com/main/topic/123434-%D0%BD%D0%B0-%D1%84%D0%BE%D1%82%D0%BE-%D0%B2%D0%B8%D0%BA%D1%82%D0%BE%D1%80%D0%B8%D1%8F-%D0%BA%D0%BE%D0%BB%D0%B5%D1%81%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2%D0%B0/#comment-6112956",
    "#comment" : "URL-escaped 'slug'",
    "#class"   : bellazon.BellazonPostExtractor,
    "#results" : "https://www.bellazon.com/main/uploads/monthly_2026_01/IMG_3177.png.b057c59b2168b2ff52d45cf6b1eba86e.png",

    "extension"   : "png",
    "filename"    : "IMG_3177",
    "id"          : "15808003",
    "post"        : {
        "author_id"  : "328354",
        "author_slug": "ghhhv",
        "author_url" : "https://www.bellazon.com/main/profile/328354-ghhhv/",
        "content"    : """<a href="https://www.bellazon.com/main/uploads/monthly_2026_01/IMG_3177.png.b057c59b2168b2ff52d45cf6b1eba86e.png" class="ipsAttachLink ipsAttachLink_image" ><img data-fileid="15808003" src="https://www.bellazon.com/main/uploads/monthly_2026_01/IMG_3177.thumb.png.a48d590d47aa78f5da7e7dddeb6c284d.png" height="300" width="172" class="ipsImage ipsImage_thumbnailed" alt="IMG_3177.png" loading='lazy'></a>""",
        "count"      : 1,
        "date"       : "dt:2026-01-04 22:14:17",
        "id"         : "6112956",
    },
    "thread"      : {
        "author"      : "Ghhhv",
        "author_id"   : "328354",
        "author_slug" : "ghhhv",
        "author_url"  : "https://www.bellazon.com/main/profile/328354-ghhhv/",
        "date"        : "dt:2026-01-04 22:14:17",
        "date_updated": "dt:2026-01-04 22:14:17",
        "id"          : "123434",
        "section"     : "Actresses",
        "slug"        : "на-фото-виктория-колесникова",
        "title"       : "на фото Виктория Колесникова",
        "url"         : "https://www.bellazon.com/main/topic/123434-%D0%BD%D0%B0-%D1%84%D0%BE%D1%82%D0%BE-%D0%B2%D0%B8%D0%BA%D1%82%D0%BE%D1%80%D0%B8%D1%8F-%D0%BA%D0%BE%D0%BB%D0%B5%D1%81%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2%D0%B0/",
        "path"        : [
            "Females",
            "Actresses",
            "на фото Виктория Колесникова",
        ],
    },
},

{
    "#url"     : "https://www.bellazon.com/main/topic/57872-millie-brady/",
    "#class"   : bellazon.BellazonThreadExtractor,
    "#pattern" : r"https://www\.bellazon\.com/main/uploads/monthly_\d+_\d+/.+\.jpg",
    "#count"   : 13,

    "id"       : r"re:\d+",
    "filename" : str,
    "extension": "jpg",
    "count"    : {5, 8},
    "num"      : range(1, 8),
    "post"     : {
        "id"       : {"3721257", "4351049"},
        "count"    : {5, 8},
        "author_id": "72476",
        "date"     : "type:datetime",
    },
    "thread"   : {
        "id"       : "57872",
        "title"    : "Millie Brady",
        "author"   : "Shepherd",
        "author_id": "72476",
        "date"     : "dt:2015-06-20 21:34:31",
    },
},

{
    "#url"     : "https://www.bellazon.com/main/topic/3556-bipasha-basu/",
    "#class"   : bellazon.BellazonThreadExtractor,
    "#pattern" : r"https?://(www\.bellazon\.com/main/uploads/.+\.\w+|www\.[^.]+\.(com|ru)|img\d+.imagevenue.com|imagesion.com)",
    "#count"   : 247,

    "count"    : range(0, 30),
    "num"      : range(0, 30),
    "post"     : {
        "id"       : r"re:\d+",
        "author_id": r"re:\d+",
        "count"    : range(0, 30),
        "date"     : "type:datetime",
    },
    "thread"   : {
        "id"          : "3556",
        "title"       : "Bipasha Basu",
        "author"      : "SaBrIaNa",
        "author_id"   : "1324",
        "date"        : "dt:2005-12-26 20:31:33",
        "date_updated": "dt:2017-06-17 05:19:09",
    },
},

{
    "#url"     : "https://www.bellazon.com/main/topic/1774-zhang-ziyi/",
    "#class"   : bellazon.BellazonThreadExtractor,
    "#range"   : "1-5",
    "#options" : {"order-posts": "asc"},
    "#results" : (
        "http://img292.echo.cx/my.php?image=4moon011rk.jpg",
        "http://img294.echo.cx/my.php?image=heroclip3jb.jpg",
        "http://img294.echo.cx/my.php?image=heroclip29ut.jpg",
        "http://img294.echo.cx/my.php?image=heroclip35lp.jpg",
        "http://img36.echo.cx/my.php?image=895welzz4514nv.jpg",
    ),

    "thread": {
        "author"      : "Hiro",
        "author_id"   : "26",
        "author_slug" : "hiro",
        "author_url"  : "https://www.bellazon.com/main/profile/26-hiro/",
        "date"        : "dt:2005-06-08 03:02:03",
        "date_updated": "dt:2023-07-09 07:33:19",
        "description" : str,
        "id"          : "1774",
        "posts"       : 480,
        "section"     : "Actresses",
        "slug"        : "zhang-ziyi",
        "title"       : "Zhang Ziyi",
        "url"         : "https://www.bellazon.com/main/topic/1774-zhang-ziyi/",
        "views"       : int,
        "path"        : [
            "Females",
            "Actresses",
            "Zhang Ziyi",
        ],
    },
},

{
    "#url"     : "https://www.bellazon.com/main/topic/56-candids/",
    "#comment" : "'Guest' author (#8397)",
    "#class"   : bellazon.BellazonThreadExtractor,
    "#options" : {"order-posts": "asc"},
    "#range"   : "1",
    "#results" : (
        "https://www.bellazon.com/main/uploads/monthly_11_2004/post-0-0-1593851439-26962.jpg",
    ),

    "post"     : {
        "author_id"  : "",
        "author_slug": "",
        "author_url" : "",
        "content"    : """<a href="https://www.bellazon.com/main/uploads/monthly_11_2004/post-0-0-1593851439-26962.jpg" class="ipsAttachLink ipsAttachLink_image"><img data-fileid="292" src="https://www.bellazon.com/main/uploads/monthly_11_2004/post-0-0-1593851439-26962_thumb.jpg" class="ipsImage ipsImage_thumbnailed" alt="sss.jpg" loading="lazy"></a>""",
        "count"      : 1,
        "date"       : "dt:2004-11-21 03:09:51",
        "id"         : "292",
    },
    "thread"   : {
        "author"      : "Guest",
        "author_id"   : "",
        "author_slug" : "",
        "author_url"  : "",
        "date"        : "dt:2004-11-21 01:44:59",
        "date_updated": "type:datetime",
        "description" : "Welcome to the Alessandra Ambrosio Candids gallery.  Please only post candid, unposed, off-guard, or funny images in this thread.",
        "id"          : "56",
        "posts"       : range(13_000, 30_000),
        "section"     : "Alessandra Ambrosio",
        "slug"        : "candids",
        "title"       : "Candids",
        "url"         : "https://www.bellazon.com/main/topic/56-candids/",
        "views"       : range(8_000_000, 10_000_000),
        "path"        : [
            "Females",
            "Female Fashion Models",
            "Alessandra Ambrosio",
            "Candids",
        ],
    },
},

{
    "#url"     : "https://www.bellazon.com/main/topic/123434-%D0%BD%D0%B0-%D1%84%D0%BE%D1%82%D0%BE-%D0%B2%D0%B8%D0%BA%D1%82%D0%BE%D1%80%D0%B8%D1%8F-%D0%BA%D0%BE%D0%BB%D0%B5%D1%81%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2%D0%B0/",
    "#class"   : bellazon.BellazonThreadExtractor,
},

{
    "#url"     : "https://www.bellazon.com/main/forum/3-actresses/",
    "#class"   : bellazon.BellazonForumExtractor,
    "#pattern" : bellazon.BellazonThreadExtractor.pattern,
    "#range"   : "1-100",
    "#count"   : 100,
},

)
