# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import text, util, exception
from ...cache import cache, memcache
import random


class TwitterAPI():
    client_transaction = None

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log

        self.root = "https://x.com/i/api"
        self._nsfw_warning = True
        self._json_dumps = util.json_dumps

        cookies = extractor.cookies
        cookies_domain = extractor.cookies_domain

        csrf = extractor.config("csrf")
        if csrf is None or csrf == "cookies":
            csrf_token = cookies.get("ct0", domain=cookies_domain)
        else:
            csrf_token = None
        if not csrf_token:
            csrf_token = util.generate_token()
            cookies.set("ct0", csrf_token, domain=cookies_domain)

        auth_token = cookies.get("auth_token", domain=cookies_domain)

        self.headers = {
            "Accept": "*/*",
            "Referer": extractor.root + "/",
            "content-type": "application/json",
            "x-guest-token": None,
            "x-twitter-auth-type": "OAuth2Session" if auth_token else None,
            "x-csrf-token": csrf_token,
            "x-twitter-client-language": "en",
            "x-twitter-active-user": "yes",
            "x-client-transaction-id": None,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejR"
                             "COuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu"
                             "4FA33AGWWjCpTnA",
        }
        self.params = {
            "include_profile_interstitial_type": "1",
            "include_blocking": "1",
            "include_blocked_by": "1",
            "include_followed_by": "1",
            "include_want_retweets": "1",
            "include_mute_edge": "1",
            "include_can_dm": "1",
            "include_can_media_tag": "1",
            "include_ext_has_nft_avatar": "1",
            "include_ext_is_blue_verified": "1",
            "include_ext_verified_type": "1",
            "skip_status": "1",
            "cards_platform": "Web-12",
            "include_cards": "1",
            "include_ext_alt_text": "true",
            "include_ext_limited_action_results": "false",
            "include_quote_count": "true",
            "include_reply_count": "1",
            "tweet_mode": "extended",
            "include_ext_collab_control": "true",
            "include_ext_views": "true",
            "include_entities": "true",
            "include_user_entities": "true",
            "include_ext_media_color": "true",
            "include_ext_media_availability": "true",
            "include_ext_sensitive_media_warning": "true",
            "include_ext_trusted_friends_metadata": "true",
            "send_error_codes": "true",
            "simple_quoted_tweet": "true",
            "q": None,
            "count": "100",
            "query_source": None,
            "cursor": None,
            "pc": None,
            "spelling_corrections": None,
            "include_ext_edit_control": "true",
            "ext": "mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,"
                   "enrichments,superFollowMetadata,unmentionInfo,editControl,"
                   "collab_control,vibe",
        }
        self.features = {
            "hidden_profile_subscriptions_enabled": True,
            "payments_enabled": False,
            "rweb_xchat_enabled": False,
            "profile_label_improvements_pcf_label_in_post_enabled": True,
            "rweb_tipjar_consumption_enabled": True,
            "verified_phone_label_enabled": False,
            "highlights_tweets_tab_ui_enabled": True,
            "responsive_web_twitter_article_notes_tab_enabled": True,
            "subscriptions_feature_can_gift_premium": True,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_"
            "skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
        }
        self.features_pagination = {
            "rweb_video_screen_enabled": False,
            "payments_enabled": False,
            "rweb_xchat_enabled": False,
            "profile_label_improvements_pcf_label_in_post_enabled": True,
            "rweb_tipjar_consumption_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql"
            "_timeline_navigation_enabled": True,
            "responsive_web_graphql"
            "_skip_user_profile_image_extensions_enabled": False,
            "premium_content_api_read_enabled": False,
            "communities_web_enable_tweet_community_results_fetch": True,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
            "responsive_web_grok_analyze_post_followups_enabled": True,
            "responsive_web_jetfuel_frame": True,
            "responsive_web_grok_share_attachment_enabled": True,
            "articles_preview_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "responsive_web_grok_show_grok_translated_post": False,
            "responsive_web_grok_analysis_button_from_backend": True,
            "creator_subscriptions_quote_tweet_preview_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results"
            "_prefer_gql_limited_actions_policy_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_grok_image_annotation_enabled": True,
            "responsive_web_grok_imagine_annotation_enabled": True,
            "responsive_web_grok"
            "_community_note_auto_translation_is_enabled": False,
            "responsive_web_enhance_cards_enabled": False,
        }

    def tweet_result_by_rest_id(self, tweet_id):
        endpoint = "/graphql/qxWQxcMLiTPcavz9Qy5hwQ/TweetResultByRestId"
        variables = {
            "tweetId": tweet_id,
            "withCommunity": False,
            "includePromotedContent": False,
            "withVoice": False,
        }
        features = self.features_pagination.copy()
        del features["rweb_video_screen_enabled"]
        field_toggles = {
            "withArticleRichContentState": True,
            "withArticlePlainText": False,
            "withGrokAnalyze": False,
            "withDisallowedReplyControls": False,
        }
        params = {
            "variables"   : self._json_dumps(variables),
            "features"    : self._json_dumps(features),
            "fieldToggles": self._json_dumps(field_toggles),
        }
        tweet = self._call(endpoint, params)["data"]["tweetResult"]["result"]
        if "tweet" in tweet:
            tweet = tweet["tweet"]

        if tweet.get("__typename") == "TweetUnavailable":
            reason = tweet.get("reason")
            if reason in ("NsfwViewerHasNoStatedAge", "NsfwLoggedOut"):
                raise exception.AuthRequired(message="NSFW Tweet")
            if reason == "Protected":
                raise exception.AuthRequired(message="Protected Tweet")
            raise exception.AbortExtraction(f"Tweet unavailable ('{reason}')")

        return tweet

    def tweet_detail(self, tweet_id):
        endpoint = "/graphql/iFEr5AcP121Og4wx9Yqo3w/TweetDetail"
        variables = {
            "focalTweetId": tweet_id,
            "referrer": "profile",
            "with_rux_injections": False,
            #  "rankingMode": "Relevance",
            "includePromotedContent": False,
            "withCommunity": True,
            "withQuickPromoteEligibilityTweetFields": False,
            "withBirdwatchNotes": True,
            "withVoice": True,
        }
        field_toggles = {
            "withArticleRichContentState": True,
            "withArticlePlainText": False,
            "withGrokAnalyze": False,
            "withDisallowedReplyControls": False,
        }
        return self._pagination_tweets(
            endpoint, variables,
            ("threaded_conversation_with_injections_v2",),
            field_toggles=field_toggles)

    def user_tweets(self, screen_name):
        endpoint = "/graphql/E8Wq-_jFSaU7hxVcuOPR9g/UserTweets"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
            "withQuickPromoteEligibilityTweetFields": False,
            "withVoice": True,
        }
        field_toggles = {
            "withArticlePlainText": False,
        }
        return self._pagination_tweets(
            endpoint, variables, field_toggles=field_toggles)

    def user_tweets_and_replies(self, screen_name):
        endpoint = "/graphql/-O3QOHrVn1aOm_cF5wyTCQ/UserTweetsAndReplies"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
            "withCommunity": True,
            "withVoice": True,
        }
        field_toggles = {
            "withArticlePlainText": False,
        }
        return self._pagination_tweets(
            endpoint, variables, field_toggles=field_toggles)

    def user_highlights(self, screen_name):
        endpoint = "/graphql/gmHw9geMTncZ7jeLLUUNOw/UserHighlightsTweets"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
            "withVoice": True,
        }
        field_toggles = {
            "withArticlePlainText": False,
        }
        return self._pagination_tweets(
            endpoint, variables, field_toggles=field_toggles)

    def user_media(self, screen_name):
        endpoint = "/graphql/jCRhbOzdgOHp6u9H4g2tEg/UserMedia"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
            "withClientEventToken": False,
            "withBirdwatchNotes": False,
            "withVoice": True,
        }
        field_toggles = {
            "withArticlePlainText": False,
        }
        return self._pagination_tweets(
            endpoint, variables, field_toggles=field_toggles)

    def user_likes(self, screen_name):
        endpoint = "/graphql/TGEKkJG_meudeaFcqaxM-Q/Likes"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
            "withClientEventToken": False,
            "withBirdwatchNotes": False,
            "withVoice": True,
        }
        field_toggles = {
            "withArticlePlainText": False,
        }
        return self._pagination_tweets(
            endpoint, variables, field_toggles=field_toggles)

    def user_bookmarks(self):
        endpoint = "/graphql/pLtjrO4ubNh996M_Cubwsg/Bookmarks"
        variables = {
            "count": 100,
            "includePromotedContent": False,
        }
        return self._pagination_tweets(
            endpoint, variables, ("bookmark_timeline_v2", "timeline"),
            stop_tweets=128)

    def search_timeline(self, query, product="Latest"):
        endpoint = "/graphql/4fpceYZ6-YQCx_JSl_Cn_A/SearchTimeline"
        variables = {
            "rawQuery": query,
            "count": self.extractor.config("search-limit", 20),
            "querySource": "typed_query",
            "product": product,
            "withGrokTranslatedBio": False,
        }

        if self.extractor.config("search-pagination") in (
                "max_id", "maxid", "id"):
            update_variables = self._update_variables_search
        else:
            update_variables = None

        stop_tweets = self.extractor.config("search-stop")
        if stop_tweets is None or stop_tweets == "auto":
            stop_tweets = 3 if update_variables is None else 0

        return self._pagination_tweets(
            endpoint, variables,
            ("search_by_raw_query", "search_timeline", "timeline"),
            stop_tweets=stop_tweets, update_variables=update_variables)

    def community_query(self, community_id):
        endpoint = "/graphql/2W09l7nD7ZbxGQHXvfB22w/CommunityQuery"
        params = {
            "variables": self._json_dumps({
                "communityId": community_id,
            }),
            "features": self._json_dumps({
                "c9s_list_members_action_api_enabled": False,
                "c9s_superc9s_indication_enabled": False,
            }),
        }
        return (self._call(endpoint, params)
                ["data"]["communityResults"]["result"])

    def community_tweets_timeline(self, community_id):
        endpoint = "/graphql/Nyt-88UX4-pPCImZNUl9RQ/CommunityTweetsTimeline"
        variables = {
            "communityId": community_id,
            "count": 100,
            "displayLocation": "Community",
            "rankingMode": "Recency",
            "withCommunity": True,
        }
        return self._pagination_tweets(
            endpoint, variables,
            ("communityResults", "result", "ranked_community_timeline",
             "timeline"))

    def community_media_timeline(self, community_id):
        endpoint = "/graphql/ZniZ7AAK_VVu1xtSx1V-gQ/CommunityMediaTimeline"
        variables = {
            "communityId": community_id,
            "count": 100,
            "withCommunity": True,
        }
        return self._pagination_tweets(
            endpoint, variables,
            ("communityResults", "result", "community_media_timeline",
             "timeline"))

    def communities_main_page_timeline(self, screen_name):
        endpoint = ("/graphql/p048a9n3hTPppQyK7FQTFw"
                    "/CommunitiesMainPageTimeline")
        variables = {
            "count": 100,
            "withCommunity": True,
        }
        return self._pagination_tweets(
            endpoint, variables,
            ("viewer", "communities_timeline", "timeline"))

    def home_timeline(self):
        endpoint = "/graphql/DXmgQYmIft1oLP6vMkJixw/HomeTimeline"
        variables = {
            "count": 100,
            "includePromotedContent": False,
            "latestControlAvailable": True,
            "withCommunity": True,
        }
        return self._pagination_tweets(
            endpoint, variables, ("home", "home_timeline_urt"))

    def home_latest_timeline(self):
        endpoint = "/graphql/SFxmNKWfN9ySJcXG_tjX8g/HomeLatestTimeline"
        variables = {
            "count": 100,
            "includePromotedContent": False,
            "latestControlAvailable": True,
        }
        return self._pagination_tweets(
            endpoint, variables, ("home", "home_timeline_urt"))

    def live_event_timeline(self, event_id):
        endpoint = f"/2/live_event/timeline/{event_id}.json"
        params = self.params.copy()
        params["timeline_id"] = "recap"
        params["urt"] = "true"
        params["get_annotations"] = "true"
        return self._pagination_legacy(endpoint, params)

    def live_event(self, event_id):
        endpoint = f"/1.1/live_event/1/{event_id}/timeline.json"
        params = self.params.copy()
        params["count"] = "0"
        params["urt"] = "true"
        return (self._call(endpoint, params)
                ["twitter_objects"]["live_events"][event_id])

    def list_latest_tweets_timeline(self, list_id):
        endpoint = "/graphql/06JtmwM8k_1cthpFZITVVA/ListLatestTweetsTimeline"
        variables = {
            "listId": list_id,
            "count": 100,
        }
        return self._pagination_tweets(
            endpoint, variables, ("list", "tweets_timeline", "timeline"))

    def list_members(self, list_id):
        endpoint = "/graphql/naea_MSad4pOb-D6_oVv_g/ListMembers"
        variables = {
            "listId": list_id,
            "count": 100,
        }
        return self._pagination_users(
            endpoint, variables, ("list", "members_timeline", "timeline"))

    def user_followers(self, screen_name):
        endpoint = "/graphql/i6PPdIMm1MO7CpAqjau7sw/Followers"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
            "withGrokTranslatedBio": False,
        }
        return self._pagination_users(endpoint, variables)

    def user_followers_verified(self, screen_name):
        endpoint = "/graphql/fxEl9kp1Tgolqkq8_Lo3sg/BlueVerifiedFollowers"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
            "withGrokTranslatedBio": False,
        }
        return self._pagination_users(endpoint, variables)

    def user_following(self, screen_name):
        endpoint = "/graphql/SaWqzw0TFAWMx1nXWjXoaQ/Following"
        variables = {
            "userId": self._user_id_by_screen_name(screen_name),
            "count": 100,
            "includePromotedContent": False,
            "withGrokTranslatedBio": False,
        }
        return self._pagination_users(endpoint, variables)

    @memcache(keyarg=1)
    def user_by_rest_id(self, rest_id):
        endpoint = "/graphql/8r5oa_2vD0WkhIAOkY4TTA/UserByRestId"
        features = self.features
        params = {
            "variables": self._json_dumps({
                "userId": rest_id,
            }),
            "features": self._json_dumps(features),
        }
        return self._call(endpoint, params)["data"]["user"]["result"]

    @memcache(keyarg=1)
    def user_by_screen_name(self, screen_name):
        endpoint = "/graphql/ck5KkZ8t5cOmoLssopN99Q/UserByScreenName"
        features = self.features.copy()
        features["subscriptions_verification_info_"
                 "is_identity_verified_enabled"] = True
        features["subscriptions_verification_info_"
                 "verified_since_enabled"] = True
        params = {
            "variables": self._json_dumps({
                "screen_name": screen_name,
                "withGrokTranslatedBio": False,
            }),
            "features": self._json_dumps(features),
            "fieldToggles": self._json_dumps({
                "withAuxiliaryUserLabels": True,
            }),
        }
        return self._call(endpoint, params)["data"]["user"]["result"]

    def _user_id_by_screen_name(self, screen_name):
        user = ()
        try:
            if screen_name.startswith("id:"):
                user = self.user_by_rest_id(screen_name[3:])
            else:
                user = self.user_by_screen_name(screen_name)
            self.extractor._assign_user(user)
            return user["rest_id"]
        except KeyError:
            if "unavailable_message" in user:
                raise exception.NotFoundError(
                    f"{user['unavailable_message'].get('text')} "
                    f"({user.get('reason')})", False)
            else:
                raise exception.NotFoundError("user")

    @cache(maxage=3600)
    def _guest_token(self):
        endpoint = "/1.1/guest/activate.json"
        self.log.info("Requesting guest token")
        return str(self._call(
            endpoint, None, "POST", False, "https://api.x.com",
        )["guest_token"])

    def _authenticate_guest(self):
        guest_token = self._guest_token()
        if guest_token != self.headers["x-guest-token"]:
            self.headers["x-guest-token"] = guest_token
            self.extractor.cookies.set(
                "gt", guest_token, domain=self.extractor.cookies_domain)

    @cache(maxage=10800)
    def _client_transaction(self):
        self.log.info("Initializing client transaction keys")

        from . import twitter_transaction_id
        ct = twitter_transaction_id.ClientTransaction()
        ct.initialize(self.extractor)

        # update 'x-csrf-token' header (#7467)
        csrf_token = self.extractor.cookies.get(
            "ct0", domain=self.extractor.cookies_domain)
        if csrf_token:
            self.headers["x-csrf-token"] = csrf_token

        return ct

    def _transaction_id(self, url, method="GET"):
        if self.client_transaction is None:
            TwitterAPI.client_transaction = self._client_transaction()
        path = url[url.find("/", 8):]
        self.headers["x-client-transaction-id"] = \
            self.client_transaction.generate_transaction_id(method, path)

    def _call(self, endpoint, params, method="GET", auth=True, root=None):
        url = (root or self.root) + endpoint

        while True:
            if auth:
                if self.headers["x-twitter-auth-type"]:
                    self._transaction_id(url, method)
                else:
                    self._authenticate_guest()

            response = self.extractor.request(
                url, method=method, params=params,
                headers=self.headers, fatal=None)

            # update 'x-csrf-token' header (#1170)
            if csrf_token := response.cookies.get("ct0"):
                self.headers["x-csrf-token"] = csrf_token

            remaining = int(response.headers.get("x-rate-limit-remaining", 6))
            if remaining < 6 and remaining <= random.randrange(1, 6):
                self._handle_ratelimit(response)
                continue

            try:
                data = response.json()
            except ValueError:
                data = {"errors": ({"message": response.text},)}

            errors = data.get("errors")
            if not errors:
                return data

            retry = False
            for error in errors:
                msg = error.get("message") or "Unspecified"
                self.log.debug("API error: '%s'", msg)

                if "this account is temporarily locked" in msg:
                    msg = "Account temporarily locked"
                    if self.extractor.config("locked") != "wait":
                        raise exception.AuthorizationError(msg)
                    self.log.warning(msg)
                    self.extractor.input("Press ENTER to retry.")
                    retry = True

                elif "Could not authenticate you" in msg:
                    raise exception.AbortExtraction(f"'{msg}'")

                elif msg.lower().startswith("timeout"):
                    retry = True

            if retry:
                if self.headers["x-twitter-auth-type"]:
                    self.log.debug("Retrying API request")
                    continue
                else:
                    # fall through to "Login Required"
                    response.status_code = 404

            if response.status_code < 400:
                return data
            elif response.status_code in (403, 404) and \
                    not self.headers["x-twitter-auth-type"]:
                raise exception.AuthRequired(
                    "authenticated cookies", "timeline")
            elif response.status_code == 429:
                self._handle_ratelimit(response)
                continue

            # error
            try:
                errors = ", ".join(e["message"] for e in errors)
            except Exception:
                pass

            raise exception.AbortExtraction(
                f"{response.status_code} {response.reason} ({errors})")

    def _pagination_legacy(self, endpoint, params):
        extr = self.extractor
        if cursor := extr._init_cursor():
            params["cursor"] = cursor
        original_retweets = (extr.retweets == "original")
        bottom = ("cursor-bottom-", "sq-cursor-bottom")

        while True:
            data = self._call(endpoint, params)

            instructions = data["timeline"]["instructions"]
            if not instructions:
                return extr._update_cursor(None)

            tweets = data["globalObjects"]["tweets"]
            users = data["globalObjects"]["users"]
            tweet_id = cursor = None
            tweet_ids = []
            entries = ()

            # process instructions
            for instr in instructions:
                if "addEntries" in instr:
                    entries = instr["addEntries"]["entries"]
                elif "replaceEntry" in instr:
                    entry = instr["replaceEntry"]["entry"]
                    if entry["entryId"].startswith(bottom):
                        cursor = (entry["content"]["operation"]
                                  ["cursor"]["value"])

            # collect tweet IDs and cursor value
            for entry in entries:
                entry_startswith = entry["entryId"].startswith

                if entry_startswith(("tweet-", "sq-I-t-")):
                    tweet_ids.append(
                        entry["content"]["item"]["content"]["tweet"]["id"])

                elif entry_startswith("homeConversation-"):
                    tweet_ids.extend(
                        entry["content"]["timelineModule"]["metadata"]
                        ["conversationMetadata"]["allTweetIds"][::-1])

                elif entry_startswith(bottom):
                    cursor = entry["content"]["operation"]["cursor"]
                    if not cursor.get("stopOnEmptyResponse", True):
                        # keep going even if there are no tweets
                        tweet_id = True
                    cursor = cursor["value"]

                elif entry_startswith("conversationThread-"):
                    tweet_ids.extend(
                        item["entryId"][6:]
                        for item in entry["content"]["timelineModule"]["items"]
                        if item["entryId"].startswith("tweet-")
                    )

            # process tweets
            for tweet_id in tweet_ids:
                try:
                    tweet = tweets[tweet_id]
                except KeyError:
                    self.log.debug("Skipping %s (deleted)", tweet_id)
                    continue

                if "retweeted_status_id_str" in tweet:
                    retweet = tweets.get(tweet["retweeted_status_id_str"])
                    if original_retweets:
                        if not retweet:
                            continue
                        retweet["retweeted_status_id_str"] = retweet["id_str"]
                        retweet["_retweet_id_str"] = tweet["id_str"]
                        tweet = retweet
                    elif retweet:
                        tweet["author"] = users[retweet["user_id_str"]]
                        if "extended_entities" in retweet and \
                                "extended_entities" not in tweet:
                            tweet["extended_entities"] = \
                                retweet["extended_entities"]
                tweet["user"] = users[tweet["user_id_str"]]
                yield tweet

                if "quoted_status_id_str" in tweet:
                    if quoted := tweets.get(tweet["quoted_status_id_str"]):
                        quoted = quoted.copy()
                        quoted["author"] = users[quoted["user_id_str"]]
                        quoted["quoted_by"] = tweet["user"]["screen_name"]
                        quoted["quoted_by_id_str"] = tweet["id_str"]
                        yield quoted

            # stop on empty response
            if not cursor or (not tweets and not tweet_id):
                return extr._update_cursor(None)
            params["cursor"] = extr._update_cursor(cursor)

    def _pagination_tweets(self, endpoint, variables,
                           path=None, stop_tweets=0, update_variables=None,
                           features=None, field_toggles=None):
        extr = self.extractor
        original_retweets = (extr.retweets == "original")
        pinned_tweet = extr.pinned
        stop_tweets_max = stop_tweets

        params = {"variables": None}
        if cursor := extr._init_cursor():
            variables["cursor"] = cursor
        if features is None:
            features = self.features_pagination
        if features:
            params["features"] = self._json_dumps(features)
        if field_toggles:
            params["fieldToggles"] = self._json_dumps(field_toggles)

        while True:
            params["variables"] = self._json_dumps(variables)
            data = self._call(endpoint, params)["data"]

            try:
                if path is None:
                    instructions = (data["user"]["result"]["timeline"]
                                    ["timeline"]["instructions"])
                else:
                    instructions = data
                    for key in path:
                        instructions = instructions[key]
                    instructions = instructions["instructions"]

                cursor = None
                entries = None
                for instr in instructions:
                    instr_type = instr.get("type")
                    if instr_type == "TimelineAddEntries":
                        if entries:
                            entries.extend(instr["entries"])
                        else:
                            entries = instr["entries"]
                    elif instr_type == "TimelineAddToModule":
                        entries = instr["moduleItems"]
                    elif instr_type == "TimelinePinEntry":
                        if pinned_tweet:
                            pinned_tweet = instr["entry"]
                    elif instr_type == "TimelineReplaceEntry":
                        entry = instr["entry"]
                        if entry["entryId"].startswith("cursor-bottom-"):
                            cursor = entry["content"]["value"]
                if entries is None:
                    if not cursor:
                        return extr._update_cursor(None)
                    entries = ()

            except LookupError:
                extr.log.debug(data)

                if user := extr._user_obj:
                    user = user["legacy"]
                    if user.get("blocked_by"):
                        if self.headers["x-twitter-auth-type"] and \
                                extr.config("logout"):
                            extr.cookies_file = None
                            del extr.cookies["auth_token"]
                            self.headers["x-twitter-auth-type"] = None
                            extr.log.info("Retrying API request as guest")
                            continue
                        raise exception.AuthorizationError(
                            f"{user['screen_name']} blocked your account")
                    elif user.get("protected"):
                        raise exception.AuthorizationError(
                            f"{user['screen_name']}'s Tweets are protected")

                raise exception.AbortExtraction(
                    "Unable to retrieve Tweets from this timeline")

            tweets = []
            tweet = None

            if pinned_tweet:
                if isinstance(pinned_tweet, dict):
                    tweets.append(pinned_tweet)
                elif instructions[-1]["type"] == "TimelinePinEntry":
                    tweets.append(instructions[-1]["entry"])
                pinned_tweet = False

            for entry in entries:
                esw = entry["entryId"].startswith

                if esw("tweet-"):
                    tweets.append(entry)
                elif esw(("profile-grid-",
                          "communities-grid-")):
                    if "content" in entry:
                        tweets.extend(entry["content"]["items"])
                    else:
                        tweets.append(entry)
                elif esw(("homeConversation-",
                          "profile-conversation-",
                          "conversationthread-")):
                    tweets.extend(entry["content"]["items"])
                elif esw("tombstone-"):
                    item = entry["content"]["itemContent"]
                    item["tweet_results"] = \
                        {"result": {"tombstone": item["tombstoneInfo"]}}
                    tweets.append(entry)
                elif esw("cursor-bottom-"):
                    cursor = entry["content"]
                    if "itemContent" in cursor:
                        cursor = cursor["itemContent"]
                    if not cursor.get("stopOnEmptyResponse", True):
                        # keep going even if there are no tweets
                        tweet = True
                    cursor = cursor.get("value")

            for entry in tweets:
                try:
                    item = ((entry.get("content") or entry["item"])
                            ["itemContent"])
                    if "promotedMetadata" in item and not extr.ads:
                        extr.log.debug(
                            "Skipping %s (ad)",
                            (entry.get("entryId") or "").rpartition("-")[2])
                        continue

                    tweet = item["tweet_results"]["result"]
                    if "tombstone" in tweet:
                        tweet = self._process_tombstone(
                            entry, tweet["tombstone"])
                        if not tweet:
                            continue

                    if "tweet" in tweet:
                        tweet = tweet["tweet"]
                    legacy = tweet["legacy"]
                    tweet["sortIndex"] = entry.get("sortIndex")
                except KeyError:
                    extr.log.debug(
                        "Skipping %s (deleted)",
                        (entry.get("entryId") or "").rpartition("-")[2])
                    continue

                if "retweeted_status_result" in legacy:
                    try:
                        retweet = legacy["retweeted_status_result"]["result"]
                        if "tweet" in retweet:
                            retweet = retweet["tweet"]
                        if original_retweets:
                            retweet["legacy"]["retweeted_status_id_str"] = \
                                retweet["rest_id"]
                            retweet["_retweet_id_str"] = tweet["rest_id"]
                            tweet = retweet
                        else:
                            legacy["retweeted_status_id_str"] = \
                                retweet["rest_id"]
                            tweet["author"] = \
                                retweet["core"]["user_results"]["result"]

                            rtlegacy = retweet["legacy"]

                            if "note_tweet" in retweet:
                                tweet["note_tweet"] = retweet["note_tweet"]

                            if "extended_entities" in rtlegacy and \
                                    "extended_entities" not in legacy:
                                legacy["extended_entities"] = \
                                    rtlegacy["extended_entities"]

                            if "withheld_scope" in rtlegacy and \
                                    "withheld_scope" not in legacy:
                                legacy["withheld_scope"] = \
                                    rtlegacy["withheld_scope"]

                            legacy["full_text"] = rtlegacy["full_text"]
                    except Exception as exc:
                        extr.log.debug(
                            "%s:  %s: %s",
                            tweet.get("rest_id"), exc.__class__.__name__, exc)
                        continue

                yield tweet

                if "quoted_status_result" in tweet:
                    try:
                        quoted = tweet["quoted_status_result"]["result"]
                        quoted["legacy"]["quoted_by"] = (
                            tweet["core"]["user_results"]["result"]
                            ["core"]["screen_name"])
                        quoted["legacy"]["quoted_by_id_str"] = tweet["rest_id"]
                        quoted["sortIndex"] = entry.get("sortIndex")

                        yield quoted
                    except KeyError:
                        extr.log.debug(
                            "Skipping quote of %s (deleted)",
                            tweet.get("rest_id"))
                        continue

            if tweet:
                stop_tweets = stop_tweets_max
                last_tweet = tweet
            else:
                if stop_tweets <= 0:
                    return extr._update_cursor(None)
                self.log.debug(
                    "No Tweet results (%s/%s)",
                    stop_tweets_max - stop_tweets + 1, stop_tweets_max)
                stop_tweets -= 1

            if not cursor or cursor == variables.get("cursor"):
                return extr._update_cursor(None)

            if update_variables is None:
                variables["cursor"] = extr._update_cursor(cursor)
            else:
                variables = update_variables(variables, cursor, last_tweet)

    def _pagination_users(self, endpoint, variables, path=None):
        extr = self.extractor
        if cursor := extr._init_cursor():
            variables["cursor"] = cursor
        params = {
            "variables": None,
            "features" : self._json_dumps(self.features_pagination),
        }

        while True:
            cursor = entry = None
            params["variables"] = self._json_dumps(variables)
            data = self._call(endpoint, params)["data"]

            try:
                if path is None:
                    instructions = (data["user"]["result"]["timeline"]
                                    ["timeline"]["instructions"])
                else:
                    for key in path:
                        data = data[key]
                    instructions = data["instructions"]
            except KeyError:
                return extr._update_cursor(None)

            for instr in instructions:
                if instr["type"] == "TimelineAddEntries":
                    for entry in instr["entries"]:
                        if entry["entryId"].startswith("user-"):
                            try:
                                user = (entry["content"]["itemContent"]
                                        ["user_results"]["result"])
                            except KeyError:
                                pass
                            else:
                                if "rest_id" in user:
                                    yield user
                        elif entry["entryId"].startswith("cursor-bottom-"):
                            cursor = entry["content"]["value"]

            if not cursor or cursor.startswith(("-1|", "0|")) or not entry:
                return extr._update_cursor(None)
            variables["cursor"] = extr._update_cursor(cursor)

    def _handle_ratelimit(self, response):
        rl = self.extractor.config("ratelimit")
        if rl == "abort":
            raise exception.AbortExtraction("Rate limit exceeded")
        elif rl and isinstance(rl, str) and rl.startswith("wait:"):
            until = None
            seconds = text.parse_float(rl.partition(":")[2]) or 60.0
        else:
            until = response.headers.get("x-rate-limit-reset")
            seconds = None if until else 60.0
        self.extractor.wait(until=until, seconds=seconds)

    def _process_tombstone(self, entry, tombstone):
        text = (tombstone.get("richText") or tombstone["text"])["text"]
        tweet_id = entry["entryId"].rpartition("-")[2]

        if text.startswith("Age-restricted"):
            if self._nsfw_warning:
                self._nsfw_warning = False
                self.log.warning('"%s"', text)

        self.log.debug("Skipping %s ('%s')", tweet_id, text)

    def _update_variables_search(self, variables, cursor, tweet):
        try:
            tweet_id = tweet.get("id_str") or tweet["legacy"]["id_str"]
            max_id = f"max_id:{int(tweet_id)-1}"

            query, n = text.re(r"\bmax_id:\d+").subn(
                max_id, variables["rawQuery"])
            if n:
                variables["rawQuery"] = query
            else:
                variables["rawQuery"] = f"{query} {max_id}"

            if prefix := self.extractor._cursor_prefix:
                self.extractor._cursor_prefix = \
                    f"{prefix.partition('_')[0]}_{tweet_id}/"
            variables["cursor"] = None
        except Exception as exc:
            self.extractor.log.debug(
                "Failed to update 'max_id' search query (%s: %s). Falling "
                "back to 'cursor' pagination", exc.__class__.__name__, exc)
            variables["cursor"] = self.extractor._update_cursor(cursor)

        return variables


@cache(maxage=365*86400, keyarg=1)
def _login_impl(extr, username, password):
    extr.log.error("Login with username & password is no longer supported. "
                   "Use browser cookies instead.")
    return {}
