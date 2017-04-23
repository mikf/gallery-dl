#!/usr/bin/env python

import sys
import os.path

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.realpath(ROOTDIR))
import gallery_dl.extractor


CATEGORY_MAP = {
    "deviantart"     : "DeviantArt",
    "dokireader"     : "Doki Reader",
    "dynastyscans"   : "Dynasty Reader",
    "e621"           : "e621",
    "exhentai"       : "ExHentai",
    "fallenangels"   : "Fallen Angels Scans",
    "gomanga"        : "GoManga",
    "hbrowse"        : "HBrowse",
    "hentai2read"    : "Hentai2Read",
    "hentaifoundry"  : "Hentai Foundry",
    "hentaihere"     : "HentaiHere",
    "hitomi"         : "Hitomi.la",
    "imagebam"       : "ImageBam",
    "imagefap"       : "ImageFap",
    "imgbox"         : "imgbox",
    "imgchili"       : "imgChili",
    "imgth"          : "imgth",
    "imgur"          : "imgur",
    "jaiminisbox"    : "Jaimini's Box",
    "kireicake"      : "Kirei Cake",
    "kisscomic"      : "KissComic",
    "kissmanga"      : "KissManga",
    "mangafox"       : "Manga Fox",
    "mangahere"      : "Manga Here",
    "mangapark"      : "MangaPark",
    "mangastream"    : "Manga Stream",
    "nhentai"        : "nhentai",
    "nijie"          : "nijie",
    "powermanga"     : "PowerManga",
    "readcomiconline": "Read Comic Online",
    "rule34"         : "Rule 34",
    "sankaku"        : "Sankaku Channel",
    "seaotterscans"  : "Sea Otter Scans",
    "seiga"          : "Niconico Seiga",
    "senmanga"       : "Sen Manga",
    "sensescans"     : "Sense-Scans",
    "spectrumnexus"  : "Spectrum Nexus",
    "worldthree"     : "World Three",
    "yomanga"        : "YoManga",
    "yonkouprod"     : "Yonkou Productions",
}

SUBCATEGORY_MAP = {
    "account": "Images from Users",
    "gallery": "Galleries",
    "image"  : "individual Images",
    "issue"  : "Comic-Issues",
    "manga"  : "Manga",
    "pinit"  : "pin.it Links",
    "status" : "Images from Statuses",
    "tag"    : "Tag-Searches",
    "user"   : "Images from Users",
    "work"   : "Individual Images",
}


class RstColumn():

    def __init__(self, title, data):
        self.title = title
        self.data = self._transform(data)
        self.size = max(len(value) for value in data + [title])

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
        return s + " " * (self.size - len(s))


class RstTable():

    def __init__(self, columns):
        self.columns = columns
        self.rowcount = max(len(col) for col in columns)
        self.sep = "+" + "+".join("-" * col.size for col in columns) + "+"

    def __iter__(self):
        yield self.sep
        yield "|" + "|".join(col.title for col in self.columns) + "|"
        yield self.sep.replace("-", "=")
        for i in range(self.rowcount):
            yield self._format_row(i)
            yield self.sep

    def _format_row(self, row):
        return "|" + "|".join(col[row] for col in self.columns) + "|"


def build_list():
    extractors = []
    classes = []
    last = None

    for extr in gallery_dl.extractor.extractors():
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
            extr.category = map_category(extr.category)
            extr.subcat   = map_subcategory(extr.subcategory)
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
    return SUBCATEGORY_MAP.get(sc, sc.capitalize() + "s")


def category_key(extrlist):
    key = extrlist[0].category.lower()
    if len(extrlist) == 1 and extrlist[0].subcat == "individual Images":
        key = "zz" + key
    return key


def subcategory_key(cls):
    if cls.subcategory in ("user", "issue"):
        return "A"
    return cls.subcategory


extractors = build_list()
columns = [
    RstColumn("Site", [
        extrlist[0].category
        for extrlist in extractors
    ]),
    RstColumn("URL", [
        get_domain(extrlist)
        for extrlist in extractors
    ]),
    RstColumn("Capabilities", [
        ", ".join(extr.subcat for extr in extrlist)
        for extrlist in extractors
    ]),
]

outfile = sys.argv[1] if len(sys.argv) > 1 else "supportedsites.rst"
with open(os.path.join(ROOTDIR, outfile), "w") as file:
    file.write("Supported Sites\n"
               "===============\n")
    for line in RstTable(columns):
        file.write(line + "\n")
