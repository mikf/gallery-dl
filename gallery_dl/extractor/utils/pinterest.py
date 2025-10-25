# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import text, util, exception


class PinterestAPI():
    """Minimal interface for the Pinterest Web API

    For a better and more complete implementation in PHP, see
    - https://github.com/seregazhuk/php-pinterest-bot
    """

    def __init__(self, extractor):
        csrf_token = util.generate_token()

        self.extractor = extractor
        self.root = extractor.root
        self.cookies = {"csrftoken": csrf_token}
        self.headers = {
            "Accept"                 : "application/json, text/javascript, "
                                       "*/*, q=0.01",
            "X-Requested-With"       : "XMLHttpRequest",
            "X-APP-VERSION"          : "a89153f",
            "X-Pinterest-AppState"   : "active",
            "X-Pinterest-Source-Url" : None,
            "X-Pinterest-PWS-Handler": "www/[username].js",
            "Alt-Used"               : "www.pinterest.com",
            "Connection"             : "keep-alive",
            "Cookie"                 : None,
            "Sec-Fetch-Dest"         : "empty",
            "Sec-Fetch-Mode"         : "cors",
            "Sec-Fetch-Site"         : "same-origin",
        }

    def pin(self, pin_id):
        """Query information about a pin"""
        options = {"id": pin_id, "field_set_key": "detailed"}
        return self._call("Pin", options)["resource_response"]["data"]

    def pin_related(self, pin_id):
        """Yield related pins of another pin"""
        options = {"pin": pin_id, "add_vase": True, "pins_only": True}
        return self._pagination("RelatedPinFeed", options)

    def board(self, user, board_name):
        """Query information about a board"""
        options = {"slug": board_name, "username": user,
                   "field_set_key": "detailed"}
        return self._call("Board", options)["resource_response"]["data"]

    def boards(self, user):
        """Yield all boards from 'user'"""
        options = {
            "sort"            : "last_pinned_to",
            "field_set_key"   : "profile_grid_item",
            "filter_stories"  : False,
            "username"        : user,
            "page_size"       : 25,
            "include_archived": True,
        }
        return self._pagination("Boards", options)

    def board_pins(self, board_id):
        """Yield all pins of a specific board"""
        options = {
            "board_id": board_id,
            "field_set_key": "react_grid_pin",
            "prepend": False,
            "bookmarks": None,
        }
        return self._pagination("BoardFeed", options)

    def board_section(self, section_id):
        """Yield a specific board section"""
        options = {"section_id": section_id}
        return self._call("BoardSection", options)["resource_response"]["data"]

    def board_section_by_name(self, user, board_slug, section_slug):
        """Yield a board section by name"""
        options = {"board_slug": board_slug, "section_slug": section_slug,
                   "username": user}
        return self._call("BoardSection", options)["resource_response"]["data"]

    def board_sections(self, board_id):
        """Yield all sections of a specific board"""
        options = {"board_id": board_id}
        return self._pagination("BoardSections", options)

    def board_section_pins(self, section_id):
        """Yield all pins from a board section"""
        options = {"section_id": section_id}
        return self._pagination("BoardSectionPins", options)

    def board_content_recommendation(self, board_id):
        """Yield related pins of a specific board"""
        options = {"id": board_id, "type": "board", "add_vase": True}
        return self._pagination("BoardContentRecommendation", options)

    def user_pins(self, user):
        """Yield all pins from 'user'"""
        options = {
            "is_own_profile_pins": False,
            "username"           : user,
            "field_set_key"      : "grid_item",
            "pin_filter"         : None,
        }
        return self._pagination("UserPins", options)

    def user_activity_pins(self, user):
        """Yield pins created by 'user'"""
        options = {
            "exclude_add_pin_rep": True,
            "field_set_key"      : "grid_item",
            "is_own_profile_pins": False,
            "username"           : user,
        }
        return self._pagination("UserActivityPins", options)

    def search(self, query):
        """Yield pins from searches"""
        options = {"query": query, "scope": "pins", "rs": "typed"}
        return self._pagination("BaseSearch", options)

    def _call(self, resource, options):
        url = f"{self.root}/resource/{resource}Resource/get/"
        params = {
            "data"      : util.json_dumps({"options": options}),
            "source_url": "",
        }

        response = self.extractor.request(
            url, params=params, headers=self.headers,
            cookies=self.cookies, fatal=False)

        try:
            data = response.json()
        except ValueError:
            data = {}

        if response.history:
            self.root = text.root_from_url(response.url)
        if response.status_code < 400:
            return data
        if response.status_code == 404:
            resource = self.extractor.subcategory.rpartition("-")[2]
            raise exception.NotFoundError(resource)
        self.extractor.log.debug("Server response: %s", response.text)
        raise exception.AbortExtraction("API request failed")

    def _pagination(self, resource, options):
        while True:
            data = self._call(resource, options)
            results = data["resource_response"]["data"]
            if isinstance(results, dict):
                results = results["results"]
            yield from results

            try:
                bookmarks = data["resource"]["options"]["bookmarks"]
                if (not bookmarks or bookmarks[0] == "-end-" or
                        bookmarks[0].startswith("Y2JOb25lO")):
                    return
                options["bookmarks"] = bookmarks
            except KeyError:
                return
