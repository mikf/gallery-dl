# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Exception classes used by gallery-dl

Class Hierarchy:

Exception
 +-- GalleryDLException
      +-- ExtractionError
      |    +-- AuthenticationError
      |    +-- AuthorizationError
      |    +-- NotFoundError
      |    +-- HttpError
      +-- FormatError
      |    +-- FilenameFormatError
      |    +-- DirectoryFormatError
      +-- FilterError
      +-- NoExtractorError
      +-- StopExtraction
"""


class GalleryDLException(Exception):
    """Base class for GalleryDL exceptions"""
    default = None
    msgfmt = None
    code = 1

    def __init__(self, message=None):
        if not message:
            message = self.default
        elif isinstance(message, Exception):
            message = "{}: {}".format(message.__class__.__name__, message)
        if self.msgfmt:
            message = self.msgfmt.format(message)
        Exception.__init__(self, message)


class ExtractionError(GalleryDLException):
    """Base class for exceptions during information extraction"""


class HttpError(ExtractionError):
    """HTTP request during data extraction failed"""
    default = "HTTP request failed"
    code = 4

    def __init__(self, message, response=None):
        ExtractionError.__init__(self, message)
        self.response = response
        self.status = response.status_code if response else 0


class NotFoundError(ExtractionError):
    """Requested resource (gallery/image) could not be found"""
    msgfmt = "Requested {} could not be found"
    default = "resource (gallery/image)"
    code = 8


class AuthenticationError(ExtractionError):
    """Invalid or missing login credentials"""
    default = "Invalid or missing login credentials"
    code = 16


class AuthorizationError(ExtractionError):
    """Insufficient privileges to access a resource"""
    default = "Insufficient privileges to access the specified resource"
    code = 16


class FormatError(GalleryDLException):
    """Error while building output paths"""
    code = 32


class FilenameFormatError(FormatError):
    """Error while building output filenames"""
    msgfmt = "Applying filename format string failed ({})"


class DirectoryFormatError(FormatError):
    """Error while building output directory paths"""
    msgfmt = "Applying directory format string failed ({})"


class FilterError(GalleryDLException):
    """Error while evaluating a filter expression"""
    msgfmt = "Evaluating filter expression failed ({})"
    code = 32


class NoExtractorError(GalleryDLException):
    """No extractor can handle the given URL"""
    code = 64


class StopExtraction(GalleryDLException):
    """Stop data extraction"""

    def __init__(self, message=None, *args):
        GalleryDLException.__init__(self)
        self.message = message % args if args else message
        self.code = 1 if message else 0
