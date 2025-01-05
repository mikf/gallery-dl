# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""noop extractor"""

from .common import Extractor, Message


class NoopExtractor(Extractor):
    category = "noop"
    pattern = r"(?i)noo?p$"
    example = "noop"

    def items(self):
        # yield *something* to prevent a 'No results' message
        yield Message.Version, 1

        # Save cookies manually, since it happens automatically only after
        # extended extractor initialization, i.e. Message.Directory, which
        # itself might cause some unintended effects.
        if self.cookies:
            self.cookies_store()
