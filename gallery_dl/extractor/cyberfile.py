# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://cyberfile.me/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?cyberfile\.me"


class CyberfileExtractor(Extractor):
    """Base class for cyberfile extractors"""
    category = "cyberfile"
    root = "https://cyberfile.me"

    def request_api(self, endpoint, data):
        url = f"{self.root}{endpoint}"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.root,
        }
        resp = self.request_json(
            url, method="POST", headers=headers, data=data)

        if "albumPasswordModel" in resp.get("javascript", ""):
            url_pw = f"{self.root}/ajax/folder_password_process"
            data_pw = {
                "folderPassword": self._get_auth_info(password=True)[1],
                "folderId": text.extr(
                    resp["html"], '<input type="hidden" value="', '"'),
                "submitme": "1",
            }
            resp = self.request_json(
                url_pw, method="POST", headers=headers, data=data_pw)
            if not resp.get("success"):
                raise exception.AuthorizationError(f"'{resp.get('msg')}'")
            resp = self.request_json(
                url, method="POST", headers=headers, data=data)

        return resp


class CyberfileFolderExtractor(CyberfileExtractor):
    subcategory = "folder"
    pattern = rf"{BASE_PATTERN}/folder/([0-9a-f]+)"
    example = "https://cyberfile.me/folder/0123456789abcdef/NAME"

    def items(self):
        folder_hash = self.groups[0]
        url = f"{self.root}/folder/{folder_hash}"
        folder_num = text.extr(self.request(url).text, "ages('folder', '", "'")

        extract_folders = text.re(r'sharing-url="([^"]+)').findall
        extract_files = text.re(r'dtfullurl="([^"]+)').findall
        recursive = self.config("recursive", True)
        perpage = 600

        data = {
            "pageType" : "folder",
            "nodeId"   : folder_num,
            "pageStart": 1,
            "perPage"  : perpage,
            "filterOrderBy": "",
        }
        resp = self.request_api("/account/ajax/load_files", data)
        html = resp["html"]

        folder = {
            "folder_hash": folder_hash,
            "folder_num" : text.parse_int(folder_num),
            "folder"     : resp["page_title"],
        }

        while True:
            folders = extract_folders(html)
            if recursive and folders:
                folder["_extractor"] = CyberfileFolderExtractor
                for url in folders:
                    yield Message.Queue, url, folder

            if files := extract_files(html):
                folder["_extractor"] = CyberfileFileExtractor
                for url in files:
                    yield Message.Queue, url, folder

            if len(folders) + len(files) < perpage:
                return
            data["pageStart"] += 1
            resp = self.request_api("/account/ajax/load_files", data)


class CyberfileSharedExtractor(CyberfileExtractor):
    subcategory = "shared"
    pattern = rf"{BASE_PATTERN}/shared/([a-zA-Z0-9]+)"
    example = "https://cyberfile.me/shared/AbCdEfGhIjK"

    def items(self):
        # get 'filehosting' cookie
        url = f"{self.root}/shared/{self.groups[0]}"
        self.request(url, method="HEAD")

        data = {
            "pageType" : "nonaccountshared",
            "nodeId"   : "",
            "pageStart": "1",
            "perPage"  : "500",
            "filterOrderBy": "",
        }
        resp = self.request_api("/account/ajax/load_files", data)

        html = resp["html"]
        pos = html.find("<!-- /.navbar-collapse -->") + 26

        data = {"_extractor": CyberfileFolderExtractor}
        for url in text.extract_iter(html, 'sharing-url="', '"', pos):
            yield Message.Queue, url, data

        data = {"_extractor": CyberfileFileExtractor}
        for url in text.extract_iter(html, 'dtfullurl="', '"', pos):
            yield Message.Queue, url, data


class CyberfileFileExtractor(CyberfileExtractor):
    subcategory = "file"
    directory_fmt = ("{category}", "{uploader}", "{folder}")
    pattern = rf"{BASE_PATTERN}/([a-zA-Z0-9]+)"
    example = "https://cyberfile.me/AbCdE"

    def items(self):
        file_id = self.groups[0]
        url = f"{self.root}/{file_id}"
        file_num = text.extr(self.request(url).text, "owFileInformation(", ")")

        data = {"u": file_num}
        resp = self.request_api("/account/ajax/file_details", data)
        extr = text.extract_from(resp["html"])
        info = text.split_html(extr('class="text-section">', "</span>"))
        folder = info[0] if len(info) > 1 else ""

        file = {
            "file_id" : file_id,
            "file_num": text.parse_int(file_num),
            "name"    : resp["page_title"],
            "folder"  : folder,
            "uploader": info[-1][2:].strip(),
            "size"    : text.parse_bytes(text.remove_html(extr(
                "Filesize:", "</tr>"))[:-1]),
            "tags"    : text.split_html(extr(
                "Keywords:", "</tr>")),
            "date"    : self.parse_datetime(text.remove_html(extr(
                "Uploaded:", "</tr>")), "%d/%m/%Y %H:%M:%S"),
            "permissions": text.remove_html(extr(
                "Permissions:", "</tr>")).split(" &amp; "),
        }

        file["file_url"] = url = extr("openUrl('", "'")
        text.nameext_from_url(file["name"] or url, file)
        yield Message.Directory, "", file
        yield Message.Url, url, file
