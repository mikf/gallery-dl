#!/usr/bin/env python

import sys
import os.path
import collections

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.realpath(ROOTDIR))
from gallery_dl import extractor  # noqa


CATEGORY_MAP = {
    "2chan"          : "Futaba Channel",
    "archivedmoe"    : "Archived.Moe",
    "archiveofsins"  : "Archive of Sins",
    "artstation"     : "ArtStation",
    "b4k"            : "arch.b4k.co",
    "bobx"           : "BobX",
    "deviantart"     : "DeviantArt",
    "dokireader"     : "Doki Reader",
    "dynastyscans"   : "Dynasty Reader",
    "e621"           : "e621",
    "exhentai"       : "ExHentai",
    "fallenangels"   : "Fallen Angels Scans",
    "fashionnova"    : "Fashion Nova",
    "hbrowse"        : "HBrowse",
    "hentai2read"    : "Hentai2Read",
    "hentaicafe"     : "Hentai Cafe",
    "hentaifoundry"  : "Hentai Foundry",
    "hentaifox"      : "HentaiFox",
    "hentaihere"     : "HentaiHere",
    "hitomi"         : "Hitomi.la",
    "idolcomplex"    : "Idol Complex",
    "imagebam"       : "ImageBam",
    "imagefap"       : "ImageFap",
    "imgbox"         : "imgbox",
    "imgth"          : "imgth",
    "imgur"          : "imgur",
    "jaiminisbox"    : "Jaimini's Box",
    "kireicake"      : "Kirei Cake",
    "kissmanga"      : "KissManga",
    "mangadex"       : "MangaDex",
    "mangafox"       : "Manga Fox",
    "mangahere"      : "Manga Here",
    "mangapark"      : "MangaPark",
    "mangastream"    : "Manga Stream",
    "myportfolio"    : "Adobe Portfolio",
    "nhentai"        : "nhentai",
    "nijie"          : "nijie",
    "nyafuu"         : "Nyafuu Archive",
    "paheal"         : "rule #34",
    "powermanga"     : "PowerManga",
    "readcomiconline": "Read Comic Online",
    "rbt"            : "RebeccaBlackTech",
    "rule34"         : "Rule 34",
    "sankaku"        : "Sankaku Channel",
    "seaotterscans"  : "Sea Otter Scans",
    "seiga"          : "Niconico Seiga",
    "senmanga"       : "Sen Manga",
    "sensescans"     : "Sense-Scans",
    "simplyhentai"   : "Simply Hentai",
    "slideshare"     : "SlideShare",
    "smugmug"        : "SmugMug",
    "thebarchive"    : "The /b/ Archive",
    "worldthree"     : "World Three",
    "xvideos"        : "XVideos",
    "yuki"           : "yuki.la 4chan archive",
}

SUBCATEGORY_MAP = {
    "artwork": "Artwork Listings",
    "doujin" : "Doujin",
    "gallery": "Galleries",
    "image"  : "individual Images",
    "issue"  : "Comic-Issues",
    "manga"  : "Manga",
    "me"     : "pixiv.me Links",
    "media"  : "Media Timelines",
    "path"   : "Images from Users and Folders",
    "pinit"  : "pin.it Links",
    "popular": "Popular Images",
    "recent" : "Recent Images",
    "search" : "Search Results",
    "stash"  : "Sta.sh",
    "status" : "Images from Statuses",
    "tag"    : "Tag-Searches",
    "user"   : "Images from Users",
    "work"   : "Individual Images",
    "related-pin"  : "related Pins",
    "related-board": "",
}

AUTH_MAP = {
    "danbooru"   : "Optional",
    "deviantart" : "Optional (OAuth)",
    "exhentai"   : "Optional",
    "flickr"     : "Optional (OAuth)",
    "idolcomplex": "Optional",
    "luscious"   : "Optional",
    "nijie"      : "Required",
    "pixiv"      : "Required",
    "reddit"     : "Optional (OAuth)",
    "sankaku"    : "Optional",
    "seiga"      : "Required",
    "smugmug"    : "Optional (OAuth)",
    "tsumino"    : "Optional",
    "tumblr"     : "Optional (OAuth)",
    "wallhaven"  : "Optional",
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
    sc = cls.subcategory
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
    if cls.subcategory in ("user", "issue"):
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

        if len(output) > size:
            sub = "|{}-{}|".format(category, col[0][0])
            subs.append((sub, output))
            output = sub

        return output + " " * (size - len(output))

    w = fobj.write
    subs = []

    # caption
    w("Supported Sites\n")
    w("===============\n")

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
with open(os.path.join(ROOTDIR, "docs", outfile), "w") as file:
    write_output(file, COLUMNS, build_extractor_list())
