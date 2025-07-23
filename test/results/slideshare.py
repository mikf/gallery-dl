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
    "#pattern"     : r"https://image\.slidesharecdn\.com/getstartedwithslideshare-150520173821-lva1-app6892/95/Getting-Started-With-SlideShare-\d+-1024\.jpg",
    "#count"       : 19,
    "#sha1_content": "2b6a191eab60b3978fdacfecf2da302dd45bc108",

    "description" : "SlideShare is a global platform for sharing presentations, infographics, videos and documents. It has over 18 million pieces of professional content uploaded by experts like Eric Schmidt and Guy Kawasaki. The document provides tips for setting up an account on SlideShare, uploading content, optimizing it for searchability, and sharing it on social media to build an audience and reputation as a subject matter expert.",
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
    "#sha1_url": "c2d0079cc3b05de0fd93b0d0b1f47ff2a32119b7",

    "title"      : "Warum Sie nicht Ihren Mitarbeitenden ändern sollten, sondern Ihr Managementsystem",
    "description": "Mitarbeitende verhalten sich mehrheitlich so, wie das System es ihnen vorgibt. Welche Voraussetzungen es braucht, damit Ihre Mitarbeitenden ihr ganzes Herzblut einsetzen, bespricht Fredi Schmidli in diesem Referat.",
},

{
    "#url"     : "https://www.slideshare.net/mobile/uqudent/introduction-to-fixed-prosthodontics",
    "#comment" : "mobile URL",
    "#category": ("", "slideshare", "presentation"),
    "#class"   : slideshare.SlidesharePresentationExtractor,
    "#pattern" : r"https://image\.slidesharecdn\.com/introductiontofixedprosthodonticsfinal-110427200948-phpapp02/95/Introduction-to-fixed-prosthodontics-\d+-1024\.jpg",
    "#count"   : 27,
},

)
