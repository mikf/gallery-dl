# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagebam
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.imagebam.com/gallery/adz2y0f9574bjpmonaismyrhtjgvey4o",
    "#category": ("", "imagebam", "gallery"),
    "#class"   : imagebam.ImagebamGalleryExtractor,
    "#sha1_url"     : "76d976788ae2757ac81694736b07b72356f5c4c8",
    "#sha1_metadata": "b048478b1bbba3072a7fa9fcc40630b3efad1f6c",
    "#sha1_content" : "596e6bfa157f2c7169805d50075c2986549973a8",
},

{
    "#url"     : "http://www.imagebam.com/gallery/op9dwcklwdrrguibnkoe7jxgvig30o5p",
    "#category": ("", "imagebam", "gallery"),
    "#class"   : imagebam.ImagebamGalleryExtractor,
    "#count"   : 107,
    "#sha1_url": "32ae6fe5dc3e4ca73ff6252e522d16473595d1d1",
},

{
    "#url"     : "http://www.imagebam.com/gallery/gsl8teckymt4vbvx1stjkyk37j70va2c",
    "#category": ("", "imagebam", "gallery"),
    "#class"   : imagebam.ImagebamGalleryExtractor,
    "#exception": exception.HttpError,
},

{
    "#url"     : "https://www.imagebam.com/view/GA3MT1",
    "#comment" : "/view/ path (#2378)",
    "#category": ("", "imagebam", "gallery"),
    "#class"   : imagebam.ImagebamGalleryExtractor,
    "#sha1_url"     : "35018ce1e00a2d2825a33d3cd37857edaf804919",
    "#sha1_metadata": "3a9f98178f73694c527890c0d7ca9a92b46987ba",
},

{
    "#url"     : "https://www.imagebam.com/image/94d56c502511890",
    "#category": ("", "imagebam", "image"),
    "#class"   : imagebam.ImagebamImageExtractor,
    "#sha1_url"     : "5e9ba3b1451f8ded0ae3a1b84402888893915d4a",
    "#sha1_metadata": "2a4380d4b57554ff793898c2d6ec60987c86d1a1",
    "#sha1_content" : "0c8768055e4e20e7c7259608b67799171b691140",
},

{
    "#url"     : "http://images3.imagebam.com/1d/8c/44/94d56c502511890.png",
    "#category": ("", "imagebam", "image"),
    "#class"   : imagebam.ImagebamImageExtractor,
},

{
    "#url"     : "https://www.imagebam.com/image/0850951366904951",
    "#comment" : "NSFW (#1534)",
    "#category": ("", "imagebam", "image"),
    "#class"   : imagebam.ImagebamImageExtractor,
    "#sha1_url": "d37297b17ed1615b4311c8ed511e50ce46e4c748",
},

{
    "#url"     : "https://www.imagebam.com/view/ME8JOQP",
    "#comment" : "/view/ path (#2378)",
    "#category": ("", "imagebam", "image"),
    "#class"   : imagebam.ImagebamImageExtractor,
    "#sha1_url"     : "4dca72bbe61a0360185cf4ab2bed8265b49565b8",
    "#sha1_metadata": "15a494c02fd30846b41b42a26117aedde30e4ceb",
    "#sha1_content" : "f81008666b17a42d8834c4749b910e1dc10a6e83",
},

{
    "#url"     : "https://www.imagebam.com/image/b728aa119132443",
    "#comment" : "filename without extension (#8476)",
    "#class"   : imagebam.ImagebamImageExtractor,
    "#results" : "https://images3.imagebam.com/d2/7a/d9/b728aa119132443.jpg",

    "extension": "",
    "filename" : "34415_AlessandraAmbrosio_PhotoshootforVictoriasSecretwearingbikinislingerieonthebeachinMalibuCalifor",
    "image_key": "b728aa119132443",
    "url"      : "https://images3.imagebam.com/d2/7a/d9/b728aa119132443.jpg",
},

)
