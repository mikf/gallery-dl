# -*- coding: utf-8 -*-

from .common import Extractor, Message


class GofileFolderExtractor(Extractor):
    root = "https://gofile.io"
    pattern = r"(?:https?://)?(?:www\.)?gofile\.io/d/(\w+)"
    category = "gofile"
    subcategory = "folder"
    directory_fmt = ("{category}", "{folder_name} ({content_id})")

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.content_id = match.group(1)

    def _create_account(self):
        response = self.request("https://api.gofile.io/createAccount", method="GET")
        json_response = response.json()
        if json_response["status"] != "ok":
            raise Exception(f"Error creating account! Status: {json_response['status']}")
        return json_response["data"]["token"]

    def _get_content(self, token, content_id):
        response = self.request(f"https://api.gofile.io/getContent?contentId={content_id}"
                                f"&token={token}"
                                "&websiteToken=websiteToken", method="GET")
        json_response = response.json()
        if json_response["status"] != "ok":
            raise Exception(f"Error getting content! Status: {json_response['status']}")
        return json_response

    def items(self):

        token = self._create_account()
        self._update_cookies({"accountToken": token})
        content = self._get_content(token, self.content_id)
        folder_name = content["data"]["name"]
        data = {"folder_name": folder_name, "content_id": self.content_id}
        yield Message.Directory, data

        for file in content["data"]["contents"].values():
            name = file["name"]
            if file["type"] != "file":
                self.log.warning(f"Warning! Content {file['name']} is not a file!")
                continue
            link = file["link"]
            data["filename"], _, data["extension"] = name.rpartition(".")
            yield Message.Url, link, data
