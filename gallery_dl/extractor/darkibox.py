# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://darkibox.com/"""

from .common import Extractor, Message
from .. import text
import re

BASE_PATTERN = r"(?:https?://)?(?:www\.)?darkibox\.com"


class DarkiboxExtractor(Extractor):
    """Base class for darkibox extractors"""
    category = "darkibox"
    root = "https://darkibox.com"

    def _api_request(self, endpoint, params):
        api_key = self.config("api-key")
        if api_key:
            params["key"] = api_key
        url = self.root + "/api/" + endpoint
        data = self.request_json(url, params=params)
        if data.get("status") != 200:
            msg = data.get("msg", "unknown error")
            raise self.exc.StopExtraction(msg)
        return data.get("result")

    def _file_info_api(self, file_code):
        result = self._api_request("file/info", {
            "file_code": file_code,
        })
        if isinstance(result, list) and result:
            return result[0]
        return result

    def _direct_link_api(self, file_code):
        result = self._api_request("file/direct_link", {
            "file_code": file_code,
        })
        versions = result.get("versions", [])
        if versions:
            # prefer original quality
            for v in versions:
                if v.get("name") == "o":
                    return v["url"]
            return versions[0]["url"]
        return None

    def _scrape_download_url(self, file_code):
        """Fallback: scrape download URL without API key"""
        url = self.root + "/dl"
        data = {
            "op": "embed",
            "file_code": file_code,
            "auto": "1",
        }
        headers = {
            "Referer": "{}/embed-{}.html".format(self.root, file_code),
            "Origin": self.root,
        }
        resp = self.request(url, method="POST", data=data, headers=headers)
        return self._unpack_url(resp.text)

    @staticmethod
    def _unpack_url(html):
        """Extract video URL from packed JavaScript response"""
        # find eval(function(p,a,c,k,e,d) packed code
        match = re.search(
            r"eval\(function\(p,a,c,k,e,d\)\{.*?\}\('(.*?)',"
            r"(\d+),(\d+),'(.*?)'\.split",
            html, re.DOTALL,
        )
        if match:
            payload, radix, count, keywords = match.groups()
            radix = int(radix)
            count = int(count)
            words = keywords.split("|")

            def base_repr(num, base):
                digits = ("0123456789abcdefghijklmnopqrstuvwxyz"
                          "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                if num == 0:
                    return "0"
                result = ""
                while num:
                    result = digits[num % base] + result
                    num //= base
                return result

            def replacer(m):
                word = m.group(0)
                idx = int(word, 36) if radix <= 36 else int(word, 62)
                if idx < len(words) and words[idx]:
                    return words[idx]
                return word

            unpacked = re.sub(r"\b\w+\b", replacer, payload)
            # extract URL from unpacked JS
            url_match = re.search(r'sources:\s*\[\{file:\s*"([^"]+)"', unpacked)
            if not url_match:
                url_match = re.search(r'src:\s*"(https?://[^"]+)"', unpacked)
            if not url_match:
                url_match = re.search(r'"(https?://[^"]*\.m3u8[^"]*)"', unpacked)
            if not url_match:
                url_match = re.search(r'"(https?://[^"]*\.mp4[^"]*)"', unpacked)
            if url_match:
                return url_match.group(1)

        # fallback: direct URL search in html
        match = re.search(
            r'sources:\s*\[\{file:\s*"(https?://[^"]+)"', html)
        if not match:
            match = re.search(r'"(https?://[^"]*\.m3u8[^"]*)"', html)
        if not match:
            match = re.search(r'"(https?://[^"]*\.mp4[^"]*)"', html)
        if match:
            return match.group(1)
        return None


class DarkiboxFileExtractor(DarkiboxExtractor):
    """Extractor for darkibox files"""
    subcategory = "file"
    archive_fmt = "{file_code}"
    filename_fmt = "{file_name}.{extension}"
    pattern = (BASE_PATTERN +
               r"/(?:embed-)?([a-zA-Z0-9]+)(?:\.html)?/?$")
    example = "https://darkibox.com/FILECODE"

    def items(self):
        file_code = self.groups[0]
        api_key = self.config("api-key")

        file = {"file_code": file_code}

        if api_key:
            info = self._file_info_api(file_code)
            if info:
                file.update({
                    "file_name" : info.get("file_title") or
                                  info.get("file_name", file_code),
                    "file_size" : info.get("file_size"),
                    "file_length": info.get("file_length"),
                })
            download_url = self._direct_link_api(file_code)
        else:
            # scrape metadata from embed page
            embed_url = "{}/embed-{}.html".format(self.root, file_code)
            page = self.request(embed_url).text
            title = text.extr(page, "<title>", "</title>")
            if title:
                title = title.strip()
                # titles often have " - darkibox" suffix
                if " - " in title:
                    title = title.rsplit(" - ", 1)[0].strip()
            file["file_name"] = title or file_code
            download_url = self._scrape_download_url(file_code)

        if not download_url:
            raise self.exc.StopExtraction(
                "Unable to get download URL for '%s'", file_code)

        if "file_name" not in file:
            file["file_name"] = file_code

        text.nameext_from_url(download_url, file)
        if not file.get("extension"):
            file["extension"] = "mp4"

        yield Message.Directory, "", file
        yield Message.Url, download_url, file
