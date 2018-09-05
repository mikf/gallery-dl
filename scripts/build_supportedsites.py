#!/usr/bin/env python

import sys
import os.path

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.realpath(ROOTDIR))
import gallery_dl.extractor  # noqa


CATEGORY_MAP = {
    "2chan"          : "Futaba Channel",
    "archivedmoe"    : "Archived.Moe",
    "archiveofsins"  : "Archive of Sins",
    "artstation"     : "ArtStation",
    "b4k"            : "arch.b4k.co",
    "deviantart"     : "DeviantArt",
    "dokireader"     : "Doki Reader",
    "dynastyscans"   : "Dynasty Reader",
    "e621"           : "e621",
    "exhentai"       : "ExHentai",
    "fallenangels"   : "Fallen Angels Scans",
    "hbrowse"        : "HBrowse",
    "hentai2read"    : "Hentai2Read",
    "hentaicafe"     : "Hentai Cafe",
    "hentaifoundry"  : "Hentai Foundry",
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
}

SUBCATEGORY_MAP = {
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
    "search" : "Search Results",
    "status" : "Images from Statuses",
    "tag"    : "Tag-Searches",
    "user"   : "Images from Users",
    "work"   : "Individual Images",
    "related-pin"  : "related Pins",
    "related-board": "",
}

AUTH_MAP = {
    "batoto"     : "Optional",
    "deviantart" : "Optional (OAuth)",
    "exhentai"   : "Optional",
    "flickr"     : "Optional (OAuth)",
    "idolcomplex": "Optional",
    "nijie"      : "Required",
    "pixiv"      : "Required",
    "reddit"     : "Optional (OAuth)",
    "sankaku"    : "Optional",
    "seiga"      : "Required",
    "smugmug"    : "Optional (OAuth)",
    "tumblr"     : "Optional (OAuth)",
}

IGNORE_LIST = (
    "oauth",
)


class RstColumn():

    def __init__(self, title, data, size=None):
        self.title = title
        self.data = self._transform(data)
        if not size:
            self.size = max(len(value) for value in data + [title])
        else:
            self.size = size

        self.title = self._pad(self.title)
        for i, value in enumerate(self.data):
            self.data[i] = self._pad(value)

    def __str__(self):
        return self.title

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key] if key < len(self.data) else [""]

    def _transform(self, data):
        return [
            value if isinstance(value, str) else ", ".join(value)
            for value in data
        ]

    def _pad(self, s):
        if len(s) <= self.size:
            return s + " " * (self.size - len(s))
        else:
            return substitute(s, self.size)


class RstTable():

    def __init__(self, columns):
        self.columns = columns
        self.rowcount = max(len(col) for col in columns)
        self.sep = " ".join("=" * col.size for col in columns)

    def __iter__(self):
        yield self.sep
        yield " ".join(col.title for col in self.columns)
        yield self.sep
        for i in range(self.rowcount):
            yield self._format_row(i)
        yield self.sep

    def _format_row(self, row):
        return " ".join(col[row] for col in self.columns)


_subs = []


def substitute(value, size):
    sub = "|{}-{}|".format(value[:15], len(_subs))
    _subs.append((value, sub))
    return sub + " " * (size - len(sub))


def build_list():
    extractors = []
    classes = []
    last = None

    for extr in gallery_dl.extractor.extractors():
        if extr.category in IGNORE_LIST:
            continue
        if extr.category == last or not last:
            classes.append(extr)
        elif last:
            if classes[0].subcategory:
                extractors.append(classes)
            classes = [extr]
        last = extr.category
    extractors.append(classes)

    for extrlist in extractors:
        extrlist.sort(key=subcategory_key)
        for extr in extrlist:
            extr.cat = map_category(extr.category)
            extr.subcat = map_subcategory(extr.subcategory)
    extractors.sort(key=category_key)

    return extractors


def get_domain(classes):
    try:
        cls = classes[0]
        url = sys.modules[cls.__module__].__doc__.split()[-1]
        if url.startswith("http"):
            return url
        scheme = "https" if hasattr(cls, "https") and cls.https else "http"
        host = cls.__doc__.split()[-1]
        return scheme + "://" + host + "/"
    except (IndexError, AttributeError):
        pass
    return ""


def map_category(c):
    return CATEGORY_MAP.get(c, c.capitalize())


def map_subcategory(sc):
    if sc in SUBCATEGORY_MAP:
        return SUBCATEGORY_MAP[sc]
    sc = sc.capitalize()
    return sc if sc.endswith("s") else sc + "s"


def category_key(extrlist):
    key = extrlist[0].cat.lower()
    if len(extrlist) == 1 and extrlist[0].__module__.endswith(".imagehosts"):
        key = "zz" + key
    return key


def subcategory_key(cls):
    if cls.subcategory in ("user", "issue"):
        return "A"
    return cls.subcategory


extractors = build_list()
columns = [
    RstColumn("Site", [
        extrlist[0].cat
        for extrlist in extractors
    ], 20),
    RstColumn("URL", [
        get_domain(extrlist)
        for extrlist in extractors
    ], 35),
    RstColumn("Capabilities", [
        ", ".join(extr.subcat for extr in extrlist if extr.subcat)
        for extrlist in extractors
    ], 50),
    RstColumn("Authentication", [
        AUTH_MAP.get(extrlist[0].category, "")
        for extrlist in extractors
    ]),
]

outfile = sys.argv[1] if len(sys.argv) > 1 else "supportedsites.rst"
with open(os.path.join(ROOTDIR, "docs", outfile), "w") as file:
    file.write("Supported Sites\n"
               "===============\n")
    for line in RstTable(columns):
        file.write(line.rstrip() + "\n")
    file.write("\n")
    for val, sub in _subs:
        file.write(".. {} replace:: {}\n".format(sub, val))
