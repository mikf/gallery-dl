# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Utility extractor to execute tests of other extractors"""

from .common import Extractor, Message
from .. import extractor, exception


class TestExtractor(Extractor):
    """Extractor to select and run the test URLs of other extractors

    Examples:
        - apply all test URLs of all pixiv extractors:
            test:pixiv

        - apply all test URLs of the PixivWorkExtractor:
            test:pixiv:work

        - apply only the first test URL of the PixivWorkExtractor:
            test:pixiv:work:0

        - apply all second test URLs of all pixiv extractors:
            test:pixiv:*:1
    """
    category = "test"
    pattern = [r"t(?:est)?:([^:]+)(?::([^:]*)(?::(\*|\d*))?)?$"]

    def __init__(self, match):
        Extractor.__init__(self)
        self.tcategory, self.tsubcategory, self.tindex = match.groups()

    def items(self):
        # get all extractor classes matching the category
        klasses = [
            klass for klass in extractor.extractors()
            if klass.category == self.tcategory
        ]

        # if a subcategory is given, find the respective class
        if self.tsubcategory and self.tsubcategory != "*":
            for klass in klasses:
                if klass.subcategory == self.tsubcategory:
                    klasses = (klass,)
                    break
            else:
                raise exception.NotFoundError("test")

        # if an index is given, only consider tests at this array position
        if self.tindex and self.tindex != "*":
            index = int(self.tindex)
            tests = [
                klass.test[index]
                for klass in klasses
                if len(klass.test) > index
            ]
        else:
            tests = [
                test
                for klass in klasses if hasattr(klass, "test")
                for test in klass.test
            ]

        if not tests:
            raise exception.NotFoundError("test")

        yield Message.Version, 1
        for test in tests:
            yield Message.Queue, test[0]
