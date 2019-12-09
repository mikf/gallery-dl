# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.


class Message():
    """Enum for message identifiers

    Extractors yield their results as message-tuples, where the first element
    is one of the following identifiers. This message-identifier determines
    the type and meaning of the other elements in such a tuple.

    - Message.Version:
      - Message protocol version (currently always '1')
      - 2nd element specifies the version of all following messages as integer

    - Message.Directory:
      - Sets the target directory for all following images
      - 2nd element is a dictionary containing general metadata

    - Message.Url:
      - Image URL and its metadata
      - 2nd element is the URL as a string
      - 3rd element is a dictionary with image-specific metadata

    - Message.Headers:  # obsolete
      - HTTP headers to use while downloading
      - 2nd element is a dictionary with header-name and -value pairs

    - Message.Cookies:  # obsolete
      - Cookies to use while downloading
      - 2nd element is a dictionary with cookie-name and -value pairs

    - Message.Queue:
      - (External) URL that should be handled by another extractor
      - 2nd element is the (external) URL as a string
      - 3rd element is a dictionary containing URL-specific metadata

    - Message.Urllist:
      - Same as Message.Url, but its 2nd element is a list of multiple URLs
      - The additional URLs serve as a fallback if the primary one fails
    """

    Version = 1
    Directory = 2
    Url = 3
    #  Headers = 4
    #  Cookies = 5
    Queue = 6
    Urllist = 7
    Metadata = 8
