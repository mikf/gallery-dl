# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import slideshare


__tests__ = (
{
    "#url"     : "https://www.slideshare.net/Slideshare/get-started-with-slide-share",
    "#category": ("", "slideshare", "presentation"),
    "#class"   : slideshare.SlidesharePresentationExtractor,
    "#pattern"     : r"https://image\.slidesharecdn\.com/getstartedwithslideshare-150520173821-lva1-app6892/95/get-started-with-slide-share-\d+-1024\.jpg\?cb=\d+",
    "#count"       : 19,
    "#sha1_content": "2b6a191eab60b3978fdacfecf2da302dd45bc108",

    "description" : "Get Started with SlideShare - A Beginngers Guide for Creators",
    "likes"       : int,
    "presentation": "get-started-with-slide-share",
    "date"        : "dt:2015-05-20 17:38:21",
    "title"       : "Getting Started With SlideShare",
    "user"        : "Slideshare",
    "views"       : int,
},

{
    "#url"     : "https://www.slideshare.net/pragmaticsolutions/warum-sie-nicht-ihren-mitarbeitenden-ndern-sollten-sondern-ihr-managementsystem",
    "#comment" : "long title and description",
    "#category": ("", "slideshare", "presentation"),
    "#class"   : slideshare.SlidesharePresentationExtractor,
    "#sha1_url": "d8952260f8bec337dd809a958ec8091350393f6b",

    "title"      : "Warum Sie nicht Ihren Mitarbeitenden ändern sollten, sondern Ihr Managementsystem",
    "description": "Mitarbeitende verhalten sich mehrheitlich so, wie das System es ihnen vorgibt. Welche Voraussetzungen es braucht, damit Ihre Mitarbeitenden ihr ganzes Herzblut einsetzen, bespricht Fredi Schmidli in diesem Referat.",
},

{
    "#url"     : "https://www.slideshare.net/mobile/uqudent/introduction-to-fixed-prosthodontics",
    "#comment" : "mobile URL",
    "#category": ("", "slideshare", "presentation"),
    "#class"   : slideshare.SlidesharePresentationExtractor,
    "#sha1_url": "72c431cb1eccbb6794f608ecbbc01d52e8768159",
},

)
