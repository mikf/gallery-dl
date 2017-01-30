# -*- coding: utf-8 -*-

# Copyright 2015, 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.


class NoExtractorError(Exception):
    """No extractor can handle the given URL"""


class AuthenticationError(Exception):
    """Invalid or missing login information"""


class AuthorizationError(Exception):
    """Insufficient privileges to access a resource"""


class NotFoundError(Exception):
    """Requested resource (gallery/image) does not exist"""
