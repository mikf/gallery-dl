#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generate a reStructuredText document with all supported sites"""

import os
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
    "erome"          : "EroMe",
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
    "myhentaigallery": "My Hentai Gallery",
    "myportfolio"    : "Adobe Portfolio",
    "nhentai"        : "nhentai",
    "nijie"          : "nijie",
    "nozomi"         : "Nozomi.la",
    "nsfwalbum"      : "NSFWalbum.com",
    "nyafuu"         : "Nyafuu Archive",
    "paheal"         : "rule #34",
    "photovogue"     : "PhotoVogue",
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
    "hentaifoundry": {
        "story": "",
    },
    "instagram": {
        "posts": "",
        "saved": "Saved Posts",
    },
    "newgrounds": {
        "art"  : "Art",
        "audio": "Audio",
        "media": "Media Files",
    },
    "pinterest": {
        "board": "",
        "pinit": "pin.it Links",
    },
    "pixiv": {
        "me"  : "pixiv.me Links",
        "work": "individual Images",
    },
    "sankaku": {
        "books": "Book Searches",
    },
    "smugmug": {
        "path": "Images from Users and Folders",
    },
    "twitter": {
        "media": "Media Timelines",
        "list-members": "List Members",
    },
    "wikiart": {
        "artists": "Artist Listings",
    },
    "weasyl": {
        "journals"   : "",
        "submissions": "",
    },
}

_OAUTH = "`OAuth <https://github.com/mikf/gallery-dl#oauth>`__"
_COOKIES = "`Cookies <https://github.com/mikf/gallery-dl#cookies>`__"
_APIKEY_DB = "`API Key <configuration.rst#extractorderpibooruapi-key>`__"
_APIKEY_WH = "`API Key <configuration.rst#extractorwallhavenapi-key>`__"
_APIKEY_WY = "`API Key <configuration.rst#extractorweasylapi-key>`__"

AUTH_MAP = {
    "aryion"         : "Supported",
    "baraag"         : _OAUTH,
    "danbooru"       : "Supported",
    "derpibooru"     : _APIKEY_DB,
    "deviantart"     : _OAUTH,
    "e621"           : "Supported",
    "e-hentai"       : "Supported",
    "exhentai"       : "Supported",
    "flickr"         : _OAUTH,
    "furaffinity"    : _COOKIES,
    "idolcomplex"    : "Supported",
    "imgbb"          : "Supported",
    "inkbunny"       : "Supported",
    "instagram"      : "Supported",
    "mangoxo"        : "Supported",
    "mastodon.social": _OAUTH,
    "newgrounds"     : "Supported",
    "nijie"          : "Required",
    "patreon"        : _COOKIES,
    "pawoo"          : _OAUTH,
    "pinterest"      : "Supported",
    "pixiv"          : _OAUTH,
    "reddit"         : _OAUTH,
    "sankaku"        : "Supported",
    "seiga"          : "Required",
    "smugmug"        : _OAUTH,
    "subscribestar"  : "Supported",
    "tsumino"        : "Supported",
    "tumblr"         : _OAUTH,
    "twitter"        : "Supported",
    "wallhaven"      : _APIKEY_WH,
    "weasyl"         : _APIKEY_WY,
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


def category_text(c):
    """Return a human-readable representation of a category"""
    return CATEGORY_MAP.get(c) or c.capitalize()


def subcategory_text(c, sc):
    """Return a human-readable representation of a subcategory"""
    if c in SUBCATEGORY_MAP:
        scm = SUBCATEGORY_MAP[c]
        if sc in scm:
            return scm[sc]

    if sc in SUBCATEGORY_MAP:
        return SUBCATEGORY_MAP[sc]

    sc = sc.capitalize()
    return sc if sc.endswith("s") else sc + "s"


def category_key(c):
    """Generate sorting keys by category"""
    return category_text(c[0]).lower()


def subcategory_key(sc):
    """Generate sorting keys by subcategory"""
    return "A" if sc == "issue" else sc


def build_extractor_list():
    """Generate a sorted list of lists of extractor classes"""
    categories = collections.defaultdict(list)
    domains = {}

    for extr in extractor._list_classes():
        category = extr.category
        if category in IGNORE_LIST:
            continue
        if category:
            categories[category].append(extr.subcategory)
            if category not in domains:
                domains[category] = domain(extr)
        else:
            for category, root in extr.instances:
                categories[category].append(extr.subcategory)
                if category not in domains:
                    domains[category] = root + "/"

    # sort subcategory lists
    for subcategories in categories.values():
        subcategories.sort(key=subcategory_key)

    # add e-hentai.org
    categories["e-hentai"] = categories["exhentai"]
    domains["e-hentai"] = domains["exhentai"].replace("x", "-")

    return categories, domains


# define table columns
COLUMNS = (
    ("Site", 20,
     lambda c, scs, d: category_text(c)),
    ("URL" , 35,
     lambda c, scs, d: d),
    ("Capabilities", 50,
     lambda c, scs, d: ", ".join(subcategory_text(c, sc) for sc in scs
                                 if subcategory_text(c, sc))),
    ("Authentication", 16,
     lambda c, scs, d: AUTH_MAP.get(c, "")),
)


def write_output(fp, columns, categories, domains):

    def pad(output, col, category=None):
        size = col[1]
        output = output if isinstance(output, str) else col[2](output)

        if len(output) > size and col[0][0] != "A":
            sub = "|{}-{}|".format(category, col[0][0])
            subs.append((sub, output))
            output = sub

        return output + " " * (size - len(output))

    w = fp.write
    subs = []

    # caption
    w("Supported Sites\n")
    w("===============\n")
    w("..\n    generated by {}\n\n".format(
        "/".join(os.path.normpath(__file__).split(os.sep)[-2:])))
    w("Consider all sites to be NSFW, unless otherwise known.\n\n")

    # table head
    sep = " ".join("=" * c[1] for c in columns) + "\n"
    w(sep)
    w(" ".join(pad(c[0], c) for c in columns).strip() + "\n")
    w(sep)

    # table body
    clist = sorted(categories.items(), key=category_key)
    for category, subcategories in clist:
        domain = domains[category]
        w(" ".join(
            pad(col[2](category, subcategories, domain), col, category)
            for col in columns
        ).strip())
        w("\n")

    # table bottom
    w(sep)
    w("\n")

    # substitutions
    for sub, value in subs:
        w(".. {} replace:: {}\n".format(sub, value))


categories, domains = build_extractor_list()
outfile = sys.argv[1] if len(sys.argv) > 1 else "supportedsites.rst"
with open(util.path("docs", outfile), "w") as file:
    write_output(file, COLUMNS, categories, domains)
