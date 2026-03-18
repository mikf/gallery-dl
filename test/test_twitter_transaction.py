#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from gallery_dl.extractor.utils.twitter_transaction_id import (
    ClientTransaction,
)


class TestTwitterTransaction(unittest.TestCase):

    def setUp(self):
        self.transaction = ClientTransaction()

    def test_extract_ondemand_s_url_legacy(self):
        homepage = '<script>"ondemand.s":"abc123"</script>'

        self.assertEqual(
            self.transaction._extract_ondemand_s_url(homepage),
            "https://abs.twimg.com/responsive-web/client-web/"
            "ondemand.s.abc123a.js",
        )

    def test_extract_ondemand_s_url_runtime_map(self):
        homepage = (
            '20113:"ondemand.s",20554:"ondemand.DirectMessagesCrypto"'
            '}[e]||e)+"."+{20113:"2507f89",20554:"d2e45cf"}[e]+"a.js"'
        )

        self.assertEqual(
            self.transaction._extract_ondemand_s_url(homepage),
            "https://abs.twimg.com/responsive-web/client-web/"
            "ondemand.s.2507f89a.js",
        )

    def test_extract_ondemand_s_url_missing(self):
        self.assertIsNone(
            self.transaction._extract_ondemand_s_url("<html></html>"))


if __name__ == "__main__":
    unittest.main()
