# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nudecollect.com/"""

from .common import GalleryExtractor
from .. import text


class NudecollectExtractor(GalleryExtractor):
    """Base class for Nudecollect extractors"""
    category = "nudecollect"
    directory_fmt = ("{category}", "{title}")
    filename_fmt = "{slug}_{num:>03}.{extension}"
    archive_fmt = "{slug}_{num}"
    root = "https://www.nudecollect.com"

    def request(self, url, **kwargs):
        kwargs["allow_redirects"] = False
        return GalleryExtractor.request(self, url, **kwargs)

    @staticmethod
    def get_title(page):
        return text.unescape(text.extr(page, "<title>", "</title>"))[31:]

    @staticmethod
    def get_image(page):
        return text.extr(page, '<img src="', '"')


class NudecollectImageExtractor(NudecollectExtractor):
    """Extractor for individual images from nudecollect.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:www\.)?nudecollect\.com"
               r"(/content/([^/?#]+)/image-(\d+)-pics-(\d+)"
               r"-mirror-(\d+)\.html)")
    test = (
        (("https://www.nudecollect.com/content/20201220_Teenpornstorage_"
          "Patritcy_Vanessa_Lesbian_Lust/image-4-pics-108-mirror-43.html"), {
            "pattern": (r"https://mirror\d+\.nudecollect\.com/showimage"
                        r"/nudecollect-8769086487/image00004-5896498214-43"
                        r"-9689595623/20201220_Teenpornstorage_Patritcy_Vaness"
                        r"a_Lesbian_Lust/9879560327/nudecollect\.com\.jpg"),
            "keyword": {
                "slug"  : ("20201220_Teenpornstorage_Patritcy"
                           "_Vanessa_Lesbian_Lust"),
                "title" : ("20201220 Teenpornstorage Patritcy"
                           " Vanessa Lesbian Lust"),
                "num"   : 4,
                "count" : 108,
                "mirror": 43,
            },
        }),
        (("https://www.nudecollect.com/content/20201220_Teenpornstorage_"
          "Patritcy_Vanessa_Lesbian_Lust/image-10-pics-108-mirror-43.html")),
    )

    def __init__(self, match):
        NudecollectExtractor.__init__(self, match)
        _, self.slug, self.num, self.count, self.mirror = match.groups()

    def metadata(self, page):
        return {
            "slug"  : self.slug,
            "title" : self.get_title(page),
            "count" : text.parse_int(self.count),
            "mirror": text.parse_int(self.mirror),
        }

    def images(self, page):
        return ((self.get_image(page), {"num": text.parse_int(self.num)}),)


class NudecollectAlbumExtractor(NudecollectExtractor):
    """Extractor for image albums on nudecollect.com"""
    subcategory = "album"
    pattern = (r"(?:https?://)?(?:www\.)?nudecollect\.com"
               r"/content/([^/?#]+)/(?:index-mirror-(\d+)-(\d+)"
               r"|page-\d+-pics-(\d+)-mirror-(\d+))\.html")
    test = (
        (("https://www.nudecollect.com/content/20170219_TheWhiteBoxxx_"
          "Caprice_Tracy_Loves_Hot_ass_fingering_and_sensual_lesbian_sex"
          "_with_alluring_Czech_babes_x125_1080px/index-mirror-67-125.html"), {
            "pattern": (r"https://mirror\d+\.nudecollect\.com/showimage"
                        r"/nudecollect-8769086487/image00\d\d\d-5896498214-67"
                        r"-9689595623/20170219_TheWhiteBoxxx_Caprice"
                        r"_Tracy_Loves_Hot_ass_fingering_and_sensual_"
                        r"lesbian_sex_with_alluring_Czech_babes_x125_1080px"
                        r"/9879560327/nudecollect\.com\.jpg"),
            "count"  : 125,
            "keyword": {
                "slug"  : ("20170219_TheWhiteBoxxx_Caprice_Tracy_Loves_Hot_"
                           "ass_fingering_and_sensual_lesbian_sex_with_"
                           "alluring_Czech_babes_x125_1080px"),
                "title" : ("20170219 TheWhiteBoxxx Caprice Tracy Loves Hot ass"
                           " fingering and sensual lesbian sex with alluring"
                           " Czech babes x125 1080px"),
                "num"   : int,
                "mirror": 67,
            },
        }),
        (("https://www.nudecollect.com/content/20201220_Teenpornstorage_"
          "Patritcy_Vanessa_Lesbian_Lust/page-1-pics-108-mirror-43.html"), {
            "pattern": (r"https://mirror\d+\.nudecollect\.com/showimage"
                        r"/nudecollect-8769086487/image00\d\d\d-5896498214-43"
                        r"-9689595623/20201220_Teenpornstorage_Patritcy_Vaness"
                        r"a_Lesbian_Lust/9879560327/nudecollect\.com\.jpg"),
            "count"  : 108,
            "keyword": {
                "slug"  : ("20201220_Teenpornstorage_Patritcy"
                           "_Vanessa_Lesbian_Lust"),
                "title" : ("20201220 Teenpornstorage Patritcy"
                           " Vanessa Lesbian Lust"),
                "num"   : int,
                "mirror": 43,
            },
        }),
    )

    def __init__(self, match):
        self.slug = match.group(1)
        self.mirror = match.group(2) or match.group(5)
        self.count = text.parse_int(match.group(3) or match.group(4))
        url = "{}/content/{}/image-1-pics-{}-mirror-{}.html".format(
            self.root, self.slug, self.count, self.mirror)
        NudecollectExtractor.__init__(self, match, url)

    def metadata(self, page):
        return {
            "slug"  : self.slug,
            "title" : self.get_title(page),
            "mirror": text.parse_int(self.mirror),
        }

    def images(self, page):
        url = self.get_image(page)
        p1, _, p2 = url.partition("/image0")
        ufmt = p1 + "/image{:>05}" + p2[4:]
        return [(ufmt.format(num), None) for num in range(1, self.count + 1)]
