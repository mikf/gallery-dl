# -*- coding: utf-8 -*-

"""Extractor for images in a generic web page."""

from .common import Extractor, Message
from .. import config, text
import re
import os.path


class GenericExtractor(Extractor):
    """Extractor for images in a generic web page."""

    category = "generic"
    directory_fmt = ("{category}", "{pageurl}")
    archive_fmt = "{imageurl}"

    # By default, the generic extractor is disabled
    # and the "g(eneric):" prefix in url is required.
    # If the extractor is enabled, make the prefix optional
    pattern = r"(?ix)(?P<generic>g(?:eneric)?:)"
    if config.get(("extractor", "generic"), "enabled"):
        pattern += r"?"

    # The generic extractor pattern should match (almost) any valid url
    # Based on: https://tools.ietf.org/html/rfc3986#appendix-B
    pattern += r"""
        (?P<scheme>https?://)?          # optional http(s) scheme
        (?P<domain>[-\w\.]+)            # required domain
        (?P<path>/[^?#]*)?              # optional path
        (?:\?(?P<query>[^#]*))?         # optional query
        (?:\#(?P<fragment>.*))?         # optional fragment
        """

    def __init__(self, match):
        """Init."""
        Extractor.__init__(self, match)

        # Strip the "g(eneric):" prefix
        # and inform about "forced" or "fallback" mode
        if match.group('generic'):
            self.log.info("Forcing use of generic information extractor.")
            self.url = match.group(0).partition(":")[2]
        else:
            self.log.info("Falling back on generic information extractor.")
            self.url = match.group(0)

        # Make sure we have a scheme, or use https
        if match.group('scheme'):
            self.scheme = match.group('scheme')
        else:
            self.scheme = 'https://'
            self.url = self.scheme + self.url

        # Used to resolve relative image urls
        self.root = self.scheme + match.group('domain')

    def items(self):
        """Get page, extract metadata & images, yield them in suitable messages.

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
        """Extract generic webpage metadata, return them in a dict."""
        data = {}
        data['pageurl'] = self.url
        data['title'] = text.extract(page, '<title>', "</title>")[0] or ""
        data['description'] = text.extract(
            page, '<meta name="description" content="', '"')[0] or ""
        data['keywords'] = text.extract(
            page, '<meta name="keywords" content="', '"')[0] or ""
        data['language'] = text.extract(
            page, '<meta name="language" content="', '"')[0] or ""
        data['name'] = text.extract(
            page, '<meta itemprop="name" content="', '"')[0] or ""
        data['copyright'] = text.extract(
            page, '<meta name="copyright" content="', '"')[0] or ""
        data['og_site'] = text.extract(
            page, '<meta property="og:site" content="', '"')[0] or ""
        data['og_site_name'] = text.extract(
            page, '<meta property="og:site_name" content="', '"')[0] or ""
        data['og_title'] = text.extract(
            page, '<meta property="og:title" content="', '"')[0] or ""
        data['og_description'] = text.extract(
            page, '<meta property="og:description" content="', '"')[0] or ""

        data = {k: text.unescape(data[k]) for k in data if data[k] != ""}

        return data

    def images(self, page):
        """Extract image urls, return a list of (image url, metadata) tuples.

        The extractor aims at finding as many _likely_ image urls as possible,
        using two strategies (see below); since these often overlap, any
        duplicate urls will be removed at the end of the process.

        Note: since we are using re.findall() (see below), it's essential that
        the following patterns contain 0 or at most 1 capturing group, so that
        re.findall() return a list of urls (instead of a list of tuples of
        matching groups). All other groups used in the pattern should be
        non-capturing (?:...).

        1: Look in src/srcset attributes of img/video/source elements

        See:
        https://www.w3schools.com/tags/att_src.asp
        https://www.w3schools.com/tags/att_source_srcset.asp

        We allow both absolute and relative urls here.

        Note that srcset attributes often contain multiple space separated
        image urls; this pattern matches only the first url; remaining urls
        will be matched by the "imageurl_pattern_ext" pattern below.
        """
        imageurl_pattern_src = r"""(?ix)
            <(?:img|video|source)\s.*?      # <img>, <video> or <source>
            src(?:set)?=["']?               # src or srcset attributes
            (?P<URL>[^"'\s>]+)              # url
            """

        """
        2: Look anywhere for urls containing common image/video extensions

        The list of allowed extensions is borrowed from the directlink.py
        extractor; other could be added, see
        https://en.wikipedia.org/wiki/List_of_file_formats

        Compared to the "pattern" class variable, here we must exclude also
        other special characters (space, ", ', >), since we are looking for
        urls in html tags.
        """

        imageurl_pattern_ext = r"""(?ix)
            (?:[^?&#"'>\s]+)                    # anything until dot+extension
            \.(?:jpe?g|jpe|png|gif
                 |web[mp]|mp4|mkv|og[gmv]|opus) # dot + image/video extensions
            (?:[^"'>\s]*)?                      # optional query and fragment
            """

        imageurls_src = re.findall(imageurl_pattern_src, page)
        imageurls_ext = re.findall(imageurl_pattern_ext, page)
        imageurls = imageurls_src + imageurls_ext

        # Resolve relative urls
        #
        # Image urls catched so far may be relative, so we must resolve them
        # by prepending a suitable base url.
        #
        # If the page contains a <base> element, use it as base url
        basematch = re.search(
            r"(?i)(?:<base\s.*?href=[\"']?)(?P<url>[^\"' >]+)", page)
        if basematch:
            self.baseurl = basematch.group('url').rstrip('/')
        # Otherwise, extract the base url from self.url
        else:
            if self.url.endswith("/"):
                self.baseurl = self.url.rstrip('/')
            else:
                self.baseurl = os.path.dirname(self.url)

        # Build the list of absolute image urls
        absimageurls = []
        for u in imageurls:
            # Absolute urls are taken as-is
            if u.startswith('http'):
                absimageurls.append(u)
            # // relative urls are prefixed with current scheme
            elif u.startswith('//'):
                absimageurls.append(self.scheme + u.lstrip('/'))
            # / relative urls are prefixed with current scheme+domain
            elif u.startswith('/'):
                absimageurls.append(self.root + u)
            # other relative urls are prefixed with baseurl
            else:
                absimageurls.append(self.baseurl + '/' + u)

        # Remove duplicates
        absimageurls = set(absimageurls)

        # Create the image metadata dict and add imageurl to it
        # (image filename and extension are added by items())
        images = [(u, {'imageurl': u}) for u in absimageurls]

        return images
