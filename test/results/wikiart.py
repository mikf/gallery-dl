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
    "#pattern" : r"https://uploads\d+\.wikiart\.org/(\d+/)?images/thomas-cole/[\w()-]+\.(jpg|png)",
    "#count"   : "> 100",

    "albums"     : None,
    "artist"     : {
        "OriginalArtistName": "Thomas Cole",
        "activeYearsCompletion": None,
        "activeYearsStart"  : None,
        "artistName"        : "Thomas Cole",
        "biography"         : "Thomas Cole inspired the generation of American [url href=https://www.wikiart.org/en/paintings-by-genre/landscape]landscape[/url] painters that came to be known as the [url href=https://www.wikiart.org/en/artists-by-painting-school/hudson-river-school]Hudson River School[/url]. Born in Bolton-le-Moors, Lancashire, England, in 1801, at the age of seventeen he emigrated with his family to the United States, first working as a wood engraver in Philadelphia before going to Steubenville, Ohio, where his father had established a wallpaper manufacturing business. \n\nCole received rudimentary instruction from an itinerant artist, began painting portraits, genre scenes, and a few landscapes, and set out to seek his fortune through Ohio and Pennsylvania. He soon moved on to Philadelphia to pursue his art, inspired by paintings he saw at the Pennsylvania Academy of the Fine Arts. Moving to New York City in spring 1825, Cole made a trip up the Hudson River to the eastern Catskill Mountains. Based on his sketches there, he executed three landscapes that a city bookseller agreed to display in his window. Colonel [url href=https://www.wikiart.org/en/john-trumbull]John Trumbull[/url], already renowned as the painter of the American Revolution, saw Cole’s pictures and instantly purchased one, recommending the other two to his colleagues William Dunlap and [url href=https://www.wikiart.org/en/asher-brown-durand]Asher B. Durand[/url]. \n\nWhat Trumbull recognized in the work of the young painter was the perception of wildness inherent in American scenery that landscape artists had theretofore ignored. Trumbull brought Cole to the attention of various patrons, who began eagerly buying his work. Dunlap publicized the discovery of the new talent, and Cole was welcomed into New York’s cultural community, which included the poet and editor William Cullen Bryant and the author James Fenimore Cooper. Cole became one of the founding members of the National Academy of Design in 1825. Even as Cole expanded his travels and subjects to include scenes in the White Mountains of New Hampshire, he aspired to what he termed a “higher style of a landscape” that included narrative—some of the paintings in paired series—including biblical and literary subjects, such as Cooper’s popular [url href=https://www.wikiart.org/en/thomas-cole/scene-from-the-last-of-the-mohicans-by-james-fenimore-cooper-1827][i]Last of the Mohicans[/i][/url]. \n\nBy 1829, his success enabled him to take the Grand Tour of Europe and especially Italy, where he remained in 1831–32, visiting Florence, Rome, and Naples. Thereafter he painted many Italian subjects, like [url href=https://www.wikiart.org/en/thomas-cole/a-view-near-tivoli-morning-1832][i]View near Tivoli. Morning[/i][/url] (1832). The region around Rome, along with the classical myth, also inspired [url href=https://www.wikiart.org/en/thomas-cole/the-titan-s-goblet-1833][i]The Titan’s Goblet[/i][/url] (1833). Cole’s travels and the encouragement and patronage of the New York merchant Luman Reed culminated in his most ambitious historical landscape series, [url href=https://www.wikiart.org/en/thomas-cole/all-works#!#filterName:Series_the-course-of-empire,resultType:masonry][i]The Course of Empire[/i][/url] (1833–1836), five pictures dramatizing the rise and fall of an ancient classical state. \n\nCole also continued to paint, with ever-rising technical assurance, sublime American scenes such as the [url href=https://www.wikiart.org/en/thomas-cole/view-from-mount-holyoke-1836][i]View from Mount Holyoke[/i][/url] (1836), [url href=https://www.wikiart.org/en/thomas-cole/the-oxbow-the-connecticut-river-near-northampton-1836][i]The Oxbow[/i][/url] (1836), in which he included a portrait of himself painting the vista and [url href=https://www.wikiart.org/en/thomas-cole/view-on-the-catskill-early-autunm-1837][i]View on the Catskill—Early Autumn[/i][/url] (1836-1837), in which he pastorally interpreted the prospect of his beloved Catskill Mountains from the village of Catskill, where he had moved the year before and met his wife-to-be, Maria Bartow. \n\nThe artist’s marriage brought with it increasing religious piety manifested in the four-part series [url href=https://www.wikiart.org/en/thomas-cole/all-works#!#filterName:Series_the-voyage-of-life,resultType:masonry][i]The Voyage of Life[/i][/url] (1840). In it, a river journey represents the human passage through life to eternal reward. Cole painted and exhibited a replica of the series in Rome, where he returned in 1841–42, traveling south to Sicily. After his return, he lived and worked chiefly in Catskill, keeping up with art activity in New York primarily through Durand. He continued to produce American and foreign landscape subjects of incredible beauty, including the [url href=https://www.wikiart.org/en/thomas-cole/the-mountain-ford-1846][i]Mountain Ford[/i][/url] (1846). \n\nIn 1844, Cole welcomed into his Catskill studio the young [url href=https://www.wikiart.org/en/frederic-edwin-church]Frederic Church[/url], who studied with him until 1846 and went on to become the most renowned exponent of the generation that followed Cole. By 1846, Cole was at work on his largest and most ambitious series, [url href=https://www.wikiart.org/en/thomas-cole/all-works#!#filterName:Series_the-cross-and-the-world,resultType:masonry][i]The Cross and the World[/i][/url], but in February 1848 contracted pleurisy and died before completing it. \n\nThe paintings of Thomas Cole, like the writings of his contemporary Ralph Waldo Emerson, stand as monuments to the dreams and anxieties of the fledgling American nation during the mid-19th century; and they are also euphoric celebrations of its natural landscapes. Cole is considered the first artist to bring the eye of a European [url href=https://www.wikiart.org/en/artists-by-art-movement/romanticism]Romantic[/url] landscape painter to those environments, but also a figure whose idealism and religious sensibilities expressed a uniquely American spirit. In his works, we find the dramatic splendor of [url href=https://www.wikiart.org/en/caspar-david-friedrich]Caspar David Freidrich[/url] or [url href=https://www.wikiart.org/en/william-turner]J.M.W Turner[/url] transposed onto the Catskill and Adirondack Mountains. But whereas younger American painters such as [url href=https://www.wikiart.org/en/albert-bierstadt]Albert Bierstadt[/url] had come into direct contact with [url href=https://www.wikiart.org/en/artists-by-art-institution/kunstakademie-dusseldorf-dusseldorf-germany#!#resultType:masonry]The Düsseldorf School of painting[/url], and thus with the tradition in which they placed themselves, Cole was largely self-tutored, representing something of the archetypal American figure of the auto-didact.\n\nIn many ways, Cole's art epitomizes all contradictions of European settler culture in America. He was in love with the sublime wildness of the American landscape and sought to preserve it with his art, but his very presence in that landscape, and the development of his career, depended on the processes of urbanization and civilization which threatened it. From a modern perspective, Cole's Eurocentric gaze on seemingly empty wildernesses which had, in fact, been populated for centuries, also seems troubling; where Native Americans do appear in his work, as in [url href=https://www.wikiart.org/en/thomas-cole/falls-of-the-kaaterskill-1826][i]Falls of the Kaaterskill[/i][/url] (1826), it is as picturesque flecks rather than characterized participants in the scene.\n\nCole's legacy is evident in the work of future American artists who advanced the Hudson River style, including his student Frederic Edwin Church, Albert Bierstadt, Jasper Cropsey, Asher B. Durand, [url href=https://www.wikiart.org/en/george-inness]George Inness[/url], [url href=https://www.wikiart.org/en/john-frederick-kensett]John Kensett[/url], and [url href=https://www.wikiart.org/en/thomas-moran]Thomas Moran[/url]. Speaking more broadly, a whole sweep of 20th-century North-American art, from [url href=https://www.wikiart.org/en/artists-by-art-movement/precisionism]Precisionism[/url] to [url href=https://www.wikiart.org/en/artists-by-art-movement/environmental-art]Land Art[/url], might be seen to have inherited something of the grand scale and ambition of Cole's work. In this sense, his paintings capture not only the character of American culture during the mid-19th century but perhaps something more enduring about the open and expansive quality of that culture.",
        "birthDay"          : "/Date(-5330448000000)/",
        "birthDayAsString"  : "February 1, 1801",
        "contentId"         : 254330,
        "deathDay"          : "/Date(-3846441600000)/",
        "deathDayAsString"  : "February 11, 1848",
        "dictonaries"       : [
            1368,
            11415,
            310,
        ],
        "gender"            : "male",
        "image"             : "https://uploads8.wikiart.org/temp/19f6a140-59d2-4959-8d11-fd4ca582b7f2.jpg!Portrait.jpg",
        "lastNameFirst"     : "Cole Thomas",
        "periodsOfWork"     : "",
        "relatedArtistsIds" : [],
        "series"            : "The Cross and the World\r\nThe Course of Empire\r\nThe Voyage of Life",
        "story"             : "http://en.wikipedia.org/wiki/Thomas_Cole",
        "themes"            : "",
        "url"               : "thomas-cole",
        "wikipediaUrl"      : "http://en.wikipedia.org/wiki/Thomas_Cole"
    },
    "artistName" : "Thomas Cole",
    "artistUrl"  : "/en/thomas-cole",
    "extension"  : str,
    "filename"   : str,
    "flags"      : int,
    "height"     : int,
    "id"         : r"re:[0-9a-f]+",
    "image"      : str,
    "map"        : str,
    "paintingUrl": r"re:/en/thomas-cole/.+",
    "title"      : str,
    "width"      : int,
    "year"       : str,
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
    "#results" : (
        "https://uploads5.wikiart.org/images/huang-shen/summer.jpg",
    ),
},

{
    "#url"     : "https://www.wikiart.org/en/paintings-by-media/grisaille",
    "#category": ("", "wikiart", "artworks"),
    "#class"   : wikiart.WikiartArtworksExtractor,
    "#sha1_url": "36e054fcb3363b7f085c81f4778e6db3994e56a3",
    "#results" : (
        "https://uploads4.wikiart.org/images/hieronymus-bosch/triptych-of-last-judgement.jpg",
        "https://uploads6.wikiart.org/images/hieronymus-bosch/triptych-of-last-judgement-1.jpg",
        "https://uploads0.wikiart.org/images/hieronymus-bosch/tiptych-of-temptation-of-st-anthony-1506.jpg",
        "https://uploads7.wikiart.org/images/matthias-grünewald/st-elizabeth-and-a-saint-woman-with-palm-1511.jpg",
        "https://uploads2.wikiart.org/images/matthias-grünewald/st-lawrence-and-st-cyricus-1511.jpg",
        "https://uploads0.wikiart.org/images/pieter-bruegel-the-elder/the-death-of-the-virgin.jpg",
        "https://uploads4.wikiart.org/images/pieter-bruegel-the-elder/christ-and-the-woman-taken-in-adultery-1565-1.jpg",
        "https://uploads6.wikiart.org/images/giovanni-battista-tiepolo/not_detected_241014.jpg",
        "https://uploads4.wikiart.org/images/edgar-degas/interior-the-rape-1869.jpg",
        "https://uploads3.wikiart.org/00265/images/john-singer-sargent/1396294310-dame-alice-ellen-terry-by-john-singer-sargent.jpg",
        "https://uploads0.wikiart.org/00293/images/hryhorii-havrylenko/1954-18-5-32-5.jpg",
    ),
},

{
    "#url"     : "https://www.wikiart.org/en/artists-by-century/12",
    "#category": ("", "wikiart", "artists"),
    "#class"   : wikiart.WikiartArtistsExtractor,
    "#pattern" : wikiart.WikiartArtistExtractor.pattern,
    "#count"   : ">= 8",
},

)
