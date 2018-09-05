# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
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
      +-- DownloadError
      |    +-- DownloadComplete
      |    +-- DownloadRetry
      +-- NoExtractorError
      +-- FormatError
      +-- FilterError
      +-- StopExtraction
"""


class GalleryDLException(Exception):
    """Base class for GalleryDL exceptions"""


class ExtractionError(GalleryDLException):
    """Base class for exceptions during information extraction"""


class AuthenticationError(ExtractionError):
    """Invalid or missing login information"""


class AuthorizationError(ExtractionError):
    """Insufficient privileges to access a resource"""


class NotFoundError(ExtractionError):
    """Requested resource (gallery/image) does not exist"""


class HttpError(ExtractionError):
    """HTTP request during extraction failed"""


class DownloadError(GalleryDLException):
    """Base class for exceptions during file downloads"""


class DownloadRetry(DownloadError):
    """Download attempt failed and should be retried"""


class DownloadComplete(DownloadError):
    """Output file of attempted download is already complete"""


class NoExtractorError(GalleryDLException):
    """No extractor can handle the given URL"""


class FormatError(GalleryDLException):
    """Error while building output path"""


class FilterError(GalleryDLException):
    """Error while evaluating a filter expression"""


class StopExtraction(GalleryDLException):
    """Extraction should stop"""
