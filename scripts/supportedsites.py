#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generate a reStructuredText document with all supported sites"""

import sys
import collections

import util
from gallery_dl import extractor


CATEGORY_MAP = {
    "2chan"          : "Futaba Channel",
    "35photo"        : "35PHOTO",
    "adultempire"    : "Adult Empire",
    "archivedmoe"    : "Archived.Moe",
    "archiveofsins"  : "Archive of Sins",
    "artstation"     : "ArtStation",
    "aryion"         : "Eka's Portal",
    "b4k"            : "arch.b4k.co",
    "baraag"         : "baraag",
    "bcy"            : "半次元",
    "bobx"           : "BobX",
    "deviantart"     : "DeviantArt",
    "dokireader"     : "Doki Reader",
    "dynastyscans"   : "Dynasty Reader",
    "e621"           : "e621",
    "e-hentai"       : "E-Hentai",
    "exhentai"       : "ExHentai",
    "fallenangels"   : "Fallen Angels Scans",
    "fashionnova"    : "Fashion Nova",
    "furaffinity"    : "Fur Affinity",
    "hbrowse"        : "HBrowse",
    "hentai2read"    : "Hentai2Read",
    "hentaicafe"     : "Hentai Cafe",
    "hentaifoundry"  : "Hentai Foundry",
    "hentaifox"      : "HentaiFox",
    "hentaihand"     : "HentaiHand",
    "hentaihere"     : "HentaiHere",
    "hitomi"         : "Hitomi.la",
    "idolcomplex"    : "Idol Complex",
    "imagebam"       : "ImageBam",
    "imagefap"       : "ImageFap",
    "imgbb"          : "ImgBB",
    "imgbox"         : "imgbox",
    "imagechest"     : "ImageChest",
    "imgth"          : "imgth",
    "imgur"          : "imgur",
    "jaiminisbox"    : "Jaimini's Box",
    "kabeuchi"       : "かべうち",
    "kireicake"      : "Kirei Cake",
    "kissmanga"      : "KissManga",
    "lineblog"       : "LINE BLOG",
    "livedoor"       : "livedoor Blog",
    "mangadex"       : "MangaDex",
    "mangafox"       : "Manga Fox",
    "mangahere"      : "Manga Here",
    "mangakakalot"   : "MangaKakalot",
    "mangapark"      : "MangaPark",
    "mangastream"    : "Manga Stream",
    "mastodon.social": "mastodon.social",
    "myportfolio"    : "Adobe Portfolio",
    "nhentai"        : "nhentai",
    "nijie"          : "nijie",
    "nozomi"         : "Nozomi.la",
    "nsfwalbum"      : "NSFWalbum.com",
    "nyafuu"         : "Nyafuu Archive",
    "paheal"         : "rule #34",
    "powermanga"     : "PowerManga",
    "readcomiconline": "Read Comic Online",
    "rbt"            : "RebeccaBlackTech",
    "redgifs"        : "RedGIFs",
    "rule34"         : "Rule 34",
    "sankaku"        : "Sankaku Channel",
    "sankakucomplex" : "Sankaku Complex",
    "seaotterscans"  : "Sea Otter Scans",
    "seiga"          : "Niconico Seiga",
    "senmanga"       : "Sen Manga",
    "sensescans"     : "Sense-Scans",
    "sexcom"         : "Sex.com",
    "simplyhentai"   : "Simply Hentai",
    "slickpic"       : "SlickPic",
    "slideshare"     : "SlideShare",
    "smugmug"        : "SmugMug",
    "speakerdeck"    : "Speaker Deck",
    "subscribestar"  : "SubscribeStar",
    "thebarchive"    : "The /b/ Archive",
    "vanillarock"    : "もえぴりあ",
    "vsco"           : "VSCO",
    "webtoons"       : "Webtoon",
    "wikiart"        : "WikiArt.org",
    "worldthree"     : "World Three",
    "xhamster"       : "xHamster",
    "xvideos"        : "XVideos",
    "yuki"           : "yuki.la 4chan archive",
}

SUBCATEGORY_MAP = {
    "doujin" : "Doujin",
    "gallery": "Galleries",
    "image"  : "individual Images",
    "issue"  : "Comic Issues",
    "manga"  : "Manga",
    "popular": "Popular Images",
    "recent" : "Recent Images",
    "search" : "Search Results",
    "status" : "Images from Statuses",
    "tag"    : "Tag Searches",
    "user"   : "User Profiles",
    "following"    : "",
    "related-pin"  : "related Pins",
    "related-board": "",

    "artstation": {
        "artwork": "Artwork Listings",
    },
    "deviantart": {
        "stash": "Sta.sh",
    },
    "instagram": {
        "saved": "Saved Posts",
    },
    "newgrounds": {
        "art"  : "Art",
        "audio": "Audio",
        "media": "Media Files",
    },
    "pinterest": {
        "pinit": "pin.it Links",
    },
    "pixiv": {
        "me"  : "pixiv.me Links",
        "work": "individual Images",
    },
    "smugmug": {
        "path": "Images from Users and Folders",
    },
    "twitter": {
        "media": "Media Timelines",
    },
    "wikiart": {
        "artists": "Artist Listings",
    },
}

_OAUTH = " (`OAuth <https://github.com/mikf/gallery-dl#oauth>`__)"
_COOKIES = " (`Cookies <https://github.com/mikf/gallery-dl#cookies>`__)"
_APIKEY_WH = " (`API Key <configuration.rst#extractorwallhavenapi-key>`__)"

AUTH_MAP = {
    "aryion"         : "Optional" + _COOKIES,
    "baraag"         : "Optional" + _OAUTH,
    "danbooru"       : "Optional",
    "deviantart"     : "Optional" + _OAUTH,
    "e621"           : "Optional",
    "e-hentai"       : "Optional",
    "exhentai"       : "Optional",
    "flickr"         : "Optional" + _OAUTH,
    "furaffinity"    : "Optional" + _COOKIES,
    "idolcomplex"    : "Optional",
    "imgbb"          : "Optional",
    "inkbunny"       : "Optional",
    "instagram"      : "Optional",
    "mangoxo"        : "Optional",
    "mastodon.social": "Optional" + _OAUTH,
    "newgrounds"     : "Optional",
    "nijie"          : "Required",
    "patreon"        : "Optional" + _COOKIES,
    "pawoo"          : "Optional" + _OAUTH,
    "pixiv"          : "Required",
    "reddit"         : "Optional" + _OAUTH,
    "sankaku"        : "Optional",
    "seiga"          : "Required",
    "smugmug"        : "Optional" + _OAUTH,
    "subscribestar"  : "Optional",
    "tsumino"        : "Optional",
    "tumblr"         : "Optional" + _OAUTH,
    "twitter"        : "Optional",
    "wallhaven"      : "Optional" + _APIKEY_WH,
}

IGNORE_LIST = (
    "directlink",
    "oauth",
    "recursive",
    "test",
)


def domain(cls):
    """Return the web-domain related to an extractor class"""
    url = sys.modules[cls.__module__].__doc__.split()[-1]
    if url.startswith("http"):
        return url

    if hasattr(cls, "root") and cls.root:
        return cls.root + "/"

    if hasattr(cls, "https"):
        scheme = "https" if cls.https else "http"
        netloc = cls.__doc__.split()[-1]
        return "{}://{}/".format(scheme, netloc)

    test = next(cls._get_tests(), None)
    if test:
        url = test[0]
        return url[:url.find("/", 8)+1]

    return ""


def category_text(cls):
    """Return a human-readable representation of a category"""
    c = cls.category
    return CATEGORY_MAP.get(c) or c.capitalize()


def subcategory_text(cls):
    """Return a human-readable representation of a subcategory"""
    c, sc = cls.category, cls.subcategory

    if c in SUBCATEGORY_MAP:
        scm = SUBCATEGORY_MAP[c]
        if sc in scm:
            return scm[sc]

    if sc in SUBCATEGORY_MAP:
        return SUBCATEGORY_MAP[sc]

    sc = sc.capitalize()
    return sc if sc.endswith("s") else sc + "s"


def category_key(cls):
    """Generate sorting keys by category"""
    key = category_text(cls).lower()
    if cls.__module__.endswith(".imagehosts"):
        key = "zz" + key
    return key


def subcategory_key(cls):
    """Generate sorting keys by subcategory"""
    if cls.subcategory == "issue":
        return "A"
    return cls.subcategory


def build_extractor_list():
    """Generate a sorted list of lists of extractor classes"""
    extractors = collections.defaultdict(list)

    # get lists of extractor classes grouped by category
    for extr in extractor.extractors():
        if not extr.category or extr.category in IGNORE_LIST:
            continue
        extractors[extr.category].append(extr)

    # sort extractor lists with the same category
    for extrlist in extractors.values():
        extrlist.sort(key=subcategory_key)

    # ugly hack to add e-hentai.org
    eh = []
    for extr in extractors["exhentai"]:
        class eh_extr(extr):
            category = "e-hentai"
            root = "https://e-hentai.org"
        eh.append(eh_extr)
    extractors["e-hentai"] = eh

    # sort lists by category
    return sorted(
        extractors.values(),
        key=lambda lst: category_key(lst[0]),
    )


# define table columns
COLUMNS = (
    ("Site", 20,
     lambda x: category_text(x[0])),
    ("URL" , 35,
     lambda x: domain(x[0])),
    ("Capabilities", 50,
     lambda x: ", ".join(subcategory_text(extr) for extr in x
                         if subcategory_text(extr))),
    ("Authentication", 16,
     lambda x: AUTH_MAP.get(x[0].category, "")),
)


def write_output(fobj, columns, extractors):

    def pad(output, col, category=None):
        size = col[1]
        output = output if isinstance(output, str) else col[2](output)

        if len(output) > size and col[0][0] != "A":
            sub = "|{}-{}|".format(category, col[0][0])
            subs.append((sub, output))
            output = sub

        return output + " " * (size - len(output))

    w = fobj.write
    subs = []

    # caption
    w("Supported Sites\n")
    w("===============\n")
    w("Unless otherwise known, assume all sites to be NSFW\n\n")

    # table head
    sep = " ".join("=" * c[1] for c in columns) + "\n"
    w(sep)
    w(" ".join(pad(c[0], c) for c in columns).strip() + "\n")
    w(sep)

    # table body
    for lst in extractors:
        w(" ".join(
            pad(col[2](lst), col, lst[0].category)
            for col in columns
        ).strip())
        w("\n")

    # table bottom
    w(sep)
    w("\n")

    # substitutions
    for sub, value in subs:
        w(".. {} replace:: {}\n".format(sub, value))


outfile = sys.argv[1] if len(sys.argv) > 1 else "supportedsites.rst"
with open(util.path("docs", outfile), "w") as file:
    write_output(file, COLUMNS, build_extractor_list())
