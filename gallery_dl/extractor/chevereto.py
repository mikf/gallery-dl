# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Chevereto galleries"""

import base64
import re
from .common import BaseExtractor, Message
from .. import text
from bs4 import BeautifulSoup

def decryptSimp(encrypted_b64):
    # Check if the input is already a valid URL
    if re.match(r'^https?://', encrypted_b64):
        print(encrypted_b64)
        return encrypted_b64

    key = b'seltilovessimpcity@simpcityhatesscrapers'  # Ensure the key is in bytes

    # Step 1: Decode the base64 string to get the hex string
    hex_string = base64.b64decode(encrypted_b64).decode('utf-8')

    # Step 2: Convert the hex string to a regular byte string
    try:
        encrypted_bytes = bytes.fromhex(hex_string)
    except ValueError:
        raise ValueError("The decoded base64 string is not a valid hex string.")

    # Step 3: Perform XOR decryption on the byte string
    decrypted_bytes = bytes([encrypted_bytes[i] ^ key[i % len(key)] for i in range(len(encrypted_bytes))])

    # Step 4: Convert the decrypted byte string to a regular string
    decrypted_str = decrypted_bytes.decode('utf-8')

    print(decrypted_str)
    return decrypted_str

class CheveretoExtractor(BaseExtractor):
    """Base class for chevereto extractors"""
    basecategory = "chevereto"
    directory_fmt = ("{category}", "{user}", "{album}",)
    archive_fmt = "{id}"

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        self.path = match.group(match.lastindex)

    def _pagination(self, url):
        while url:
            print(url)
            page = self.request(url).text

            for item in text.extract_iter(
                    page, '<div class="list-item-image ', 'image-container'):
                yield text.extr(item, '<a href="', '"')

            url = text.extr(page, '<a data-pagination="next" href="', '" ><')
            print(url)


BASE_PATTERN = CheveretoExtractor.update({
    "jpgfish": {
        "root": "https://jpg5.su",
        "pattern": r"jpe?g\d?\.(?:su|pet|fish(?:ing)?|church)",
    },
    "imgkiwi": {
        "root": "https://img.kiwi",
        "pattern": r"img\.kiwi",
    },
})


class CheveretoImageExtractor(CheveretoExtractor):
    """Extractor for chevereto Images"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"(/im(?:g|age)/[^/?#]+)"
    example = "https://jpg2.su/img/TITLE.ID"

    def items(self):
        url = decryptSimp(self.root + self.path)
        print(url)
        txt = self.request(url).text
        extr = text.extract_from(txt)
        # Parse the HTML content
        soup = BeautifulSoup(txt, 'html.parser')

        # Find the <a> tag with the specified class
        a_tag = soup.find('a', class_='btn btn-download default')
        picurl=""
        # Extract the href attribute
        if a_tag and 'href' in a_tag.attrs:
            picurl = a_tag['href']
            print("Extracted href:", picurl)
            picurl = decryptSimp(picurl)
            print("Decrypted href:", picurl)
        else:
            print("No href found or the class does not match.")

        image = {
            "id"   : self.path.rpartition(".")[2],
            "url"  : picurl,
            "album": text.extr(extr("Added to <a", "/a>"), ">", "<"),
            "user" : extr('username: "', '"'),
        }
        print(image["url"])

        text.nameext_from_url(image["url"], image)
        yield Message.Directory, image
        yield Message.Url, image["url"], image


class CheveretoAlbumExtractor(CheveretoExtractor):
    """Extractor for chevereto Albums"""
    subcategory = "album"
    pattern = BASE_PATTERN + r"(/a(?:lbum)?/[^/?#]+(?:/sub)?)"
    example = "https://jpg2.su/album/TITLE.ID"

    def items(self):
        url = decryptSimp(self.root + self.path)
        print(url)
        data = {"_extractor": CheveretoImageExtractor}

        if self.path.endswith("/sub"):
            albums = self._pagination(url)
        else:
            albums = (url,)

        for album in albums:
            for image in self._pagination(album):
                yield Message.Queue, image, data


class CheveretoUserExtractor(CheveretoExtractor):
    """Extractor for chevereto Users"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"(/(?!img|image|a(?:lbum)?)[^/?#]+(?:/albums)?)"
    example = "https://jpg2.su/USER"

    def items(self):
        url = decryptSimp(self.root + self.path)
        print(url)

        if self.path.endswith("/albums"):
            data = {"_extractor": CheveretoAlbumExtractor}
        else:
            data = {"_extractor": CheveretoImageExtractor}

        for url in self._pagination(url):
            yield Message.Queue, url, data
