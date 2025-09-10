# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Exception classes used by gallery-dl

Class Hierarchy:

Exception
 └── GalleryDLException
      ├── ExtractionError
      │    ├── HttpError
      │    │    └── ChallengeError
      │    ├── AuthorizationError
      │    │    └── AuthRequired
      │    ├── AuthenticationError
      │    └── NotFoundError
      ├── InputError
      │    ├── FormatError
      │    │    ├── FilenameFormatError
      │    │    └── DirectoryFormatError
      │    ├── FilterError
      │    ├── InputFileError
      │    └── NoExtractorError
      └── ControlException
           ├── StopExtraction
           ├── AbortExtraction
           ├── TerminateExtraction
           └── RestartExtraction
"""


class GalleryDLException(Exception):
    """Base class for GalleryDL exceptions"""
    default = None
    msgfmt = None
    code = 1

    def __init__(self, message=None, fmt=True):
        if not message:
            message = self.default
        elif isinstance(message, Exception):
            message = f"{message.__class__.__name__}: {message}"
        if fmt and self.msgfmt is not None:
            message = self.msgfmt.replace("{}", message)
        self.message = message
        Exception.__init__(self, message)


###############################################################################
# Extractor Errors ############################################################

class ExtractionError(GalleryDLException):
    """Base class for exceptions during information extraction"""
    code = 4


class HttpError(ExtractionError):
    """HTTP request during data extraction failed"""
    default = "HTTP request failed"

    def __init__(self, message="", response=None):
        self.response = response
        if response is None:
            self.status = 0
        else:
            self.status = response.status_code
            if not message:
                message = (f"'{response.status_code} {response.reason}' "
                           f"for '{response.url}'")
        ExtractionError.__init__(self, message)


class ChallengeError(HttpError):
    code = 8

    def __init__(self, challenge, response):
        message = (
            f"{challenge} ({response.status_code} {response.reason}) "
            f"for '{response.url}'")
        HttpError.__init__(self, message, response)


class AuthenticationError(ExtractionError):
    """Invalid or missing login credentials"""
    default = "Invalid login credentials"
    code = 16


class AuthorizationError(ExtractionError):
    """Insufficient privileges to access a resource"""
    default = "Insufficient privileges to access this resource"
    code = 16


class AuthRequired(AuthorizationError):
    default = "Account credentials required"

    def __init__(self, auth=None, resource="resource", message=None):
        if auth:
            if not isinstance(auth, str):
                auth = " or ".join(auth)

            if resource:
                if " " not in resource:
                    resource = f"this {resource}"
                resource = f" to access {resource}"
            else:
                resource = ""

            message = f" ('{message}')" if message else ""
            message = f"{auth} needed{resource}{message}"
        AuthorizationError.__init__(self, message)


class NotFoundError(ExtractionError):
    """Requested resource (gallery/image) could not be found"""
    msgfmt = "Requested {} could not be found"
    default = "resource (gallery/image)"


###############################################################################
# User Input ##################################################################

class InputError(GalleryDLException):
    """Error caused by user input and config options"""
    code = 32


class FormatError(InputError):
    """Error while building output paths"""


class FilenameFormatError(FormatError):
    """Error while building output filenames"""
    msgfmt = "Applying filename format string failed ({})"


class DirectoryFormatError(FormatError):
    """Error while building output directory paths"""
    msgfmt = "Applying directory format string failed ({})"


class FilterError(InputError):
    """Error while evaluating a filter expression"""
    msgfmt = "Evaluating filter expression failed ({})"


class InputFileError(InputError):
    """Error when parsing an input file"""


class NoExtractorError(InputError):
    """No extractor can handle the given URL"""


###############################################################################
# Control Flow ################################################################

class ControlException(GalleryDLException):
    code = 0


class StopExtraction(ControlException):
    """Stop data extraction"""

    def __init__(self, target=None):
        ControlException.__init__(self)

        if target is None:
            self.target = None
            self.depth = 1
        elif isinstance(target, int):
            self.target = None
            self.depth = target
        elif target.isdecimal():
            self.target = None
            self.depth = int(target)
        else:
            self.target = target
            self.depth = 128


class AbortExtraction(ExtractionError, ControlException):
    """Abort data extraction due to an error"""


class TerminateExtraction(ControlException):
    """Terminate data extraction"""


class RestartExtraction(ControlException):
    """Restart data extraction"""
