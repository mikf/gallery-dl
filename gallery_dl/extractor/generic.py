# -*- coding: utf-8 -*-

"""Extractor for images in a generic web page"""

from .common import Extractor, Message
from .. import text
import re
import os.path


class GenericExtractor(Extractor):
    """Extractor for images in a generic web page"""
    category = "generic"
    directory_fmt = ("{pageurl}",)
    filename_fmt = "{filename}.{extension}"
    archive_fmt = filename_fmt

    # Allow any url, optionally prefixed by "g:" or "generic:"
    # in case we want to override other extractors.
    # Based on: https://tools.ietf.org/html/rfc3986#appendix-B
    pattern = r"""(?ix)
            (?P<generic>g(?:eneric)?:)?     # optional "g(eneric):" prefix
            (?P<scheme>https?://)           # required http or https scheme
            (?P<domain>[^/?&#]+)            # required domain
            (?P<path>/[^?&#]*)?             # optional path
            (?:\?(?P<query>[^/?#]*))?       # optional query
            (?:\#(?P<fragment>.*))?$        # optional fragment
            """


    def __init__(self, match):

        Extractor.__init__(self, match)

        # Allow optional "g(eneric):" prefix and warn about "forced" or "fall-back" mode
        if match.group(0).startswith('g'):
            self.url = match.group(0).partition(":")[2]
            self.log.warning("Forcing use of generic information extractor.")
        else:
            self.url = match.group(0)
            self.log.warning("Falling back on generic information extractor.")

        # Used to resolve relative image urls
        self.root = match.group('scheme') + match.group('domain')


    def items(self):
        """Get page, extract metadata & images, yield them in suitable messages

        Adapted from common.GalleryExtractor.items()

        """

        page = self.request(self.url).text
        data = self.metadata(page)
        imgs = self.images(page)

        try:
            data["count"] = len(imgs)
        except TypeError:
            pass
        images = enumerate(imgs, 1)

        yield Message.Version, 1
        yield Message.Directory, data

        for data["num"], (url, imgdata) in images:
            if imgdata:
                data.update(imgdata)
                if "extension" not in imgdata:
                    text.nameext_from_url(url, data)
            else:
                text.nameext_from_url(url, data)
            yield Message.Url, url, data


    def metadata(self, page):
        """Extract generic webpage metadata, return them in a dict"""

        data = {}

        data['pageurl'] = self.url
        data['title'] = text.extract(page, '<title>', "</title>")[0] or ""
        data['descr'] = text.extract(page, '<meta name="description" content="', '"')[0] or ""
        data['keywords'] = text.extract(page, '<meta name="keywords" content="', '"')[0] or ""
        data['language'] = text.extract(page, '<meta name="language" content="', '"')[0] or ""
        data['name'] = text.extract(page, '<meta itemprop="name" content="', '"')[0] or ""
        data['copyright'] = text.extract(page, '<meta name="copyright" content="', '"')[0] or ""
        data['og_site'] = text.extract(page, '<meta property="og:site" content="', '"')[0] or ""
        data['og_site_name'] = text.extract(page, '<meta property="og:site_name" content="', '"')[0] or ""
        data['og_title'] = text.extract(page, '<meta property="og:title" content="', '"')[0] or ""
        data['og_descr'] = text.extract(page, '<meta property="og:description" content="', '"')[0] or ""

        data = { k: text.unescape(data[k]) for k in data if data[k] != "" }

        return data


    def images(self, page):
        """Extract image urls, return them in a list of (image url, metadata) tuples

        The extractor aims at finding as many _likely_ image urls as possible, using two
        overlapping strategies (duplicate urls will be removed later in the process).

        Note: since we are using re.findall() (see below), it's essential that the following
        patterns contain 0 or at most 1 capturing group, so that re.findall() return a list
        of urls (instead of a list of tuples of matching groups). All other groups used in
        the pattern should be non-capturing (?:...).
        """

        """ Strategy 1: look for any urls in src/srcset attributes of img/video/source elements

        See:
        https://www.w3schools.com/tags/att_src.asp
        https://www.w3schools.com/tags/att_source_srcset.asp

        We allow both absolute and relative urls here.

        Note that srcset attributes often contain multiple space separated image urls;
        this pattern matches only the first url; remaining urls will be matched by the
        "Strategy 2" pattern below.
        """
        imageurl_pattern_src = r"""(?ix)
            <(?:img|video|source)\s.*?      # <img>, <video> or <source> elements
            src(?:set)?=["']?               # src or srcset attributes
            (?P<URL>[^"'\s>]+)              # url
            """


        """ Strategy 2: look anywhere for urls containing common image/video extensions

        The list of allowed extensions is borrowed from the directlink.py extractor;
        other could be added, see https://en.wikipedia.org/wiki/List_of_file_formats

        We don't allow relative urls here, i.e. generic strings containing an image filename
        (such as in <... alt="image.jpg">) because they often get resolved into non-existing
        absolute urls, leading to 404 errors that might confuse the user.

        Compared to the "pattern" class variable, here we must exclude also other
        special characters (\s,",',>), since we are looking for urls in html tags.

        Note that we use the x flag, so spaces and # must be backslash-quoted, unless they are
        in a character class ([]).
        """
        imageurl_pattern_ext = r"""(?ix)
            (?:https?://[^/?&#"'>\s]+)                              # scheme + domain
            (?:[^?&#"'>\s]+)                                        # path until dot+ext
            \.(?:jpe?g|jpe|png|gif|web[mp]|mp4|mkv|og[gmv]|opus)    # dot + image/video extensions
            (?:\?[^/?#"'>\s]*)?                                     # optional query
            (?:\#[^/?#"'>\s]*)?                                     # optional fragment
            """

        imageurls_src = re.findall(imageurl_pattern_src, page)
        imageurls_ext = re.findall(imageurl_pattern_ext, page)
        imageurls = imageurls_src + imageurls_ext

        # Resolve relative urls
        #
        # Some of the urls may be relative, so we resolve them prefixing them
        # either by the page root url (self.root) if the relative url starts with "/",
        # or by a proper "base" url if the relative url doesn't start with "/"

        # If the page contains a <base> element, use it as base url
        basematch = re.search(r"(?i)(?:<base\s.*?href=[\"']?)(?P<url>[^\"' >]+)", page)
        if basematch:
            self.baseurl = basematch.group('url')
        else:
            # Use self.url if it doesn't end with an extension
            if os.path.splitext(self.url)[1] == "":
                self.baseurl = self.url
            # Otherwise, strip the last part
            else:
                self.baseurl = os.path.dirname(self.url)

        # Really resolve relative urls
        absimageurls = []
        for u in imageurls:
            if u.startswith('http'):
                absimageurls.append(u)
            elif u.startswith('/'):
                absimageurls.append(self.root + '/' + u)
            else:
                absimageurls.append(self.baseurl + '/' + u)

        # Remove duplicates
        absimageurls = set(absimageurls)

        # Create the image metadata dict and add image url to it
        # (image filename and extension are added by items())
        images = [ (u, {'imageurl': u}) for u in absimageurls ]

        return images
