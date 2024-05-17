# Changelog

## 1.26.9 - 2024-03-23
### Extractors
#### Additions
- [artstation] support video clips ([#2566](https://github.com/mikf/gallery-dl/issues/2566), [#3309](https://github.com/mikf/gallery-dl/issues/3309), [#3911](https://github.com/mikf/gallery-dl/issues/3911))
- [artstation] support collections ([#146](https://github.com/mikf/gallery-dl/issues/146))
- [deviantart] recognize `deviantart.com/stash/…` URLs
- [idolcomplex] support new pool URLs
- [lensdump] recognize direct image links ([#5293](https://github.com/mikf/gallery-dl/issues/5293))
- [skeb] add extractor for followed users ([#5290](https://github.com/mikf/gallery-dl/issues/5290))
- [twitter] add `quotes` extractor ([#5262](https://github.com/mikf/gallery-dl/issues/5262))
- [wikimedia] support `azurlane.koumakan.jp` ([#5256](https://github.com/mikf/gallery-dl/issues/5256))
- [xvideos] support `/channels/` URLs ([#5244](https://github.com/mikf/gallery-dl/issues/5244))
#### Fixes
- [artstation] fix handling usernames with dashes in domain names ([#5224](https://github.com/mikf/gallery-dl/issues/5224))
- [bluesky] fix not spawning child extractors for followed users ([#5246](https://github.com/mikf/gallery-dl/issues/5246))
- [deviantart] handle CloudFront blocks ([#5363](https://github.com/mikf/gallery-dl/issues/5363))
- [deviantart:avatar] fix `index` for URLs without `?` ([#5276](https://github.com/mikf/gallery-dl/issues/5276))
- [deviantart:stash] fix `index` values ([#5335](https://github.com/mikf/gallery-dl/issues/5335))
- [gofile] fix extraction
- [hiperdex] update URL patterns & fix `manga` metadata ([#5340](https://github.com/mikf/gallery-dl/issues/5340))
- [idolcomplex] fix metadata extraction
- [imagefap] fix folder extraction ([#5333](https://github.com/mikf/gallery-dl/issues/5333))
- [instagram] make accessing `like_count` non-fatal ([#5218](https://github.com/mikf/gallery-dl/issues/5218))
- [mastodon] fix handling null `moved` account field ([#5321](https://github.com/mikf/gallery-dl/issues/5321))
- [naver] fix EUC-KR encoding issue in old image URLs ([#5126](https://github.com/mikf/gallery-dl/issues/5126))
- [nijie] increase default delay between requests ([#5221](https://github.com/mikf/gallery-dl/issues/5221))
- [nitter] ignore invalid Tweets ([#5253](https://github.com/mikf/gallery-dl/issues/5253))
- [pixiv:novel] fix text extraction ([#5285](https://github.com/mikf/gallery-dl/issues/5285), [#5309](https://github.com/mikf/gallery-dl/issues/5309))
- [skeb] retry 429 responses containing a `request_key` cookie ([#5210](https://github.com/mikf/gallery-dl/issues/5210))
- [warosu] fix crash for threads with deleted posts ([#5289](https://github.com/mikf/gallery-dl/issues/5289))
- [weibo] fix retweets ([#2825](https://github.com/mikf/gallery-dl/issues/2825), [#3874](https://github.com/mikf/gallery-dl/issues/3874), [#5263](https://github.com/mikf/gallery-dl/issues/5263))
- [weibo] fix `livephoto` filename extensions ([#5287](https://github.com/mikf/gallery-dl/issues/5287))
- [xvideos] fix galleries with more than 500 images ([#5244](https://github.com/mikf/gallery-dl/issues/5244))
#### Improvements
- [bluesky] improve API error messages
- [bluesky] handle posts with different `embed` structure
- [deviantart:avatar] ignore default avatars ([#5276](https://github.com/mikf/gallery-dl/issues/5276))
- [fapello] download full-sized images ([#5349](https://github.com/mikf/gallery-dl/issues/5349))
- [gelbooru:favorite] automatically detect returned post order ([#5220](https://github.com/mikf/gallery-dl/issues/5220))
- [imgur] fail downloads when redirected to `removed.png` ([#5308](https://github.com/mikf/gallery-dl/issues/5308))
- [instagram] raise proper error for missing `reels_media` ([#5257](https://github.com/mikf/gallery-dl/issues/5257))
- [instagram] change `posts are private` exception to a warning ([#5322](https://github.com/mikf/gallery-dl/issues/5322))
- [reddit] improve preview fallback formats ([#5296](https://github.com/mikf/gallery-dl/issues/5296), [#5315](https://github.com/mikf/gallery-dl/issues/5315))
- [steamgriddb] raise exception for deleted assets
- [twitter] handle "account is temporarily locked" errors ([#5300](https://github.com/mikf/gallery-dl/issues/5300))
- [weibo] rework pagination logic ([#4168](https://github.com/mikf/gallery-dl/issues/4168))
- [zerochan] fetch more posts by using the API ([#3669](https://github.com/mikf/gallery-dl/issues/3669))
#### Metadata
- [bluesky] add `instance` metadata field ([#4438](https://github.com/mikf/gallery-dl/issues/4438))
- [gelbooru:favorite] add `date_favorited` metadata field
- [imagefap] extract `folder` metadata ([#5270](https://github.com/mikf/gallery-dl/issues/5270))
- [instagram] default `likes` to `0` ([#5323](https://github.com/mikf/gallery-dl/issues/5323))
- [kemonoparty] add `revision_count` metadata field ([#5334](https://github.com/mikf/gallery-dl/issues/5334))
- [naver] unescape post `title` and `description`
- [pornhub:gif] extract `viewkey` and `timestamp` metadata ([#4463](https://github.com/mikf/gallery-dl/issues/4463))
- [redgifs] make `date` available for directories ([#5262](https://github.com/mikf/gallery-dl/issues/5262))
- [subscribestar] fix `date` metadata
- [twitter] add `birdwatch` metadata field ([#5317](https://github.com/mikf/gallery-dl/issues/5317))
- [twitter] add `protected` metadata field ([#5327](https://github.com/mikf/gallery-dl/issues/5327))
- [warosu] fix `board_name` metadata
#### Options
- [bluesky] add `reposts` option ([#4438](https://github.com/mikf/gallery-dl/issues/4438), [#5248](https://github.com/mikf/gallery-dl/issues/5248))
- [deviantart] add `comments-avatars` option ([#4995](https://github.com/mikf/gallery-dl/issues/4995))
- [deviantart] extend `metadata` option ([#5175](https://github.com/mikf/gallery-dl/issues/5175))
- [flickr] add `contexts` option ([#5324](https://github.com/mikf/gallery-dl/issues/5324))
- [gelbooru:favorite] add `order-posts` option ([#5220](https://github.com/mikf/gallery-dl/issues/5220))
- [kemonoparty] add `order-revisions` option ([#5334](https://github.com/mikf/gallery-dl/issues/5334))
- [vipergirls] add `like` option ([#4166](https://github.com/mikf/gallery-dl/issues/4166))
- [vipergirls] add `domain` option ([#4166](https://github.com/mikf/gallery-dl/issues/4166))
### Downloaders
- [http] add MIME type and signature for `.mov` files ([#5287](https://github.com/mikf/gallery-dl/issues/5287))
### Docker
- build images from source instead of PyPI package
- build `linux/arm64` images ([#5227](https://github.com/mikf/gallery-dl/issues/5227))
- build images on every push to master
  - tag images as `YYYY.MM.DD`
  - tag the most recent build from master as `dev`
  - tag the most recent release build as `latest`
- reduce image size ([#5097](https://github.com/mikf/gallery-dl/issues/5097))
### Miscellaneous
- [formatter] fix local DST datetime offsets for `:O`
- build Linux executable on Ubuntu 22.04 LTS ([#4184](https://github.com/mikf/gallery-dl/issues/4184))
- automatically create directories for logging files ([#5249](https://github.com/mikf/gallery-dl/issues/5249))

## 1.26.8 - 2024-02-17
### Extractors
#### Additions
- [bluesky] add support ([#4438](https://github.com/mikf/gallery-dl/issues/4438), [#4708](https://github.com/mikf/gallery-dl/issues/4708), [#4722](https://github.com/mikf/gallery-dl/issues/4722), [#5047](https://github.com/mikf/gallery-dl/issues/5047))
- [bunkr] support new domains ([#5114](https://github.com/mikf/gallery-dl/issues/5114), [#5130](https://github.com/mikf/gallery-dl/issues/5130), [#5134](https://github.com/mikf/gallery-dl/issues/5134))
- [fanbox] add `home` and `supporting` extractors ([#5138](https://github.com/mikf/gallery-dl/issues/5138))
- [imagechest] add `user` extractor ([#5143](https://github.com/mikf/gallery-dl/issues/5143))
- [imagetwist] add `gallery` extractor ([#5190](https://github.com/mikf/gallery-dl/issues/5190))
- [kemonoparty] add `posts` extractor ([#5194](https://github.com/mikf/gallery-dl/issues/5194), [#5198](https://github.com/mikf/gallery-dl/issues/5198))
- [twitter] support communities ([#4913](https://github.com/mikf/gallery-dl/issues/4913))
- [vsco] support spaces ([#5202](https://github.com/mikf/gallery-dl/issues/5202))
- [weibo] add `gifs` option ([#5183](https://github.com/mikf/gallery-dl/issues/5183))
- [wikimedia] support `www.pidgi.net` ([#5205](https://github.com/mikf/gallery-dl/issues/5205))
- [wikimedia] support `bulbapedia.bulbagarden.net` ([#5206](https://github.com/mikf/gallery-dl/issues/5206))
#### Fixes
- [archivedmoe] fix `thebarchive` WebM URLs ([#5116](https://github.com/mikf/gallery-dl/issues/5116))
- [batoto] fix crash when manga name or chapter contains a `-` ([#5200](https://github.com/mikf/gallery-dl/issues/5200))
- [bunkr] fix extraction ([#5088](https://github.com/mikf/gallery-dl/issues/5088), [#5151](https://github.com/mikf/gallery-dl/issues/5151), [#5153](https://github.com/mikf/gallery-dl/issues/5153))
- [gofile] update `website_token` extraction
- [idolcomplex] fix pagination for tags containing `:` ([#5184](https://github.com/mikf/gallery-dl/issues/5184))
- [kemonoparty] fix deleting file names when computing `revision_hash` ([#5103](https://github.com/mikf/gallery-dl/issues/5103))
- [luscious] fix IndexError for files without thumbnail ([#5122](https://github.com/mikf/gallery-dl/issues/5122), [#5124](https://github.com/mikf/gallery-dl/issues/5124), [#5182](https://github.com/mikf/gallery-dl/issues/5182))
- [naverwebtoon] fix `title` for comics with empty tags ([#5120](https://github.com/mikf/gallery-dl/issues/5120))
- [pinterest] fix section URLs for boards with `/`, `?`, or `#` in their name ([#5104](https://github.com/mikf/gallery-dl/issues/5104))
- [twitter] update query hashes
- [zerochan] fix skipping every other post
#### Improvements
- [deviantart] skip locked/blurred posts ([#4567](https://github.com/mikf/gallery-dl/issues/4567), [#5193](https://github.com/mikf/gallery-dl/issues/5193))
- [deviantart] implement downloading PNG versions of non-original images with `"quality": "png"` ([#4846](https://github.com/mikf/gallery-dl/issues/4846))
- [flickr] handle non-JSON errors ([#5131](https://github.com/mikf/gallery-dl/issues/5131))
- [idolcomplex] support alphanumeric post IDs ([#5171](https://github.com/mikf/gallery-dl/issues/5171))
- [kemonoparty] implement filtering duplicate revisions with `"revisions": "unique"`([#5013](https://github.com/mikf/gallery-dl/issues/5013))
- [naverwebtoon] support `/webtoon/` paths for all comics ([#5123](https://github.com/mikf/gallery-dl/issues/5123))
#### Metadata
- [idolcomplex] extract `id_alnum` metadata ([#5171](https://github.com/mikf/gallery-dl/issues/5171))
- [pornpics] support multiple values for `channel` ([#5195](https://github.com/mikf/gallery-dl/issues/5195))
- [sankaku] add `id-format` option ([#5073](https://github.com/mikf/gallery-dl/issues/5073))
- [skeb] add `num` and `count` metadata fields ([#5187](https://github.com/mikf/gallery-dl/issues/5187))
### Downloaders
#### Fixes
- [http] remove `pyopenssl` import ([#5156](https://github.com/mikf/gallery-dl/issues/5156))
### Miscellaneous
- fix filename formatting silently failing under certain circumstances ([#5185](https://github.com/mikf/gallery-dl/issues/5185), [#5186](https://github.com/mikf/gallery-dl/issues/5186))

## 1.26.7 - 2024-01-21
### Extractors
#### Additions
- [2ch] add support ([#1009](https://github.com/mikf/gallery-dl/issues/1009), [#3540](https://github.com/mikf/gallery-dl/issues/3540), [#4444](https://github.com/mikf/gallery-dl/issues/4444))
- [deviantart:avatar] add `formats` option ([#4995](https://github.com/mikf/gallery-dl/issues/4995))
- [hatenablog] add support ([#5036](https://github.com/mikf/gallery-dl/issues/5036), [#5037](https://github.com/mikf/gallery-dl/issues/5037))
- [mangadex] add `list` extractor ([#5025](https://github.com/mikf/gallery-dl/issues/5025))
- [steamgriddb] add support ([#5033](https://github.com/mikf/gallery-dl/issues/5033), [#5041](https://github.com/mikf/gallery-dl/issues/5041))
- [wikimedia] add support ([#1443](https://github.com/mikf/gallery-dl/issues/1443), [#2906](https://github.com/mikf/gallery-dl/issues/2906), [#3660](https://github.com/mikf/gallery-dl/issues/3660), [#2340](https://github.com/mikf/gallery-dl/issues/2340))
- [wikimedia] support `fandom` wikis ([#2677](https://github.com/mikf/gallery-dl/issues/2677), [#3378](https://github.com/mikf/gallery-dl/issues/3378))
#### Fixes
- [blogger] fix `lh-*.googleusercontent.com` URLs ([#5091](https://github.com/mikf/gallery-dl/issues/5091))
- [bunkr] update domain ([#5088](https://github.com/mikf/gallery-dl/issues/5088))
- [deviantart] fix AttributeError for URLs without username ([#5065](https://github.com/mikf/gallery-dl/issues/5065))
- [deviantart] fix `KeyError: 'premium_folder_data'` ([#5063](https://github.com/mikf/gallery-dl/issues/5063))
- [deviantart:avatar] fix exception when `comments` are enabled ([#4995](https://github.com/mikf/gallery-dl/issues/4995))
- [fuskator] make metadata extraction non-fatal ([#5039](https://github.com/mikf/gallery-dl/issues/5039))
- [gelbooru] only log "Incomplete API response" for favorites ([#5045](https://github.com/mikf/gallery-dl/issues/5045))
- [giantessbooru] update domain
- [issuu] fix extraction
- [nijie] fix download URLs of single image posts ([#5049](https://github.com/mikf/gallery-dl/issues/5049))
- [patreon] fix `KeyError: 'name'` ([#5048](https://github.com/mikf/gallery-dl/issues/5048), [#5069](https://github.com/mikf/gallery-dl/issues/5069), [#5093](https://github.com/mikf/gallery-dl/issues/5093))
- [pixiv] update API headers ([#5029](https://github.com/mikf/gallery-dl/issues/5029))
- [realbooru] fix download URLs of older posts
- [twitter] revert to using `media` timeline by default ([#4953](https://github.com/mikf/gallery-dl/issues/4953))
- [vk] transform image URLs to non-blurred versions ([#5017](https://github.com/mikf/gallery-dl/issues/5017))
#### Improvements
- [batoto] support more mirror domains ([#5042](https://github.com/mikf/gallery-dl/issues/5042))
- [batoto] improve v2 manga URL pattern
- [gelbooru] support `all` tag and URLs with empty tags ([#5076](https://github.com/mikf/gallery-dl/issues/5076))
- [patreon] download `m3u8` manifests with ytdl
- [sankaku] support post URLs with alphanumeric IDs ([#5073](https://github.com/mikf/gallery-dl/issues/5073))
#### Metadata
- [batoto] improve `manga_id` extraction ([#5042](https://github.com/mikf/gallery-dl/issues/5042))
- [erome] fix `count` metadata
- [kemonoparty] add `revision_hash` metadata ([#4706](https://github.com/mikf/gallery-dl/issues/4706), [#4727](https://github.com/mikf/gallery-dl/issues/4727), [#5013](https://github.com/mikf/gallery-dl/issues/5013))
- [paheal] fix `source` metadata
- [webtoons] extract more metadata ([#5061](https://github.com/mikf/gallery-dl/issues/5061), [#5094](https://github.com/mikf/gallery-dl/issues/5094))
#### Removals
- [chevereto] remove `pixl.li`
- [hbrowse] remove module
- [nitter] remove `nitter.lacontrevoie.fr`

## 1.26.6 - 2024-01-06
### Extractors
#### Additions
- [batoto] add `chapter` and `manga` extractors ([#1434](https://github.com/mikf/gallery-dl/issues/1434), [#2111](https://github.com/mikf/gallery-dl/issues/2111), [#4979](https://github.com/mikf/gallery-dl/issues/4979))
- [deviantart] add `avatar` and `background` extractors ([#4995](https://github.com/mikf/gallery-dl/issues/4995))
- [poringa] add support ([#4675](https://github.com/mikf/gallery-dl/issues/4675), [#4962](https://github.com/mikf/gallery-dl/issues/4962))
- [szurubooru] support `snootbooru.com` ([#5023](https://github.com/mikf/gallery-dl/issues/5023))
- [zzup] add `gallery` extractor ([#4517](https://github.com/mikf/gallery-dl/issues/4517), [#4604](https://github.com/mikf/gallery-dl/issues/4604), [#4659](https://github.com/mikf/gallery-dl/issues/4659), [#4863](https://github.com/mikf/gallery-dl/issues/4863), [#5016](https://github.com/mikf/gallery-dl/issues/5016))
#### Fixes
- [gelbooru] fix `favorite` extractor ([#4903](https://github.com/mikf/gallery-dl/issues/4903))
- [idolcomplex] fix extraction & update URL patterns ([#5002](https://github.com/mikf/gallery-dl/issues/5002))
- [imagechest] fix loading more than 10 images in a gallery ([#4469](https://github.com/mikf/gallery-dl/issues/4469))
- [jpgfish] update domain
- [komikcast] fix `manga` extractor ([#5027](https://github.com/mikf/gallery-dl/issues/5027))
- [komikcast] update domain ([#5027](https://github.com/mikf/gallery-dl/issues/5027))
- [lynxchan] update `bbw-chan` domain ([#4970](https://github.com/mikf/gallery-dl/issues/4970))
- [manganelo] fix extraction & recognize `.to` TLDs ([#5005](https://github.com/mikf/gallery-dl/issues/5005))
- [paheal] restore `extension` metadata ([#4976](https://github.com/mikf/gallery-dl/issues/4976))
- [rule34us] add fallback for `video-cdn1` videos ([#4985](https://github.com/mikf/gallery-dl/issues/4985))
- [weibo] fix AttributeError in `user` extractor ([#5022](https://github.com/mikf/gallery-dl/issues/5022))
#### Improvements
- [gelbooru] show error for invalid API responses ([#4903](https://github.com/mikf/gallery-dl/issues/4903))
- [rule34] recognize URLs with `www` subdomain ([#4984](https://github.com/mikf/gallery-dl/issues/4984))
- [twitter] raise error for invalid `strategy` values ([#4953](https://github.com/mikf/gallery-dl/issues/4953))
#### Metadata
- [fanbox] add `metadata` option ([#4921](https://github.com/mikf/gallery-dl/issues/4921))
- [nijie] add `count` metadata ([#146](https://github.com/mikf/gallery-dl/issues/146))
- [pinterest] add `count` metadata ([#4981](https://github.com/mikf/gallery-dl/issues/4981))
### Miscellaneous
- fix and update zsh completion ([#4972](https://github.com/mikf/gallery-dl/issues/4972))
- fix `--cookies-from-browser` macOS Firefox profile path

## 1.26.5 - 2023-12-23
### Extractors
#### Additions
- [deviantart] add `intermediary` option ([#4955](https://github.com/mikf/gallery-dl/issues/4955))
- [inkbunny] add `unread` extractor ([#4934](https://github.com/mikf/gallery-dl/issues/4934))
- [mastodon] support non-numeric status IDs ([#4936](https://github.com/mikf/gallery-dl/issues/4936))
- [myhentaigallery] recognize `/g/` URLs ([#4920](https://github.com/mikf/gallery-dl/issues/4920))
- [postmill] add support ([#4917](https://github.com/mikf/gallery-dl/issues/4917), [#4919](https://github.com/mikf/gallery-dl/issues/4919))
- {shimmie2[ support `rule34hentai.net` ([#861](https://github.com/mikf/gallery-dl/issues/861), [#4789](https://github.com/mikf/gallery-dl/issues/4789), [#4945](https://github.com/mikf/gallery-dl/issues/4945))
#### Fixes
- [deviantart] add workaround for integer `client-id` values ([#4924](https://github.com/mikf/gallery-dl/issues/4924))
- [exhentai] fix error for infinite `fallback-retries` ([#4911](https://github.com/mikf/gallery-dl/issues/4911))
- [inkbunny] stop pagination on empty results
- [patreon] fix bootstrap data extraction again ([#4904](https://github.com/mikf/gallery-dl/issues/4904))
- [tumblr] fix exception after waiting for rate limit ([#4916](https://github.com/mikf/gallery-dl/issues/4916))
#### Improvements
- [exhentai] output continuation URL when interrupted ([#4782](https://github.com/mikf/gallery-dl/issues/4782))
- [inkbunny] improve `/submissionsviewall.php` patterns ([#4934](https://github.com/mikf/gallery-dl/issues/4934))
- [tumblr] support infinite `fallback-retries`
- [twitter] default to `tweets` timeline when `replies` are enabled ([#4953](https://github.com/mikf/gallery-dl/issues/4953))
#### Metadata
- [danbooru] provide `tags` as list ([#4942](https://github.com/mikf/gallery-dl/issues/4942))
- [deviantart] set `is_original` for intermediary URLs to `false`
- [twitter] remove `date_liked` ([#3850](https://github.com/mikf/gallery-dl/issues/3850), [#4108](https://github.com/mikf/gallery-dl/issues/4108), [#4657](https://github.com/mikf/gallery-dl/issues/4657))
### Docker
- add Docker instructions to README ([#4850](https://github.com/mikf/gallery-dl/issues/4850))
- fix auto-generation of `latest` tags

## 1.26.4 - 2023-12-10
### Extractors
#### Additions
- [exhentai] add `fallback-retries` option ([#4792](https://github.com/mikf/gallery-dl/issues/4792))
- [urlgalleries] add `gallery` extractor ([#919](https://github.com/mikf/gallery-dl/issues/919), [#1184](https://github.com/mikf/gallery-dl/issues/1184), [#2905](https://github.com/mikf/gallery-dl/issues/2905), [#4886](https://github.com/mikf/gallery-dl/issues/4886))
#### Fixes
- [nijie] fix image URLs of multi-image posts ([#4876](https://github.com/mikf/gallery-dl/issues/4876))
- [patreon] fix bootstrap data extraction ([#4904](https://github.com/mikf/gallery-dl/issues/4904), [#4906](https://github.com/mikf/gallery-dl/issues/4906))
- [twitter] fix `/media` timelines ([#4898](https://github.com/mikf/gallery-dl/issues/4898), [#4899](https://github.com/mikf/gallery-dl/issues/4899))
- [twitter] retry API requests when response contains incomplete results ([#4811](https://github.com/mikf/gallery-dl/issues/4811))
#### Improvements
- [exhentai] store more cookies when logging in with username & password ([#4881](https://github.com/mikf/gallery-dl/issues/4881))
- [twitter] generalize "Login Required" errors ([#4734](https://github.com/mikf/gallery-dl/issues/4734), [#4324](https://github.com/mikf/gallery-dl/issues/4324))
### Options
- add `-e/--error-file` command-line and `output.errorfile` config option ([#4732](https://github.com/mikf/gallery-dl/issues/4732))
### Miscellaneous
- automatically build and push Docker images
- prompt for passwords on login when necessary
- fix `util.dump_response()` to work with `bytes` header values

## 1.26.3 - 2023-11-27
### Extractors
#### Additions
- [behance] support `text` modules ([#4799](https://github.com/mikf/gallery-dl/issues/4799))
- [behance] add `modules` option ([#4799](https://github.com/mikf/gallery-dl/issues/4799))
- [blogger] support `www.micmicidol.club` ([#4759](https://github.com/mikf/gallery-dl/issues/4759))
- [erome] add `count` metadata ([#4812](https://github.com/mikf/gallery-dl/issues/4812))
- [exhentai] add `gp` option ([#4576](https://github.com/mikf/gallery-dl/issues/4576))
- [fapello] support `.su` TLD ([#4840](https://github.com/mikf/gallery-dl/issues/4840), [#4841](https://github.com/mikf/gallery-dl/issues/4841))
- [pixeldrain] add `file` and `album` extractors ([#4839](https://github.com/mikf/gallery-dl/issues/4839))
- [pixeldrain] add `api-key` option ([#4839](https://github.com/mikf/gallery-dl/issues/4839))
- [tmohentai] add `gallery` extractor ([#4808](https://github.com/mikf/gallery-dl/issues/4808), [#4832](https://github.com/mikf/gallery-dl/issues/4832))
#### Fixes
- [cyberdrop] update to site layout changes
- [exhentai] handle `Downloading … requires GP` errors ([#4576](https://github.com/mikf/gallery-dl/issues/4576), [#4763](https://github.com/mikf/gallery-dl/issues/4763))
- [exhentai] fix empty API URL with `"source": "hitomi"` ([#4829](https://github.com/mikf/gallery-dl/issues/4829))
- [hentaifoundry] check for and update expired sessions ([#4694](https://github.com/mikf/gallery-dl/issues/4694))
- [hiperdex] fix `manga` metadata
- [idolcomplex] update to site layout changes
- [imagefap] fix resolution of single images
- [instagram] fix exception on empty `video_versions` ([#4795](https://github.com/mikf/gallery-dl/issues/4795))
- [mangaread] fix extraction
- [mastodon] fix reblogs ([#4580](https://github.com/mikf/gallery-dl/issues/4580))
- [nitter] fix video extraction ([#4853](https://github.com/mikf/gallery-dl/issues/4853), [#4855](https://github.com/mikf/gallery-dl/issues/4855))
- [pornhub] fix `user` metadata for gifs
- [tumblr] fix `day` extractor
- [wallpapercave] fix extraction
- [warosu] fix file URLs
- [webtoons] fix pagination when receiving an HTTP redirect
- [xvideos] fix metadata extraction
- [zerochan] fix metadata extraction
#### Improvements
- [hentaicosplays] force `https://` for download URLs
- [oauth] warn when cache is enabled but not writeable ([#4771](https://github.com/mikf/gallery-dl/issues/4771))
- [sankaku] update URL patterns
- [twitter] ignore promoted Tweets ([#3894](https://github.com/mikf/gallery-dl/issues/3894), [#4790](https://github.com/mikf/gallery-dl/issues/4790))
- [weibo] detect redirects to login page ([#4773](https://github.com/mikf/gallery-dl/issues/4773))
#### Removals
- [foolslide] remove `powermanga.org`
### Downloaders
#### Changes
- [http] treat files not passing `filesize-min`/`-max` as skipped ([#4821](https://github.com/mikf/gallery-dl/issues/4821))
### Options
#### Additions
- add `metadata-extractor` option ([#4549](https://github.com/mikf/gallery-dl/issues/4549))
- support `metadata-*` names for `*-metadata` options
  (for example `url-metadata` is now also recognized as `metadata-url`)
### CLI
#### Additions
- implement `-I/--input-file-comment` and `-x/--input-file-delete` options ([#4732](https://github.com/mikf/gallery-dl/issues/4732))
- add `--ugoira` as a general version of `--ugoira-conv` and co.
- add `--mtime` as a general version of `--mtime-from-date`
- add `--cbz`
#### Fixes
- allow `--mtime-from-date` to work with Weibo`s metadata structure
### Miscellaneous
#### Additions
- add a simple Dockerfile ([#4831](https://github.com/mikf/gallery-dl/issues/4831))

## 1.26.2 - 2023-11-04
### Extractors
#### Additions
- [4archive] add `thread` and `board` extractors ([#1262](https://github.com/mikf/gallery-dl/issues/1262), [#2418](https://github.com/mikf/gallery-dl/issues/2418), [#4400](https://github.com/mikf/gallery-dl/issues/4400), [#4710](https://github.com/mikf/gallery-dl/issues/4710), [#4714](https://github.com/mikf/gallery-dl/issues/4714))
- [hitomi] recognize `imageset` gallery URLs ([#4756](https://github.com/mikf/gallery-dl/issues/4756))
- [kemonoparty] add `revision_index` metadata field ([#4727](https://github.com/mikf/gallery-dl/issues/4727))
- [misskey] support `misskey.design` ([#4713](https://github.com/mikf/gallery-dl/issues/4713))
- [reddit] support Reddit Mobile share links ([#4693](https://github.com/mikf/gallery-dl/issues/4693))
- [sankaku] support `/posts/` tag search URLs ([#4740](https://github.com/mikf/gallery-dl/issues/4740))
- [twitter] recognize `fixupx.com` URLs ([#4755](https://github.com/mikf/gallery-dl/issues/4755))
#### Fixes
- [exhentai] update to site layout changes ([#4730](https://github.com/mikf/gallery-dl/issues/4730), [#4754](https://github.com/mikf/gallery-dl/issues/4754))
- [exhentai] provide fallback URLs ([#1021](https://github.com/mikf/gallery-dl/issues/1021), [#4745](https://github.com/mikf/gallery-dl/issues/4745))
- [exhentai] disable `DH` ciphers to avoid `DH_KEY_TOO_SMALL` errors ([#1021](https://github.com/mikf/gallery-dl/issues/1021), [#4593](https://github.com/mikf/gallery-dl/issues/4593))
- [idolcomplex] disable sending Referer headers ([#4726](https://github.com/mikf/gallery-dl/issues/4726))
- [instagram] update API headers
- [kemonoparty] fix parsing of non-standard `date` values ([#4676](https://github.com/mikf/gallery-dl/issues/4676))
- [patreon] fix `campaign_id` extraction ([#4699](https://github.com/mikf/gallery-dl/issues/4699), [#4715](https://github.com/mikf/gallery-dl/issues/4715), [#4736](https://github.com/mikf/gallery-dl/issues/4736), [#4738](https://github.com/mikf/gallery-dl/issues/4738))
- [pixiv] load cookies for non-OAuth URLs ([#4760](https://github.com/mikf/gallery-dl/issues/4760))
- [twitter] fix avatars without `date` information ([#4696](https://github.com/mikf/gallery-dl/issues/4696))
- [twitter] restore truncated retweet texts ([#3430](https://github.com/mikf/gallery-dl/issues/3430), [#4690](https://github.com/mikf/gallery-dl/issues/4690))
- [weibo] fix Sina Visitor requests
#### Improvements
- [behance] unescape embed URLs ([#4742](https://github.com/mikf/gallery-dl/issues/4742))
- [fantia] simplify `tags` to a list of strings ([#4752](https://github.com/mikf/gallery-dl/issues/4752))
- [kemonoparty] limit `title` length ([#4741](https://github.com/mikf/gallery-dl/issues/4741))
- [nijie] set 1-2s delay between requests to avoid 429 errors
- [patreon] provide ways to manually specify a user's campaign_id
  - `https://www.patreon.com/id:12345`
  - `https://www.patreon.com/USER?c=12345`
  - `https://www.patreon.com/USER?campaign_id=12345`
- [twitter] cache `user_by_…` results ([#4719](https://github.com/mikf/gallery-dl/issues/4719))
### Post Processors
#### Fixes
- [metadata] ignore non-string tag values ([#4764](https://github.com/mikf/gallery-dl/issues/4764))
### Miscellaneous
#### Fixes
- prevent crash when `stdout.line_buffering` is not defined ([#642](https://github.com/mikf/gallery-dl/issues/642))

## 1.26.1 - 2023-10-21
### Extractors
#### Additions
- [bunkr] add extractor for media URLs ([#4684](https://github.com/mikf/gallery-dl/issues/4684))
- [chevereto] add generic extractors for `chevereto` sites ([#4664](https://github.com/mikf/gallery-dl/issues/4664))
  - `deltaporno.com` ([#1381](https://github.com/mikf/gallery-dl/issues/1381))
  - `img.kiwi`
  - `jpgfish`
  - `pixl.li` ([#3179](https://github.com/mikf/gallery-dl/issues/3179), [#4357](https://github.com/mikf/gallery-dl/issues/4357))
- [deviantart] implement `"group": "skip"` ([#4630](https://github.com/mikf/gallery-dl/issues/4630))
- [fantia] add `content_count` and `content_num` metadata fields ([#4627](https://github.com/mikf/gallery-dl/issues/4627))
- [imgbb] add `displayname` and `user_id` metadata ([#4626](https://github.com/mikf/gallery-dl/issues/4626))
- [kemonoparty] support post revisions; add `revisions` option ([#4498](https://github.com/mikf/gallery-dl/issues/4498), [#4597](https://github.com/mikf/gallery-dl/issues/4597))
- [kemonoparty] support searches ([#3385](https://github.com/mikf/gallery-dl/issues/3385), [#4057](https://github.com/mikf/gallery-dl/issues/4057))
- [kemonoparty] support discord URLs with channel IDs ([#4662](https://github.com/mikf/gallery-dl/issues/4662))
- [moebooru] add `metadata` option ([#4646](https://github.com/mikf/gallery-dl/issues/4646))
- [newgrounds] support multi-image posts ([#4642](https://github.com/mikf/gallery-dl/issues/4642))
- [sankaku] support `/posts/` URLs ([#4688](https://github.com/mikf/gallery-dl/issues/4688))
- [twitter] add `sensitive` metadata field ([#4619](https://github.com/mikf/gallery-dl/issues/4619))
#### Fixes
- [4chanarchives] disable Referer headers by default ([#4686](https://github.com/mikf/gallery-dl/issues/4686))
- [bunkr] fix `/d/` file URLs ([#4685](https://github.com/mikf/gallery-dl/issues/4685))
- [deviantart] expand nested comment replies ([#4653](https://github.com/mikf/gallery-dl/issues/4653))
- [deviantart] disable `jwt` ([#4652](https://github.com/mikf/gallery-dl/issues/4652))
- [hentaifoundry] fix `.swf` file downloads ([#4641](https://github.com/mikf/gallery-dl/issues/4641))
- [imgbb] fix `user` metadata extraction ([#4626](https://github.com/mikf/gallery-dl/issues/4626))
- [imgbb] update pagination end condition ([#4626](https://github.com/mikf/gallery-dl/issues/4626))
- [kemonoparty] update API endpoints ([#4676](https://github.com/mikf/gallery-dl/issues/4676), [#4677](https://github.com/mikf/gallery-dl/issues/4677))
- [patreon] update `campaign_id` path ([#4639](https://github.com/mikf/gallery-dl/issues/4639))
- [reddit] fix wrong previews ([#4649](https://github.com/mikf/gallery-dl/issues/4649))
- [redgifs] fix `niches` extraction ([#4666](https://github.com/mikf/gallery-dl/issues/4666), [#4667](https://github.com/mikf/gallery-dl/issues/4667))
- [twitter] fix crash due to missing `source` ([#4620](https://github.com/mikf/gallery-dl/issues/4620))
- [warosu] fix extraction ([#4634](https://github.com/mikf/gallery-dl/issues/4634))
### Post Processors
#### Additions
- support `{_filename}`, `{_directory}`, and `{_path}` replacement fields for `--exec` ([#4633](https://github.com/mikf/gallery-dl/issues/4633))
### Miscellaneous
#### Improvements
- avoid temporary copies with `--cookies-from-browser` by opening cookie databases in read-only mode

## 1.26.0 - 2023-10-03
- ### Extractors
    #### Additions
    - [behance] add `date` metadata field ([#4417](https://github.com/mikf/gallery-dl/issues/4417))
    - [danbooru] support `booru.borvar.art` ([#4096](https://github.com/mikf/gallery-dl/issues/4096))
    - [danbooru] support `donmai.moe`
    - [deviantart] add `is_original` metadata field ([#4559](https://github.com/mikf/gallery-dl/issues/4559))
    - [e621] support `e6ai.net` ([#4320](https://github.com/mikf/gallery-dl/issues/4320))
    - [exhentai] add `fav` option ([#4409](https://github.com/mikf/gallery-dl/issues/4409))
    - [gelbooru_v02] support `xbooru.com` ([#4493](https://github.com/mikf/gallery-dl/issues/4493))
    - [instagram] add `following` extractor ([#1848](https://github.com/mikf/gallery-dl/issues/1848))
    - [pillowfort] support `/tagged/` URLs ([#4570](https://github.com/mikf/gallery-dl/issues/4570))
    - [pornhub] add `gif` support ([#4463](https://github.com/mikf/gallery-dl/issues/4463))
    - [reddit] add `previews` option ([#4322](https://github.com/mikf/gallery-dl/issues/4322))
    - [redgifs] add `niches` extractor ([#4311](https://github.com/mikf/gallery-dl/issues/4311), [#4312](https://github.com/mikf/gallery-dl/issues/4312))
    - [redgifs] support `order` parameter for user URLs ([#4583](https://github.com/mikf/gallery-dl/issues/4583))
    - [twitter] add `user` extractor and `include` option ([#4275](https://github.com/mikf/gallery-dl/issues/4275))
    - [twitter] add `tweet-endpoint` option ([#4307](https://github.com/mikf/gallery-dl/issues/4307))
    - [twitter] add `date_original` metadata for retweets ([#4337](https://github.com/mikf/gallery-dl/issues/4337), [#4443](https://github.com/mikf/gallery-dl/issues/4443))
    - [twitter] extract `source` metadata ([#4459](https://github.com/mikf/gallery-dl/issues/4459))
    - [twitter] support `x.com` URLs ([#4452](https://github.com/mikf/gallery-dl/issues/4452))
    #### Improvements
    - include `Referer` header in all HTTP requests ([#4490](https://github.com/mikf/gallery-dl/issues/4490), [#4518](https://github.com/mikf/gallery-dl/issues/4518))
      (can be disabled with `referer` option)
    - [behance] show errors for mature content ([#4417](https://github.com/mikf/gallery-dl/issues/4417))
    - [deviantart] re-add `quality` option and `/intermediary/` transform
    - [fantia] improve metadata extraction ([#4126](https://github.com/mikf/gallery-dl/issues/4126))
    - [instagram] better error messages for invalid users ([#4606](https://github.com/mikf/gallery-dl/issues/4606))
    - [mangadex] support multiple values for `lang` ([#4093](https://github.com/mikf/gallery-dl/issues/4093))
    - [mastodon] support `/@USER/following` URLs ([#4608](https://github.com/mikf/gallery-dl/issues/4608))
    - [moebooru] match search URLs with empty `tags` ([#4354](https://github.com/mikf/gallery-dl/issues/4354))
    - [pillowfort] extract `b2_lg_url` media ([#4570](https://github.com/mikf/gallery-dl/issues/4570))
    - [reddit] improve comment metadata ([#4482](https://github.com/mikf/gallery-dl/issues/4482))
    - [reddit] ignore `/message/compose` URLs ([#4482](https://github.com/mikf/gallery-dl/issues/4482), [#4581](https://github.com/mikf/gallery-dl/issues/4581))
    - [redgifs] provide `collection` metadata as separate field ([#4508](https://github.com/mikf/gallery-dl/issues/4508))
    - [redgifs] match `gfycat` image URLs ([#4558](https://github.com/mikf/gallery-dl/issues/4558))
    - [twitter] improve error messages for single Tweets ([#4369](https://github.com/mikf/gallery-dl/issues/4369))
    #### Fixes
    - [acidimg] fix extraction
    - [architizer] fix extraction ([#4537](https://github.com/mikf/gallery-dl/issues/4537))
    - [behance] fix and update `user` extractor ([#4417](https://github.com/mikf/gallery-dl/issues/4417))
    - [behance] fix cookie usage ([#4417](https://github.com/mikf/gallery-dl/issues/4417))
    - [behance] handle videos without `renditions` ([#4523](https://github.com/mikf/gallery-dl/issues/4523))
    - [bunkr] fix media domain for `cdn9` ([#4386](https://github.com/mikf/gallery-dl/issues/4386), [#4412](https://github.com/mikf/gallery-dl/issues/4412))
    - [bunkr] fix extracting `.wmv` files ([#4419](https://github.com/mikf/gallery-dl/issues/4419))
    - [bunkr] fix media domain for `cdn-pizza.bunkr.ru` ([#4489](https://github.com/mikf/gallery-dl/issues/4489))
    - [bunkr] fix extraction ([#4514](https://github.com/mikf/gallery-dl/issues/4514), [#4532](https://github.com/mikf/gallery-dl/issues/4532), [#4529](https://github.com/mikf/gallery-dl/issues/4529), [#4540](https://github.com/mikf/gallery-dl/issues/4540))
    - [deviantart] fix full resolution URLs for non-downloadable images ([#293](https://github.com/mikf/gallery-dl/issues/293), [#4548](https://github.com/mikf/gallery-dl/issues/4548), [#4563](https://github.com/mikf/gallery-dl/issues/4563))
    - [deviantart] fix shortened URLs ([#4316](https://github.com/mikf/gallery-dl/issues/4316))
    - [deviantart] fix search ([#4384](https://github.com/mikf/gallery-dl/issues/4384))
    - [deviantart] update Eclipse API endpoints ([#4553](https://github.com/mikf/gallery-dl/issues/4553), [#4615](https://github.com/mikf/gallery-dl/issues/4615))
    - [deviantart] use private tokens for `is_mature` posts ([#4563](https://github.com/mikf/gallery-dl/issues/4563))
    - [flickr] update default API credentials ([#4332](https://github.com/mikf/gallery-dl/issues/4332))
    - [giantessbooru] fix extraction ([#4373](https://github.com/mikf/gallery-dl/issues/4373))
    - [hiperdex] fix crash for titles containing Unicode characters ([#4325](https://github.com/mikf/gallery-dl/issues/4325))
    - [hiperdex] fix `manga` metadata
    - [imagefap] fix pagination ([#3013](https://github.com/mikf/gallery-dl/issues/3013))
    - [imagevenue] fix extraction ([#4473](https://github.com/mikf/gallery-dl/issues/4473))
    - [instagram] fix private posts with long shortcodes ([#4362](https://github.com/mikf/gallery-dl/issues/4362))
    - [instagram] fix video preview archive IDs ([#2135](https://github.com/mikf/gallery-dl/issues/2135), [#4455](https://github.com/mikf/gallery-dl/issues/4455))
    - [instagram] handle exceptions due to missing media ([#4555](https://github.com/mikf/gallery-dl/issues/4555))
    - [issuu] fix extraction ([#4420](https://github.com/mikf/gallery-dl/issues/4420))
    - [jpgfish] update domain to `jpg1.su` ([#4494](https://github.com/mikf/gallery-dl/issues/4494))
    - [kemonoparty] update `favorite` API endpoint ([#4522](https://github.com/mikf/gallery-dl/issues/4522))
    - [lensdump] fix extraction ([#4352](https://github.com/mikf/gallery-dl/issues/4352))
    - [mangakakalot] update domain
    - [reddit] fix `preview.redd.it` URLs ([#4470](https://github.com/mikf/gallery-dl/issues/4470))
    - [patreon] fix extraction ([#4547](https://github.com/mikf/gallery-dl/issues/4547))
    - [pixiv] handle errors for private novels ([#4481](https://github.com/mikf/gallery-dl/issues/4481))
    - [pornhub] fix extraction ([#4301](https://github.com/mikf/gallery-dl/issues/4301))
    - [pururin] fix extraction ([#4375](https://github.com/mikf/gallery-dl/issues/4375))
    - [subscribestar] fix preview detection ([#4468](https://github.com/mikf/gallery-dl/issues/4468))
    - [twitter] fix crash on private user ([#4349](https://github.com/mikf/gallery-dl/issues/4349))
    - [twitter] fix `TweetWithVisibilityResults` ([#4369](https://github.com/mikf/gallery-dl/issues/4369))
    - [twitter] fix crash when `sortIndex` is undefined ([#4499](https://github.com/mikf/gallery-dl/issues/4499))
    - [zerochan] fix `tags` extraction ([#4315](https://github.com/mikf/gallery-dl/issues/4315), [#4319](https://github.com/mikf/gallery-dl/issues/4319))
    #### Removals
    - [gfycat] remove module
    - [shimmie2] remove `meme.museum`
- ### Post Processors
    #### Changes
    - update `finalize` events
        - add `finalize-error` and `finalize-success` events that trigger
          depending on whether error(s) did or did not happen
        - change `finalize` to always trigger regardless of error status
    #### Additions
    - add `python` post processor
    - add `prepare-after` event ([#4083](https://github.com/mikf/gallery-dl/issues/4083))
    - [ugoira] add `"framerate": "uniform"` ([#4421](https://github.com/mikf/gallery-dl/issues/4421))
    #### Improvements
    - [ugoira] extend `ffmpeg-output` ([#4421](https://github.com/mikf/gallery-dl/issues/4421))
    #### Fixes
    - [ugoira] restore `libx264-prevent-odd` ([#4407](https://github.com/mikf/gallery-dl/issues/4407))
    - [ugoira] fix high frame rates ([#4421](https://github.com/mikf/gallery-dl/issues/4421))
- ### Downloaders
    #### Fixes
    - [http] close connection when file already exists ([#4403](https://github.com/mikf/gallery-dl/issues/4403))
- ### Options
    #### Additions
    - support `parent>child` categories for child extractor options,
      for example an `imgur` album from a `reddit` thread with `reddit>imgur`
    - implement `subconfigs` option ([#4440](https://github.com/mikf/gallery-dl/issues/4440))
    - add `"ascii+"` as a special `path-restrict` value ([#4371](https://github.com/mikf/gallery-dl/issues/4371))
    #### Removals
    - remove `pyopenssl` option
- ### Tests
    #### Improvements
    - move extractor results into their own, separate files ([#4504](https://github.com/mikf/gallery-dl/issues/4504))
    - include fallback URLs in content tests ([#3163](https://github.com/mikf/gallery-dl/issues/3163))
    - various test method improvements
- ### Miscellaneous
    #### Fixes
    - [formatter] use value of last alternative ([#4492](https://github.com/mikf/gallery-dl/issues/4492))
    - fix imports when running `__main__.py` ([#4581](https://github.com/mikf/gallery-dl/issues/4581))
    - fix symlink resolution in `__main__.py`
    - fix default Firefox user agent string

## 1.25.8 - 2023-07-15
### Changes
- update default User-Agent header to Firefox 115 ESR
### Additions
- [gfycat] support `@me` user ([#3770](https://github.com/mikf/gallery-dl/issues/3770), [#4271](https://github.com/mikf/gallery-dl/issues/4271))
- [gfycat] implement login support ([#3770](https://github.com/mikf/gallery-dl/issues/3770), [#4271](https://github.com/mikf/gallery-dl/issues/4271))
- [reddit] notify users about registering an OAuth application ([#4292](https://github.com/mikf/gallery-dl/issues/4292))
- [twitter] add `ratelimit` option ([#4251](https://github.com/mikf/gallery-dl/issues/4251))
- [twitter] use `TweetResultByRestId` endpoint that allows accessing single Tweets without login ([#4250](https://github.com/mikf/gallery-dl/issues/4250))
### Fixes
- [bunkr] use `.la` TLD for `media-files12` servers ([#4147](https://github.com/mikf/gallery-dl/issues/4147), [#4276](https://github.com/mikf/gallery-dl/issues/4276))
- [erome] ignore duplicate album IDs
- [fantia] send `X-Requested-With` header ([#4273](https://github.com/mikf/gallery-dl/issues/4273))
- [gelbooru_v01] fix `source` metadata ([#4302](https://github.com/mikf/gallery-dl/issues/4302), [#4303](https://github.com/mikf/gallery-dl/issues/4303))
- [gelbooru_v01] update `vidyart` domain
- [jpgfish] update domain to `jpeg.pet`
- [mangaread] fix `tags` metadata extraction
- [naverwebtoon] fix `comic` metadata extraction
- [newgrounds] extract & pass auth token during login ([#4268](https://github.com/mikf/gallery-dl/issues/4268))
- [paheal] fix extraction ([#4262](https://github.com/mikf/gallery-dl/issues/4262), [#4293](https://github.com/mikf/gallery-dl/issues/4293))
- [paheal] unescape `source`
- [philomena] fix `--range` ([#4288](https://github.com/mikf/gallery-dl/issues/4288))
- [philomena] handle `429 Too Many Requests` errors ([#4288](https://github.com/mikf/gallery-dl/issues/4288))
- [pornhub] set `accessAgeDisclaimerPH` cookie ([#4301](https://github.com/mikf/gallery-dl/issues/4301))
- [reddit] use 0.6s delay between API requests ([#4292](https://github.com/mikf/gallery-dl/issues/4292))
- [seiga] set `skip_fetish_warning` cookie ([#4242](https://github.com/mikf/gallery-dl/issues/4242))
- [slideshare] fix extraction
- [twitter] fix `following` extractor not getting all users ([#4287](https://github.com/mikf/gallery-dl/issues/4287))
- [twitter] use GraphQL search endpoint by default ([#4264](https://github.com/mikf/gallery-dl/issues/4264))
- [twitter] do not treat missing `TimelineAddEntries` instruction as fatal ([#4278](https://github.com/mikf/gallery-dl/issues/4278))
- [weibo] fix cursor based pagination
- [wikifeet] fix `tag` extraction ([#4289](https://github.com/mikf/gallery-dl/issues/4289), [#4291](https://github.com/mikf/gallery-dl/issues/4291))
### Removals
- [bcy] remove module
- [lineblog] remove module

## 1.25.7 - 2023-07-02
### Additions
- [flickr] add 'exif' option
- [flickr] add 'metadata' option ([#4227](https://github.com/mikf/gallery-dl/issues/4227))
- [mangapark] add 'source' option ([#3969](https://github.com/mikf/gallery-dl/issues/3969))
- [twitter] extend 'conversations' option ([#4211](https://github.com/mikf/gallery-dl/issues/4211))
### Fixes
- [furaffinity] improve 'description' HTML ([#4224](https://github.com/mikf/gallery-dl/issues/4224))
- [gelbooru_v01] fix '--range' ([#4167](https://github.com/mikf/gallery-dl/issues/4167))
- [hentaifox] fix titles containing '@' ([#4201](https://github.com/mikf/gallery-dl/issues/4201))
- [mangapark] update to v5 ([#3969](https://github.com/mikf/gallery-dl/issues/3969))
- [piczel] update API server address ([#4244](https://github.com/mikf/gallery-dl/issues/4244))
- [poipiku] improve error detection ([#4206](https://github.com/mikf/gallery-dl/issues/4206))
- [sankaku] improve warnings for unavailable posts
- [senmanga] ensure download URLs have a scheme ([#4235](https://github.com/mikf/gallery-dl/issues/4235))

## 1.25.6 - 2023-06-17
### Additions
- [blogger] download files from `lh*.googleusercontent.com` ([#4070](https://github.com/mikf/gallery-dl/issues/4070))
- [fantia] extract `plan` metadata ([#2477](https://github.com/mikf/gallery-dl/issues/2477))
- [fantia] emit warning for non-visible content sections ([#4128](https://github.com/mikf/gallery-dl/issues/4128))
- [furaffinity] extract `favorite_id` metadata ([#4133](https://github.com/mikf/gallery-dl/issues/4133))
- [jschan] add generic extractors for jschan image boards ([#3447](https://github.com/mikf/gallery-dl/issues/3447))
- [kemonoparty] support `.su` TLDs ([#4139](https://github.com/mikf/gallery-dl/issues/4139))
- [pixiv:novel] add `novel-bookmark` extractor ([#4111](https://github.com/mikf/gallery-dl/issues/4111))
- [pixiv:novel] add `full-series` option ([#4111](https://github.com/mikf/gallery-dl/issues/4111))
- [postimage] add gallery support, update image extractor ([#3115](https://github.com/mikf/gallery-dl/issues/3115), [#4134](https://github.com/mikf/gallery-dl/issues/4134))
- [redgifs] support galleries ([#4021](https://github.com/mikf/gallery-dl/issues/4021))
- [twitter] extract `conversation_id` metadata ([#3839](https://github.com/mikf/gallery-dl/issues/3839))
- [vipergirls] add login support ([#4166](https://github.com/mikf/gallery-dl/issues/4166))
- [vipergirls] use API endpoints ([#4166](https://github.com/mikf/gallery-dl/issues/4166))
- [formatter] implement `H` conversion ([#4164](https://github.com/mikf/gallery-dl/issues/4164))
### Fixes
- [acidimg] fix extraction ([#4136](https://github.com/mikf/gallery-dl/issues/4136))
- [bunkr] update domain to bunkrr.su ([#4159](https://github.com/mikf/gallery-dl/issues/4159), [#4189](https://github.com/mikf/gallery-dl/issues/4189))
- [bunkr] fix video downloads
- [fanbox] prevent exception due to missing embeds ([#4088](https://github.com/mikf/gallery-dl/issues/4088))
- [instagram] fix retrieving `/tagged` posts ([#4122](https://github.com/mikf/gallery-dl/issues/4122))
- [jpgfish] update domain to `jpg.pet` ([#4138](https://github.com/mikf/gallery-dl/issues/4138))
- [pixiv:novel] fix error with embeds extraction ([#4175](https://github.com/mikf/gallery-dl/issues/4175))
- [pornhub] improve redirect handling ([#4188](https://github.com/mikf/gallery-dl/issues/4188))
- [reddit] fix crash due to empty `crosspost_parent_lists` ([#4120](https://github.com/mikf/gallery-dl/issues/4120), [#4172](https://github.com/mikf/gallery-dl/issues/4172))
- [redgifs] update `search` URL pattern ([#4115](https://github.com/mikf/gallery-dl/issues/4115), [#4185](https://github.com/mikf/gallery-dl/issues/4185))
- [senmanga] fix and update ([#4160](https://github.com/mikf/gallery-dl/issues/4160))
- [twitter] use GraphQL API search endpoint ([#3942](https://github.com/mikf/gallery-dl/issues/3942))
- [wallhaven] improve HTTP error handling ([#4192](https://github.com/mikf/gallery-dl/issues/4192))
- [weibo] prevent fatal exception due to missing video data ([#4150](https://github.com/mikf/gallery-dl/issues/4150))
- [weibo] fix `.json` extension for some videos

## 1.25.5 - 2023-05-27
### Additions
- [8muses] add `parts` metadata field ([#3329](https://github.com/mikf/gallery-dl/issues/3329))
- [danbooru] add `date` metadata field ([#4047](https://github.com/mikf/gallery-dl/issues/4047))
- [e621] add `date` metadata field ([#4047](https://github.com/mikf/gallery-dl/issues/4047))
- [gofile] add basic password support ([#4056](https://github.com/mikf/gallery-dl/issues/4056))
- [imagechest] implement API support ([#4065](https://github.com/mikf/gallery-dl/issues/4065))
- [instagram] add `order-files` option ([#3993](https://github.com/mikf/gallery-dl/issues/3993), [#4017](https://github.com/mikf/gallery-dl/issues/4017))
- [instagram] add `order-posts` option ([#3993](https://github.com/mikf/gallery-dl/issues/3993), [#4017](https://github.com/mikf/gallery-dl/issues/4017))
- [instagram] add `metadata` option ([#3107](https://github.com/mikf/gallery-dl/issues/3107))
- [jpgfish] add `jpg.fishing` extractors ([#2657](https://github.com/mikf/gallery-dl/issues/2657), [#2719](https://github.com/mikf/gallery-dl/issues/2719))
- [lensdump] add `lensdump.com` extractors ([#2078](https://github.com/mikf/gallery-dl/issues/2078), [#4104](https://github.com/mikf/gallery-dl/issues/4104))
- [mangaread] add `mangaread.org` extractors ([#2425](https://github.com/mikf/gallery-dl/issues/2425), [#2781](https://github.com/mikf/gallery-dl/issues/2781))
- [misskey] add `favorite` extractor ([#3950](https://github.com/mikf/gallery-dl/issues/3950))
- [pixiv] add `novel` support ([#1241](https://github.com/mikf/gallery-dl/issues/1241), [#4044](https://github.com/mikf/gallery-dl/issues/4044))
- [reddit] support cross-posted media ([#887](https://github.com/mikf/gallery-dl/issues/887), [#3586](https://github.com/mikf/gallery-dl/issues/3586), [#3976](https://github.com/mikf/gallery-dl/issues/3976))
- [postprocessor:exec] support tilde expansion for `command`
- [formatter] support slicing strings as bytes ([#4087](https://github.com/mikf/gallery-dl/issues/4087))
### Fixes
- [8muses] fix value of `album[url]` ([#3329](https://github.com/mikf/gallery-dl/issues/3329))
- [danbooru] refactor pagination logic ([#4002](https://github.com/mikf/gallery-dl/issues/4002))
- [fanbox] skip invalid posts ([#4088](https://github.com/mikf/gallery-dl/issues/4088))
- [gofile] automatically fetch `website-token`
- [kemonoparty] fix kemono and coomer logins sharing the same cache ([#4098](https://github.com/mikf/gallery-dl/issues/4098))
- [newgrounds] add default delay between requests ([#4046](https://github.com/mikf/gallery-dl/issues/4046))
- [nsfwalbum] detect placeholder images
- [poipiku] extract full `descriptions` ([#4066](https://github.com/mikf/gallery-dl/issues/4066))
- [tcbscans] update domain to `tcbscans.com` ([#4080](https://github.com/mikf/gallery-dl/issues/4080))
- [twitter] extract TwitPic URLs in text ([#3792](https://github.com/mikf/gallery-dl/issues/3792), [#3796](https://github.com/mikf/gallery-dl/issues/3796))
- [weibo] require numeric IDs to have length >= 10 ([#4059](https://github.com/mikf/gallery-dl/issues/4059))
- [ytdl] fix crash due to removed `no_color` attribute
- [cookies] improve logging behavior ([#4050](https://github.com/mikf/gallery-dl/issues/4050))

## 1.25.4 - 2023-05-07
### Additions
- [4chanarchives] add `thread` and `board` extractors ([#4012](https://github.com/mikf/gallery-dl/issues/4012))
- [foolfuuka] add `archive.palanq.win`
- [imgur] add `favorite-folder` extractor ([#4016](https://github.com/mikf/gallery-dl/issues/4016))
- [mangadex] add `status` and `tags` metadata ([#4031](https://github.com/mikf/gallery-dl/issues/4031))
- allow selecting a domain with `--cookies-from-browser`
- add `--cookies-export` command-line option
- add `-C` as short option for `--cookies`
- include exception type in config error messages
### Fixes
- [exhentai] update sadpanda check
- [imagechest] load all images when a "Load More" button is present ([#4028](https://github.com/mikf/gallery-dl/issues/4028))
- [imgur] fix bug causing some images/albums from user profiles and favorites to be ignored
- [pinterest] update endpoint for related board pins
- [pinterest] fix `pin.it` extractor
- [ytdl] fix yt-dlp `--xff/--geo-bypass` tests ([#3989](https://github.com/mikf/gallery-dl/issues/3989))
### Removals
- [420chan] remove module
- [foolfuuka] remove `archive.alice.al` and `tokyochronos.net`
- [foolslide] remove `sensescans.com`
- [nana] remove module

## 1.25.3 - 2023-04-30
### Additions
- [imagefap] extract `description` and `categories` metadata ([#3905](https://github.com/mikf/gallery-dl/issues/3905))
- [imxto] add `gallery` extractor ([#1289](https://github.com/mikf/gallery-dl/issues/1289))
- [itchio] add `game` extractor ([#3923](https://github.com/mikf/gallery-dl/issues/3923))
- [nitter] extract user IDs from encoded banner URLs
- [pixiv] allow sorting search results by popularity ([#3970](https://github.com/mikf/gallery-dl/issues/3970))
- [reddit] match `preview.redd.it` URLs ([#3935](https://github.com/mikf/gallery-dl/issues/3935))
- [sankaku] support post URLs with MD5 hashes ([#3952](https://github.com/mikf/gallery-dl/issues/3952))
- [shimmie2] add generic extractors for Shimmie2 sites ([#3734](https://github.com/mikf/gallery-dl/issues/3734), [#943](https://github.com/mikf/gallery-dl/issues/943))
- [tumblr] add `day` extractor ([#3951](https://github.com/mikf/gallery-dl/issues/3951))
- [twitter] support `profile-conversation` entries ([#3938](https://github.com/mikf/gallery-dl/issues/3938))
- [vipergirls] add `thread` and `post` extractors ([#3812](https://github.com/mikf/gallery-dl/issues/3812), [#2720](https://github.com/mikf/gallery-dl/issues/2720), [#731](https://github.com/mikf/gallery-dl/issues/731))
- [downloader:http] add `consume-content` option ([#3748](https://github.com/mikf/gallery-dl/issues/3748))
### Fixes
- [2chen] update domain to sturdychan.help
- [behance] fix extraction ([#3980](https://github.com/mikf/gallery-dl/issues/3980))
- [deviantart] retry downloads with private token ([#3941](https://github.com/mikf/gallery-dl/issues/3941))
- [imagefap] fix empty `tags` metadata
- [manganelo] support arbitrary minor version separators ([#3972](https://github.com/mikf/gallery-dl/issues/3972))
- [nozomi] fix file URLs ([#3925](https://github.com/mikf/gallery-dl/issues/3925))
- [oauth] catch exceptions from `webbrowser.get()` ([#3947](https://github.com/mikf/gallery-dl/issues/3947))
- [pixiv] fix `pixivision` extraction
- [reddit] ignore `id-max` value `"zik0zj"`/`2147483647` ([#3939](https://github.com/mikf/gallery-dl/issues/3939), [#3862](https://github.com/mikf/gallery-dl/issues/3862), [#3697](https://github.com/mikf/gallery-dl/issues/3697), [#3606](https://github.com/mikf/gallery-dl/issues/3606), [#3546](https://github.com/mikf/gallery-dl/issues/3546), [#3521](https://github.com/mikf/gallery-dl/issues/3521), [#3412](https://github.com/mikf/gallery-dl/issues/3412))
- [sankaku] sanitize `date:` tags ([#1790](https://github.com/mikf/gallery-dl/issues/1790))
- [tumblr] fix and update pagination logic ([#2191](https://github.com/mikf/gallery-dl/issues/2191))
- [twitter] fix `user` metadata when downloading quoted Tweets ([#3922](https://github.com/mikf/gallery-dl/issues/3922))
- [ytdl] fix crash due to `--geo-bypass` deprecation ([#3975](https://github.com/mikf/gallery-dl/issues/3975))
- [postprocessor:metadata] support putting keys in quotes
- include more optional dependencies in executables ([#3907](https://github.com/mikf/gallery-dl/issues/3907))

## 1.25.2 - 2023-04-15
### Additions
- [deviantart] add `public` option
- [nitter] extract videos from `source` elements ([#3912](https://github.com/mikf/gallery-dl/issues/3912))
- [twitter] add `date_liked` and `date_bookmarked` metadata for liked and bookmarked Tweets ([#3816](https://github.com/mikf/gallery-dl/issues/3816))
- [urlshortener] add support for bit.ly & t.co ([#3841](https://github.com/mikf/gallery-dl/issues/3841))
- [downloader:http] add MIME type and signature for `.heic` files ([#3915](https://github.com/mikf/gallery-dl/issues/3915))
### Fixes
- [blogger] update regex to get the highest resolution URLs ([#3863](https://github.com/mikf/gallery-dl/issues/3863), [#3870](https://github.com/mikf/gallery-dl/issues/3870))
- [bunkr] update domain to `bunkr.la` ([#3813](https://github.com/mikf/gallery-dl/issues/3813), [#3877](https://github.com/mikf/gallery-dl/issues/3877))
- [deviantart] keep using private access tokens when requesting download URLs ([#3845](https://github.com/mikf/gallery-dl/issues/3845), [#3857](https://github.com/mikf/gallery-dl/issues/3857), [#3896](https://github.com/mikf/gallery-dl/issues/3896))
- [hentaifoundry] fix content filters ([#3887](https://github.com/mikf/gallery-dl/issues/3887))
- [hotleak] fix downloading of creators whose name starts with a category name ([#3871](https://github.com/mikf/gallery-dl/issues/3871))
- [imagechest] fix extraction ([#3914](https://github.com/mikf/gallery-dl/issues/3914))
- [realbooru] fix extraction ([#2530](https://github.com/mikf/gallery-dl/issues/2530))
- [sexcom] fix pagination ([#3906](https://github.com/mikf/gallery-dl/issues/3906))
- [sexcom] fix HD video extraction
- [shopify] fix `collection` extractor ([#3866](https://github.com/mikf/gallery-dl/issues/3866), [#3868](https://github.com/mikf/gallery-dl/issues/3868))
- [twitter] update to bookmark timeline v2 ([#3859](https://github.com/mikf/gallery-dl/issues/3859), [#3854](https://github.com/mikf/gallery-dl/issues/3854))
- [twitter] warn about "withheld" Tweets and users ([#3864](https://github.com/mikf/gallery-dl/issues/3864))
### Improvements
- [danbooru] reduce number of API requests when fetching extended `metadata`
- [deviantart:search] detect login redirects ([#3860](https://github.com/mikf/gallery-dl/issues/3860))
- [generic] write regular expressions without `x` flags
- [mastodon] try to get account IDs without access token
- [twitter] calculate `date` from Tweet IDs

## 1.25.1 - 2023-03-25
### Additions
- [nitter] support nitter.it ([#3819](https://github.com/mikf/gallery-dl/issues/3819))
- [twitter] add `hashtag` extractor ([#3783](https://github.com/mikf/gallery-dl/issues/3783))
- [twitter] support Tweet content with >280 characters
- [formatter] support loading f-strings from template files ([#3800](https://github.com/mikf/gallery-dl/issues/3800))
- [formatter] support filesystem paths for `\fM` modules ([#3399](https://github.com/mikf/gallery-dl/issues/3399))
- [formatter] support putting keys in quotes (e.g. `user['name']`) ([#2559](https://github.com/mikf/gallery-dl/issues/2559))
- [postprocessor:metadata] add `skip` option ([#3786](https://github.com/mikf/gallery-dl/issues/3786))
### Fixes
- [output] set `errors=replace` for output streams ([#3765](https://github.com/mikf/gallery-dl/issues/3765))
- [gelbooru] extract favorites without needing cookies ([#3704](https://github.com/mikf/gallery-dl/issues/3704))
- [gelbooru] fix and improve `--range` for pools
- [hiperdex] fix extraction ([#3768](https://github.com/mikf/gallery-dl/issues/3768))
- [naverwebtoon] fix extraction ([#3729](https://github.com/mikf/gallery-dl/issues/3729))
- [nitter] fix extraction for instances without user banners
- [twitter] update API query hashes and parameters
- [weibo] support `mix_media_info` entries ([#3793](https://github.com/mikf/gallery-dl/issues/3793))
- fix circular reference detection for `-K`
### Changes
- update `globals` instead of overwriting the default ([#3773](https://github.com/mikf/gallery-dl/issues/3773))

## 1.25.0 - 2023-03-11
### Changes
- [e621] split `e621` extractors from `danbooru` module ([#3425](https://github.com/mikf/gallery-dl/issues/3425))
- [deviantart] remove mature scraps warning ([#3691](https://github.com/mikf/gallery-dl/issues/3691))
- [deviantart] use `/collections/all` endpoint for favorites ([#3666](https://github.com/mikf/gallery-dl/issues/3666), [#3668](https://github.com/mikf/gallery-dl/issues/3668))
- [newgrounds] update default image and audio archive IDs to prevent ID overlap ([#3681](https://github.com/mikf/gallery-dl/issues/3681))
- rename `--ignore-config` to `--config-ignore`
### Extractors
- [catbox] add `file` extractor ([#3570](https://github.com/mikf/gallery-dl/issues/3570))
- [deviantart] add `search` extractor ([#538](https://github.com/mikf/gallery-dl/issues/538), [#1264](https://github.com/mikf/gallery-dl/issues/1264), [#2954](https://github.com/mikf/gallery-dl/issues/2954), [#2970](https://github.com/mikf/gallery-dl/issues/2970), [#3577](https://github.com/mikf/gallery-dl/issues/3577))
- [deviantart] add `gallery-search` extractor ([#1695](https://github.com/mikf/gallery-dl/issues/1695))
- [deviantart] support `fxdeviantart.com` URLs (##3740)
- [e621] implement `notes` and `pools` metadata extraction ([#3425](https://github.com/mikf/gallery-dl/issues/3425))
- [gelbooru] add `favorite` extractor ([#3704](https://github.com/mikf/gallery-dl/issues/3704))
- [imagetwist] support `phun.imagetwist.com` and `imagehaha.com` domains ([#3622](https://github.com/mikf/gallery-dl/issues/3622))
- [instagram] add `user` metadata field ([#3107](https://github.com/mikf/gallery-dl/issues/3107))
- [manganelo] update and fix metadata extraction
- [manganelo] support mobile-only chapters
- [mangasee] extract `author` and `genre` metadata ([#3703](https://github.com/mikf/gallery-dl/issues/3703))
- [misskey] add `misskey` extractors ([#3717](https://github.com/mikf/gallery-dl/issues/3717))
- [pornpics] add `gallery` and `search` extractors ([#263](https://github.com/mikf/gallery-dl/issues/263), [#3544](https://github.com/mikf/gallery-dl/issues/3544), [#3654](https://github.com/mikf/gallery-dl/issues/3654))
- [redgifs] support v3 URLs ([#3588](https://github.com/mikf/gallery-dl/issues/3588). [#3589](https://github.com/mikf/gallery-dl/issues/3589))
- [redgifs] add `collection` extractors ([#3427](https://github.com/mikf/gallery-dl/issues/3427), [#3662](https://github.com/mikf/gallery-dl/issues/3662))
- [shopify] support ohpolly.com ([#440](https://github.com/mikf/gallery-dl/issues/440), [#3596](https://github.com/mikf/gallery-dl/issues/3596))
- [szurubooru] add `tag` and `post` extractors ([#3583](https://github.com/mikf/gallery-dl/issues/3583), [#3713](https://github.com/mikf/gallery-dl/issues/3713))
- [twitter] add `transform` option
### Options
- [postprocessor:metadata] add `sort` and `separators` options
- [postprocessor:exec] implement archive options ([#3584](https://github.com/mikf/gallery-dl/issues/3584))
- add `--config-create` command-line option ([#2333](https://github.com/mikf/gallery-dl/issues/2333))
- add `--config-toml` command-line option to load config files in TOML format
- add `output.stdout`, `output.stdin`, and `output.stderr` options ([#1621](https://github.com/mikf/gallery-dl/issues/1621), [#2152](https://github.com/mikf/gallery-dl/issues/2152), [#2529](https://github.com/mikf/gallery-dl/issues/2529))
- add `hash_md5` and `hash_sha1` functions ([#3679](https://github.com/mikf/gallery-dl/issues/3679))
- implement `globals` option to enable defining custom functions for `eval` statements
- implement `archive-pragma` option to use SQLite PRAGMA statements
- implement `actions` to trigger events on logging messages ([#3338](https://github.com/mikf/gallery-dl/issues/3338), [#3630](https://github.com/mikf/gallery-dl/issues/3630))
- implement ability to load external extractor classes
  - `-X/--extractors` command-line options
  - `extractor.modules-sources` config option
### Fixes
- [bunkr] fix extraction ([#3636](https://github.com/mikf/gallery-dl/issues/3636), [#3655](https://github.com/mikf/gallery-dl/issues/3655))
- [danbooru] send gallery-dl User-Agent ([#3665](https://github.com/mikf/gallery-dl/issues/3665))
- [deviantart] fix crash when handling deleted deviations in status updates ([#3656](https://github.com/mikf/gallery-dl/issues/3656))
- [fanbox] fix crash with missing images ([#3673](https://github.com/mikf/gallery-dl/issues/3673))
- [imagefap] update `gallery` URLs ([#3595](https://github.com/mikf/gallery-dl/issues/3595))
- [imagefap] fix infinite pagination loop ([#3594](https://github.com/mikf/gallery-dl/issues/3594))
- [imagefap] fix metadata extraction
- [oauth] use default name for browsers without `name` attribute
- [pinterest] unescape search terms ([#3621](https://github.com/mikf/gallery-dl/issues/3621))
- [pixiv] fix `--write-tags` for `"tags": "original"` ([#3675](https://github.com/mikf/gallery-dl/issues/3675))
- [poipiku] warn about incorrect passwords ([#3646](https://github.com/mikf/gallery-dl/issues/3646))
- [reddit] update `videos` option ([#3712](https://github.com/mikf/gallery-dl/issues/3712))
- [soundgasm] rewrite ([#3578](https://github.com/mikf/gallery-dl/issues/3578))
- [telegraph] fix extraction when images are not in `<figure>` elements ([#3590](https://github.com/mikf/gallery-dl/issues/3590))
- [tumblr] raise more detailed errors for dashboard-only blogs ([#3628](https://github.com/mikf/gallery-dl/issues/3628))
- [twitter] fix some `original` retweets not downloading ([#3744](https://github.com/mikf/gallery-dl/issues/3744))
- [ytdl] fix `--parse-metadata` ([#3663](https://github.com/mikf/gallery-dl/issues/3663))
- [downloader:ytdl] prevent exception on empty results
### Improvements
- [downloader:http] use `time.monotonic()`
- [downloader:http] update `_http_retry` to accept a Python function ([#3569](https://github.com/mikf/gallery-dl/issues/3569))
- [postprocessor:metadata] speed up JSON encoding
- replace `json.loads/dumps` with direct calls to `JSONDecoder.decode/JSONEncoder.encode`
- improve `option.Formatter` performance
### Removals
- [nitter] remove `nitter.pussthecat.org`

## 1.24.5 - 2023-01-28
### Additions
- [booru] add `url` option
- [danbooru] extend `metadata` option ([#3505](https://github.com/mikf/gallery-dl/issues/3505))
- [deviantart] add extractor for status updates ([#3539](https://github.com/mikf/gallery-dl/issues/3539), [#3541](https://github.com/mikf/gallery-dl/issues/3541))
- [deviantart] add support for `/deviation/` and `fav.me` URLs ([#3558](https://github.com/mikf/gallery-dl/issues/3558), [#3560](https://github.com/mikf/gallery-dl/issues/3560))
- [kemonoparty] extract `hash` metadata for discord files ([#3531](https://github.com/mikf/gallery-dl/issues/3531))
- [lexica] add `search` extractor ([#3567](https://github.com/mikf/gallery-dl/issues/3567))
- [mastodon] add `num` and `count` metadata fields ([#3517](https://github.com/mikf/gallery-dl/issues/3517))
- [nudecollect] add `image` and `album` extractors ([#2430](https://github.com/mikf/gallery-dl/issues/2430), [#2818](https://github.com/mikf/gallery-dl/issues/2818), [#3575](https://github.com/mikf/gallery-dl/issues/3575))
- [wikifeet] add `gallery` extractor ([#519](https://github.com/mikf/gallery-dl/issues/519), [#3537](https://github.com/mikf/gallery-dl/issues/3537))
- [downloader:http] add signature checks for `.blend`, `.obj`, and `.clip` files ([#3535](https://github.com/mikf/gallery-dl/issues/3535))
- add `extractor.retry-codes` option
- add `-O/--postprocessor-option` command-line option ([#3565](https://github.com/mikf/gallery-dl/issues/3565))
- improve `write-pages` output
### Fixes
- [bunkr] fix downloading `.mkv` and `.ts` files ([#3571](https://github.com/mikf/gallery-dl/issues/3571))
- [fantia] send `X-CSRF-Token` headers ([#3576](https://github.com/mikf/gallery-dl/issues/3576))
- [generic] fix regex for non-src image URLs ([#3555](https://github.com/mikf/gallery-dl/issues/3555))
- [hiperdex] update domain ([#3572](https://github.com/mikf/gallery-dl/issues/3572))
- [hotleak] fix video URLs ([#3516](https://github.com/mikf/gallery-dl/issues/3516), [#3525](https://github.com/mikf/gallery-dl/issues/3525), [#3563](https://github.com/mikf/gallery-dl/issues/3563), [#3581](https://github.com/mikf/gallery-dl/issues/3581))
- [instagram] always show `cursor` value after errors ([#3440](https://github.com/mikf/gallery-dl/issues/3440))
- [instagram] update API domain, headers, and csrf token handling
- [oauth] show `client-id`/`api-key` values ([#3518](https://github.com/mikf/gallery-dl/issues/3518))
- [philomena] match URLs with www subdomain
- [sankaku] update URL pattern ([#3523](https://github.com/mikf/gallery-dl/issues/3523))
- [twitter] refresh guest tokens ([#3445](https://github.com/mikf/gallery-dl/issues/3445), [#3458](https://github.com/mikf/gallery-dl/issues/3458))
- [twitter] fix search pagination ([#3536](https://github.com/mikf/gallery-dl/issues/3536), [#3534](https://github.com/mikf/gallery-dl/issues/3534), [#3549](https://github.com/mikf/gallery-dl/issues/3549))
- [twitter] use `"browser": "firefox"` by default ([#3522](https://github.com/mikf/gallery-dl/issues/3522))

## 1.24.4 - 2023-01-11
### Additions
- [downloader:http] add `validate` option
### Fixes
- [kemonoparty] fix regression from commit 473bd380 ([#3519](https://github.com/mikf/gallery-dl/issues/3519))

## 1.24.3 - 2023-01-10
### Additions
- [danbooru] extract `uploader` metadata ([#3457](https://github.com/mikf/gallery-dl/issues/3457))
- [deviantart] initial implementation of username & password login for `scraps` ([#1029](https://github.com/mikf/gallery-dl/issues/1029))
- [fanleaks] add `post` and `model` extractors ([#3468](https://github.com/mikf/gallery-dl/issues/3468), [#3474](https://github.com/mikf/gallery-dl/issues/3474))
- [imagefap] add `folder` extractor ([#3504](https://github.com/mikf/gallery-dl/issues/3504))
- [lynxchan] support `bbw-chan.nl` ([#3456](https://github.com/mikf/gallery-dl/issues/3456), [#3463](https://github.com/mikf/gallery-dl/issues/3463))
- [pinterest] support `All Pins` boards ([#2855](https://github.com/mikf/gallery-dl/issues/2855), [#3484](https://github.com/mikf/gallery-dl/issues/3484))
- [pinterest] add `domain` option ([#3484](https://github.com/mikf/gallery-dl/issues/3484))
- [pixiv] implement `metadata-bookmark` option ([#3417](https://github.com/mikf/gallery-dl/issues/3417))
- [tcbscans] add `chapter` and `manga` extractors ([#3189](https://github.com/mikf/gallery-dl/issues/3189))
- [twitter] implement `syndication=extended` ([#3483](https://github.com/mikf/gallery-dl/issues/3483))
- implement slice notation for `range` options ([#918](https://github.com/mikf/gallery-dl/issues/918), [#2865](https://github.com/mikf/gallery-dl/issues/2865))
- allow `filter` options to be a list of expressions
### Fixes
- [behance] use delay between requests ([#2507](https://github.com/mikf/gallery-dl/issues/2507))
- [bunkr] fix URLs returned by API ([#3481](https://github.com/mikf/gallery-dl/issues/3481))
- [fanbox] return `imageMap` files in order ([#2718](https://github.com/mikf/gallery-dl/issues/2718))
- [imagefap] use delay between requests ([#1140](https://github.com/mikf/gallery-dl/issues/1140))
- [imagefap] warn about redirects to `/human-verification` ([#1140](https://github.com/mikf/gallery-dl/issues/1140))
- [kemonoparty] reject invalid/empty files ([#3510](https://github.com/mikf/gallery-dl/issues/3510))
- [myhentaigallery] handle whitespace before title tag ([#3503](https://github.com/mikf/gallery-dl/issues/3503))
- [poipiku] fix extraction for a different warning button style ([#3493](https://github.com/mikf/gallery-dl/issues/3493), [#3460](https://github.com/mikf/gallery-dl/issues/3460))
- [poipiku] warn about login requirements
- [telegraph] fix file URLs ([#3506](https://github.com/mikf/gallery-dl/issues/3506))
- [twitter] fix crash when using `expand` and `syndication` ([#3473](https://github.com/mikf/gallery-dl/issues/3473))
- [twitter] apply tweet type checks before uniqueness check ([#3439](https://github.com/mikf/gallery-dl/issues/3439), [#3455](https://github.com/mikf/gallery-dl/issues/3455))
- [twitter] force `https://` for TwitPic URLs ([#3449](https://github.com/mikf/gallery-dl/issues/3449))
- [ytdl] adapt to yt-dlp changes
- update and improve documentation ([#3453](https://github.com/mikf/gallery-dl/issues/3453), [#3462](https://github.com/mikf/gallery-dl/issues/3462), [#3496](https://github.com/mikf/gallery-dl/issues/3496))

## 1.24.2 - 2022-12-18
### Additions
- [2chen] support `.club` URLs ([#3406](https://github.com/mikf/gallery-dl/issues/3406))
- [deviantart] extract sta.sh URLs from `text_content` ([#3366](https://github.com/mikf/gallery-dl/issues/3366))
- [deviantart] add `/view` URL support ([#3367](https://github.com/mikf/gallery-dl/issues/3367))
- [e621] implement `threshold` option to control pagination ([#3413](https://github.com/mikf/gallery-dl/issues/3413))
- [fapello] add `post`, `user` and `path` extractors ([#3065](https://github.com/mikf/gallery-dl/issues/3065), [#3360](https://github.com/mikf/gallery-dl/issues/3360), [#3415](https://github.com/mikf/gallery-dl/issues/3415))
- [imgur] add support for imgur.io URLs ([#3419](https://github.com/mikf/gallery-dl/issues/3419))
- [lynxchan] add generic extractors for lynxchan imageboards ([#3389](https://github.com/mikf/gallery-dl/issues/3389), [#3394](https://github.com/mikf/gallery-dl/issues/3394))
- [mangafox] extract more metadata ([#3167](https://github.com/mikf/gallery-dl/issues/3167))
- [pixiv] extract `date_url` metadata ([#3405](https://github.com/mikf/gallery-dl/issues/3405))
- [soundgasm] add `audio` and `user` extractors ([#3384](https://github.com/mikf/gallery-dl/issues/3384), [#3388](https://github.com/mikf/gallery-dl/issues/3388))
- [webmshare] add `video` extractor ([#2410](https://github.com/mikf/gallery-dl/issues/2410))
- support Firefox containers for `--cookies-from-browser` ([#3346](https://github.com/mikf/gallery-dl/issues/3346))
### Fixes
- [2chen] fix file URLs
- [bunkr] update domain ([#3391](https://github.com/mikf/gallery-dl/issues/3391))
- [exhentai] fix pagination
- [imagetwist] fix extraction
- [imgth] rewrite
- [instagram] prevent post `date` overwriting file `date` ([#3392](https://github.com/mikf/gallery-dl/issues/3392))
- [khinsider] fix metadata extraction
- [komikcast] update domain and fix extraction
- [reddit] increase `id-max` default value ([#3397](https://github.com/mikf/gallery-dl/issues/3397))
- [seiga] raise error when redirected to login page ([#3401](https://github.com/mikf/gallery-dl/issues/3401))
- [sexcom] fix video URLs ([#3408](https://github.com/mikf/gallery-dl/issues/3408), [#3414](https://github.com/mikf/gallery-dl/issues/3414))
- [twitter] update `search` pagination ([#544](https://github.com/mikf/gallery-dl/issues/544))
- [warosu] fix and update
- [zerochan] update for layout v3
- restore paths for archived files ([#3362](https://github.com/mikf/gallery-dl/issues/3362), [#3377](https://github.com/mikf/gallery-dl/issues/3377))
- use `util.NONE` as `keyword-default` default value ([#3334](https://github.com/mikf/gallery-dl/issues/3334))
### Removals
- [foolslide] remove `kireicake`
- [kissgoddess] remove module

## 1.24.1 - 2022-12-04
### Additions
- [artstation] add `pro-first` option ([#3273](https://github.com/mikf/gallery-dl/issues/3273))
- [artstation] add `max-posts` option ([#3270](https://github.com/mikf/gallery-dl/issues/3270))
- [fapachi] add `post` and `user` extractors ([#3339](https://github.com/mikf/gallery-dl/issues/3339), [#3347](https://github.com/mikf/gallery-dl/issues/3347))
- [inkbunny] provide additional metadata ([#3274](https://github.com/mikf/gallery-dl/issues/3274))
- [nitter] add `retweets` option ([#3278](https://github.com/mikf/gallery-dl/issues/3278))
- [nitter] add `videos` option ([#3279](https://github.com/mikf/gallery-dl/issues/3279))
- [nitter] support `/i/web/` and `/i/user/` URLs ([#3310](https://github.com/mikf/gallery-dl/issues/3310))
- [pixhost] add `gallery` support ([#3336](https://github.com/mikf/gallery-dl/issues/3336), [#3353](https://github.com/mikf/gallery-dl/issues/3353))
- [weibo] add `count` metadata field ([#3305](https://github.com/mikf/gallery-dl/issues/3305))
- [downloader:http] add `retry-codes` option ([#3313](https://github.com/mikf/gallery-dl/issues/3313))
- [formatter] implement `S` format specifier to sort lists ([#3266](https://github.com/mikf/gallery-dl/issues/3266))
- implement `version-metadata` option ([#3201](https://github.com/mikf/gallery-dl/issues/3201))
### Fixes
- [2chen] fix extraction ([#3354](https://github.com/mikf/gallery-dl/issues/3354), [#3356](https://github.com/mikf/gallery-dl/issues/3356))
- [bcy] fix JSONDecodeError ([#3321](https://github.com/mikf/gallery-dl/issues/3321))
- [bunkr] fix video downloads ([#3326](https://github.com/mikf/gallery-dl/issues/3326), [#3335](https://github.com/mikf/gallery-dl/issues/3335))
- [bunkr] use `media-files` servers for more file types
- [itaku] remove `Extreme` rating ([#3285](https://github.com/mikf/gallery-dl/issues/3285), [#3287](https://github.com/mikf/gallery-dl/issues/3287))
- [hitomi] apply format check for every image ([#3280](https://github.com/mikf/gallery-dl/issues/3280))
- [hotleak] fix UnboundLocalError ([#3288](https://github.com/mikf/gallery-dl/issues/3288), [#3293](https://github.com/mikf/gallery-dl/issues/3293))
- [nitter] sanitize filenames ([#3294](https://github.com/mikf/gallery-dl/issues/3294))
- [nitter] retry downloads on 404 ([#3313](https://github.com/mikf/gallery-dl/issues/3313))
- [nitter] set `hlsPlayback` cookie
- [patreon] fix `403 Forbidden` errors ([#3341](https://github.com/mikf/gallery-dl/issues/3341))
- [patreon] improve `campaign_id` extraction ([#3235](https://github.com/mikf/gallery-dl/issues/3235))
- [patreon] update API query parameters
- [pixiv] preserve `tags` order ([#3266](https://github.com/mikf/gallery-dl/issues/3266))
- [reddit] use `dash_url` for videos ([#3258](https://github.com/mikf/gallery-dl/issues/3258), [#3306](https://github.com/mikf/gallery-dl/issues/3306))
- [twitter] fix error when using user IDs for suspended accounts
- [weibo] fix bug with empty `playback_list` ([#3301](https://github.com/mikf/gallery-dl/issues/3301))
- [downloader:http] fix potential `ZeroDivisionError` ([#3328](https://github.com/mikf/gallery-dl/issues/3328))
### Removals
- [lolisafe] remove `zz.ht`

## 1.24.0 - 2022-11-20
### Additions
- [exhentai] add metadata to search results ([#3181](https://github.com/mikf/gallery-dl/issues/3181))
- [gelbooru_v02] implement `notes` extraction
- [instagram] add `guide` extractor ([#3192](https://github.com/mikf/gallery-dl/issues/3192))
- [lolisafe] add support for xbunkr ([#3153](https://github.com/mikf/gallery-dl/issues/3153), [#3156](https://github.com/mikf/gallery-dl/issues/3156))
- [mastodon] add `instance_remote` metadata field ([#3119](https://github.com/mikf/gallery-dl/issues/3119))
- [nitter] add extractors for Nitter instances ([#2415](https://github.com/mikf/gallery-dl/issues/2415), [#2696](https://github.com/mikf/gallery-dl/issues/2696))
- [pixiv] add support for new daily AI rankings category ([#3214](https://github.com/mikf/gallery-dl/issues/3214), [#3221](https://github.com/mikf/gallery-dl/issues/3221))
- [twitter] add `avatar` and `background` extractors ([#349](https://github.com/mikf/gallery-dl/issues/349), [#3023](https://github.com/mikf/gallery-dl/issues/3023))
- [uploadir] add support for `uploadir.com` ([#3162](https://github.com/mikf/gallery-dl/issues/3162))
- [wallhaven] add `user` extractor ([#3212](https://github.com/mikf/gallery-dl/issues/3212), [#3213](https://github.com/mikf/gallery-dl/issues/3213), [#3226](https://github.com/mikf/gallery-dl/issues/3226))
- [downloader:http] add `chunk-size` option ([#3143](https://github.com/mikf/gallery-dl/issues/3143))
- [downloader:http] add file signature check for `.mp4` files
- [downloader:http] add file signature check and MIME type for `.avif` files
- [postprocessor] implement `post-after` event ([#3117](https://github.com/mikf/gallery-dl/issues/3117))
- [postprocessor:metadata] implement `"mode": "jsonl"`
- [postprocessor:metadata] add `open`, `encoding`, and `private` options
- add `--chunk-size` command-line option ([#3143](https://github.com/mikf/gallery-dl/issues/3143))
- add `--user-agent` command-line option
- implement `http-metadata` option
- implement `"user-agent": "browser"` ([#2636](https://github.com/mikf/gallery-dl/issues/2636))
### Changes
- [deviantart] restore cookies warning for mature scraps ([#3129](https://github.com/mikf/gallery-dl/issues/3129))
- [instagram] use REST API for unauthenticated users by default
- [downloader:http] increase default `chunk-size` to 32768 bytes ([#3143](https://github.com/mikf/gallery-dl/issues/3143))
- build Windows executables using py2exe's new `freeze()` API
- build executables on GitHub Actions with Python 3.11
- reword error text for unsupported URLs
### Fixes
- [exhentai] fix pagination ([#3181](https://github.com/mikf/gallery-dl/issues/3181))
- [khinsider] fix extraction ([#3215](https://github.com/mikf/gallery-dl/issues/3215), [#3219](https://github.com/mikf/gallery-dl/issues/3219))
- [realbooru] fix download URLs ([#2530](https://github.com/mikf/gallery-dl/issues/2530))
- [realbooru] fix `tags` extraction ([#2530](https://github.com/mikf/gallery-dl/issues/2530))
- [tumblr] fall back to `gifv` when possible ([#3095](https://github.com/mikf/gallery-dl/issues/3095), [#3159](https://github.com/mikf/gallery-dl/issues/3159))
- [twitter] fix login ([#3220](https://github.com/mikf/gallery-dl/issues/3220))
- [twitter] update URL for syndication API ([#3160](https://github.com/mikf/gallery-dl/issues/3160))
- [weibo] send `Referer` headers ([#3188](https://github.com/mikf/gallery-dl/issues/3188))
- [ytdl] update `parse_bytes` location ([#3256](https://github.com/mikf/gallery-dl/issues/3256))
### Improvements
- [imxto] extract additional metadata ([#3118](https://github.com/mikf/gallery-dl/issues/3118), [#3175](https://github.com/mikf/gallery-dl/issues/3175))
- [instagram] allow downloading avatars for private profiles ([#3255](https://github.com/mikf/gallery-dl/issues/3255))
- [pixiv] raise error for invalid search/ranking parameters ([#3214](https://github.com/mikf/gallery-dl/issues/3214))
- [twitter] update `bookmarks` pagination ([#3172](https://github.com/mikf/gallery-dl/issues/3172))
- [downloader:http] refactor file signature checks
- [downloader:http] improve `-r/--limit-rate` accuracy ([#3143](https://github.com/mikf/gallery-dl/issues/3143))
- add loaded config files to debug output
- improve `-K` output for lists
### Removals
- [instagram] remove login support ([#3139](https://github.com/mikf/gallery-dl/issues/3139), [#3141](https://github.com/mikf/gallery-dl/issues/3141), [#3191](https://github.com/mikf/gallery-dl/issues/3191))
- [instagram] remove `channel` extractor
- [ngomik] remove module

## 1.23.5 - 2022-10-30
### Fixes
- [instagram] fix AttributeError on user stories extraction ([#3123](https://github.com/mikf/gallery-dl/issues/3123))

## 1.23.4 - 2022-10-29
### Additions
- [aibooru] add support for aibooru.online ([#3075](https://github.com/mikf/gallery-dl/issues/3075))
- [instagram] add 'avatar' extractor ([#929](https://github.com/mikf/gallery-dl/issues/929), [#1097](https://github.com/mikf/gallery-dl/issues/1097), [#2992](https://github.com/mikf/gallery-dl/issues/2992))
- [instagram] support 'instagram.com/s/' highlight URLs ([#3076](https://github.com/mikf/gallery-dl/issues/3076))
- [instagram] extract 'coauthors' metadata ([#3107](https://github.com/mikf/gallery-dl/issues/3107))
- [mangasee] add support for 'mangalife' ([#3086](https://github.com/mikf/gallery-dl/issues/3086))
- [mastodon] add 'bookmark' extractor ([#3109](https://github.com/mikf/gallery-dl/issues/3109))
- [mastodon] support cross-instance user references and '/web/' URLs ([#3109](https://github.com/mikf/gallery-dl/issues/3109))
- [moebooru] implement 'notes' extraction ([#3094](https://github.com/mikf/gallery-dl/issues/3094))
- [pixiv] extend 'metadata' option ([#3057](https://github.com/mikf/gallery-dl/issues/3057))
- [reactor] match 'best', 'new', 'all' URLs ([#3073](https://github.com/mikf/gallery-dl/issues/3073))
- [smugloli] add 'smugloli' extractors ([#3060](https://github.com/mikf/gallery-dl/issues/3060))
- [tumblr] add 'fallback-delay' and 'fallback-retries' options ([#2957](https://github.com/mikf/gallery-dl/issues/2957))
- [vichan] add generic extractors for vichan imageboards
### Fixes
- [bcy] fix extraction ([#3103](https://github.com/mikf/gallery-dl/issues/3103))
- [gelbooru] support alternate parameter order in post URLs ([#2821](https://github.com/mikf/gallery-dl/issues/2821))
- [hentai2read] support minor versions in chapter URLs ([#3089](https://github.com/mikf/gallery-dl/issues/3089))
- [hentaihere] support minor versions in chapter URLs
- [kemonoparty] fix 'dms' extraction ([#3106](https://github.com/mikf/gallery-dl/issues/3106))
- [kemonoparty] update pagination offset
- [manganelo] update domain to 'chapmanganato.com' ([#3097](https://github.com/mikf/gallery-dl/issues/3097))
- [pixiv] use 'exact_match_for_tags' as default search mode ([#3092](https://github.com/mikf/gallery-dl/issues/3092))
- [redgifs] fix 'token' extraction ([#3080](https://github.com/mikf/gallery-dl/issues/3080), [#3081](https://github.com/mikf/gallery-dl/issues/3081))
- [skeb] fix extraction ([#3112](https://github.com/mikf/gallery-dl/issues/3112))
- improve compatibility of DownloadArchive ([#3078](https://github.com/mikf/gallery-dl/issues/3078))

## 1.23.3 - 2022-10-15
### Additions
- [2chen] Add `2chen.moe` extractor ([#2707](https://github.com/mikf/gallery-dl/issues/2707))
- [8chan] add `thread` and `board` extractors ([#2938](https://github.com/mikf/gallery-dl/issues/2938))
- [deviantart] add `group` option ([#3018](https://github.com/mikf/gallery-dl/issues/3018))
- [fanbox] add `content` metadata field ([#3020](https://github.com/mikf/gallery-dl/issues/3020))
- [instagram] restore `cursor` functionality ([#2991](https://github.com/mikf/gallery-dl/issues/2991))
- [instagram] restore warnings for private profiles ([#3004](https://github.com/mikf/gallery-dl/issues/3004), [#3045](https://github.com/mikf/gallery-dl/issues/3045))
- [nana] add `nana` extractors ([#2967](https://github.com/mikf/gallery-dl/issues/2967))
- [nijie] add `feed` and `followed` extractors ([#3048](https://github.com/mikf/gallery-dl/issues/3048))
- [tumblr] support `https://www.tumblr.com/BLOGNAME` URLs ([#3034](https://github.com/mikf/gallery-dl/issues/3034))
- [tumblr] add `offset` option
- [vk] add `tagged` extractor ([#2997](https://github.com/mikf/gallery-dl/issues/2997))
- add `path-extended` option ([#3021](https://github.com/mikf/gallery-dl/issues/3021))
- emit debug logging messages before calling time.sleep() ([#2982](https://github.com/mikf/gallery-dl/issues/2982))
### Changes
- [postprocessor:metadata] assume `"mode": "custom"` when `format` is given
### Fixes
- [artstation] skip missing projects ([#3016](https://github.com/mikf/gallery-dl/issues/3016))
- [danbooru] fix ugoira metadata extraction ([#3056](https://github.com/mikf/gallery-dl/issues/3056))
- [deviantart] fix `deviation` extraction ([#2981](https://github.com/mikf/gallery-dl/issues/2981))
- [hitomi] fall back to `webp` when selected format is not available ([#3030](https://github.com/mikf/gallery-dl/issues/3030))
- [imagefap] fix and improve folder extraction and gallery pagination ([#3013](https://github.com/mikf/gallery-dl/issues/3013))
- [instagram] fix login ([#3011](https://github.com/mikf/gallery-dl/issues/3011), [#3015](https://github.com/mikf/gallery-dl/issues/3015))
- [nozomi] fix extraction ([#3051](https://github.com/mikf/gallery-dl/issues/3051))
- [redgifs] fix extraction ([#3037](https://github.com/mikf/gallery-dl/issues/3037))
- [tumblr] sleep between fallback retries ([#2957](https://github.com/mikf/gallery-dl/issues/2957))
- [vk] unescape error messages
- fix duplicated metadata bug with `-j` ([#3033](https://github.com/mikf/gallery-dl/issues/3033))
- fix bug when processing input file comments ([#2808](https://github.com/mikf/gallery-dl/issues/2808))

## 1.23.2 - 2022-10-01
### Additions
- [artstation] support search filters ([#2970](https://github.com/mikf/gallery-dl/issues/2970))
- [blogger] add `label` and `query` metadata fields ([#2930](https://github.com/mikf/gallery-dl/issues/2930))
- [exhentai] add a slash to the end of gallery URLs ([#2947](https://github.com/mikf/gallery-dl/issues/2947))
- [instagram] add `count` metadata field ([#2979](https://github.com/mikf/gallery-dl/issues/2979))
- [instagram] add `api` option
- [kemonoparty] add `count` metadata field ([#2952](https://github.com/mikf/gallery-dl/issues/2952))
- [mastodon] warn about moved accounts ([#2939](https://github.com/mikf/gallery-dl/issues/2939))
- [newgrounds] add `games` extractor ([#2955](https://github.com/mikf/gallery-dl/issues/2955))
- [newgrounds] extract `type` metadata
- [pixiv] add `series` extractor ([#2964](https://github.com/mikf/gallery-dl/issues/2964))
- [sankaku] implement `refresh` option ([#2958](https://github.com/mikf/gallery-dl/issues/2958))
- [skeb] add `search` extractor and `filters` option ([#2945](https://github.com/mikf/gallery-dl/issues/2945))
### Fixes
- [deviantart] fix extraction ([#2981](https://github.com/mikf/gallery-dl/issues/2981), [#2983](https://github.com/mikf/gallery-dl/issues/2983))
- [fappic] fix extraction
- [instagram] extract higher-resolution photos ([#2666](https://github.com/mikf/gallery-dl/issues/2666))
- [instagram] fix `username` and `fullname` metadata for saved posts ([#2911](https://github.com/mikf/gallery-dl/issues/2911))
- [instagram] update API headers
- [kemonoparty] send `Referer` headers ([#2989](https://github.com/mikf/gallery-dl/issues/2989), [#2990](https://github.com/mikf/gallery-dl/issues/2990))
- [kemonoparty] restore `favorites` API endpoints ([#2994](https://github.com/mikf/gallery-dl/issues/2994))
- [myportfolio] use fallback when no images are found ([#2959](https://github.com/mikf/gallery-dl/issues/2959))
- [plurk] fix extraction ([#2977](https://github.com/mikf/gallery-dl/issues/2977))
- [sankaku] detect expired links ([#2958](https://github.com/mikf/gallery-dl/issues/2958))
- [tumblr] retry extraction of failed higher-resolution images ([#2957](https://github.com/mikf/gallery-dl/issues/2957))

## 1.23.1 - 2022-09-18
### Additions
- [flickr] add support for `secure.flickr.com` URLs ([#2910](https://github.com/mikf/gallery-dl/issues/2910))
- [hotleak] add hotleak extractors ([#2890](https://github.com/mikf/gallery-dl/issues/2890), [#2909](https://github.com/mikf/gallery-dl/issues/2909))
- [instagram] add `highlight_title` and `date` metadata for highlight downloads ([#2879](https://github.com/mikf/gallery-dl/issues/2879))
- [paheal] add support for videos ([#2892](https://github.com/mikf/gallery-dl/issues/2892))
- [tumblr] fetch high-quality inline images ([#2877](https://github.com/mikf/gallery-dl/issues/2877))
- [tumblr] implement `ratelimit` option ([#2919](https://github.com/mikf/gallery-dl/issues/2919))
- [twitter] add general support for unified cards ([#2875](https://github.com/mikf/gallery-dl/issues/2875))
- [twitter] implement `cards-blacklist` option ([#2875](https://github.com/mikf/gallery-dl/issues/2875))
- [zerochan] add `metadata` option ([#2861](https://github.com/mikf/gallery-dl/issues/2861))
- [postprocessor:zip] implement `files` option ([#2872](https://github.com/mikf/gallery-dl/issues/2872))
### Fixes
- [bunkr] fix extraction ([#2903](https://github.com/mikf/gallery-dl/issues/2903))
- [bunkr] use `media-files` servers for `m4v` and `mov` downloads ([#2925](https://github.com/mikf/gallery-dl/issues/2925))
- [exhentai] improve 509.gif detection ([#2901](https://github.com/mikf/gallery-dl/issues/2901))
- [exhentai] guess extension for original files ([#2842](https://github.com/mikf/gallery-dl/issues/2842))
- [poipiku] use `img-org.poipiku.com` as image domain ([#2796](https://github.com/mikf/gallery-dl/issues/2796))
- [reddit] prevent exception with empty submission URLs ([#2913](https://github.com/mikf/gallery-dl/issues/2913))
- [redgifs] fix download URLs ([#2884](https://github.com/mikf/gallery-dl/issues/2884))
- [smugmug] update default API credentials ([#2881](https://github.com/mikf/gallery-dl/issues/2881))
- [twitter] provide proper `date` for syndication results ([#2920](https://github.com/mikf/gallery-dl/issues/2920))
- [twitter] fix new-style `/card_img/` URLs
- remove all whitespace before comments after input file URLs ([#2808](https://github.com/mikf/gallery-dl/issues/2808))

## 1.23.0 - 2022-08-28
### Changes
- [twitter] update `user` and `author` metdata fields
  - for URLs with a single username or ID like `https://twitter.com/USER` or a search with a single `from:` statement, `user` will now always refer to the user referenced in the URL.
  - for all other URLs like `https://twitter.com/i/bookmarks`, `user` and `author` refer to the same user
  - `author` will always refer to the original Tweet author
- [twitter] update `quote_id` and `quote_by` metadata fields
  - `quote_id` is now non-zero for quoted Tweets and contains the Tweet ID of the quotng Tweet (was the other way round before)
  - `quote_by` is only defined for quoted Tweets like before, but now contains the screen name of the user quoting this Tweet
- [skeb] improve archive IDs for thumbnails and article images
### Additions
- [artstation] add `num` and `count` metadata fields ([#2764](https://github.com/mikf/gallery-dl/issues/2764))
- [catbox] add `album` extractor ([#2410](https://github.com/mikf/gallery-dl/issues/2410))
- [blogger] emit metadata for posts without files ([#2789](https://github.com/mikf/gallery-dl/issues/2789))
- [foolfuuka] update supported domains
- [gelbooru] add support for `api_key` and `user_id` ([#2767](https://github.com/mikf/gallery-dl/issues/2767))
- [gelbooru] implement pagination for `pool` results ([#2853](https://github.com/mikf/gallery-dl/issues/2853))
- [instagram] add support for a user's saved collections ([#2769](https://github.com/mikf/gallery-dl/issues/2769))
- [instagram] provide `date` for directory format strings ([#2830](https://github.com/mikf/gallery-dl/issues/2830))
- [kemonoparty] add `favorites` option ([#2826](https://github.com/mikf/gallery-dl/issues/2826), [#2831](https://github.com/mikf/gallery-dl/issues/2831))
- [oauth] add `host` config option ([#2806](https://github.com/mikf/gallery-dl/issues/2806))
- [rule34] implement pagination for `pool` results ([#2853](https://github.com/mikf/gallery-dl/issues/2853))
- [skeb] add option to download `article` images ([#1031](https://github.com/mikf/gallery-dl/issues/1031))
- [tumblr] download higher-quality images ([#2761](https://github.com/mikf/gallery-dl/issues/2761))
- [tumblr] add `count` metadata field ([#2804](https://github.com/mikf/gallery-dl/issues/2804))
- [wallhaven] implement `metadata` option ([#2803](https://github.com/mikf/gallery-dl/issues/2803))
- [zerochan] add `tag` and `image` extractors ([#1434](https://github.com/mikf/gallery-dl/issues/1434))
- [zerochan] implement login with username & password ([#1434](https://github.com/mikf/gallery-dl/issues/1434))
- [postprocessor:metadata] implement `mode: modify` and `mode: delete` ([#2640](https://github.com/mikf/gallery-dl/issues/2640))
- [formatter] add `g` conversion for slugifying a string ([#2410](https://github.com/mikf/gallery-dl/issues/2410))
- [formatter] apply `:J` only to lists ([#2833](https://github.com/mikf/gallery-dl/issues/2833))
- implement `path-metadata` option ([#2734](https://github.com/mikf/gallery-dl/issues/2734))
- allow comments after input file URLs ([#2808](https://github.com/mikf/gallery-dl/issues/2808))
- add global `warnings` option to control `urllib3` warning behavior ([#2762](https://github.com/mikf/gallery-dl/issues/2762))
### Fixes
- [bunkr] fix extraction ([#2788](https://github.com/mikf/gallery-dl/issues/2788))
- [deviantart] use public access token for journals ([#2702](https://github.com/mikf/gallery-dl/issues/2702))
- [e621] fix extraction of `popular` posts
- [fanbox] download cover images in original size ([#2784](https://github.com/mikf/gallery-dl/issues/2784))
- [mastodon] allow downloading without access token ([#2782](https://github.com/mikf/gallery-dl/issues/2782))
- [hitomi] update cache expiry time ([#2863](https://github.com/mikf/gallery-dl/issues/2863))
- [hitomi] fix error when number of tag results is a multiple of 25 ([#2870](https://github.com/mikf/gallery-dl/issues/2870))
- [mangahere] fix `page-reverse` option ([#2795](https://github.com/mikf/gallery-dl/issues/2795))
- [poipiku] fix posts with more than one image ([#2796](https://github.com/mikf/gallery-dl/issues/2796))
- [poipiku] update filter for static images ([#2796](https://github.com/mikf/gallery-dl/issues/2796))
- [slideshare] fix metadata extraction
- [twitter] unescape `+` in search queries ([#2226](https://github.com/mikf/gallery-dl/issues/2226))
- [twitter] fall back to unfiltered search ([#2766](https://github.com/mikf/gallery-dl/issues/2766))
- [twitter] ignore invalid user entries ([#2850](https://github.com/mikf/gallery-dl/issues/2850))
- [vk] prevent exceptions for broken/invalid photos ([#2774](https://github.com/mikf/gallery-dl/issues/2774))
- [vsco] fix `collection` extraction
- [weibo] prevent exception for missing `playback_list` ([#2792](https://github.com/mikf/gallery-dl/issues/2792))
- [weibo] prevent errors when paginating over album entries ([#2817](https://github.com/mikf/gallery-dl/issues/2817))

## 1.22.4 - 2022-07-15
### Additions
- [instagram] add `pinned` metadata field ([#2752](https://github.com/mikf/gallery-dl/issues/2752))
- [itaku] categorize sections by group ([#1842](https://github.com/mikf/gallery-dl/issues/1842))
- [khinsider] extract `platform` metadata
- [tumblr] support `/blog/view` URLs ([#2760](https://github.com/mikf/gallery-dl/issues/2760))
- [twitter] implement `strategy` option ([#2712](https://github.com/mikf/gallery-dl/issues/2712))
- [twitter] add `count` metadata field ([#2741](https://github.com/mikf/gallery-dl/issues/2741))
- [formatter] implement `O` format specifier ([#2736](https://github.com/mikf/gallery-dl/issues/2736))
- [postprocessor:mtime] add `value` option ([#2739](https://github.com/mikf/gallery-dl/issues/2739))
- add `--no-postprocessors` command-line option ([#2725](https://github.com/mikf/gallery-dl/issues/2725))
- implement `format-separator` option ([#2737](https://github.com/mikf/gallery-dl/issues/2737))
### Changes
- [pinterest] handle section pins with separate extractors ([#2684](https://github.com/mikf/gallery-dl/issues/2684))
- [postprocessor:ugoira] enable `mtime` by default ([#2714](https://github.com/mikf/gallery-dl/issues/2714))
### Fixes
- [bunkr] fix extraction ([#2732](https://github.com/mikf/gallery-dl/issues/2732))
- [hentaifoundry] fix metadata extraction
- [itaku] fix user caching ([#1842](https://github.com/mikf/gallery-dl/issues/1842))
- [itaku] fix `date` parsing
- [kemonoparty] ensure all files have an `extension` ([#2740](https://github.com/mikf/gallery-dl/issues/2740))
- [komikcast] update domain
- [mangakakalot] update domain
- [newgrounds] only attempt to login if necessary ([#2715](https://github.com/mikf/gallery-dl/issues/2715))
- [newgrounds] prevent exception on empty results ([#2727](https://github.com/mikf/gallery-dl/issues/2727))
- [nozomi] reduce memory consumption during searches ([#2754](https://github.com/mikf/gallery-dl/issues/2754))
- [pixiv] fix default `background` filenames
- [sankaku] rewrite file URLs to s.sankakucomplex.com ([#2746](https://github.com/mikf/gallery-dl/issues/2746))
- [slideshare] fix `description` extraction
- [twitter] ignore previously seen Tweets ([#2712](https://github.com/mikf/gallery-dl/issues/2712))
- [twitter] unescape HTML entities in `content` ([#2757](https://github.com/mikf/gallery-dl/issues/2757))
- [weibo] handle invalid or broken status objects
- [postprocessor:zip] ensure target directory exists ([#2758](https://github.com/mikf/gallery-dl/issues/2758))
- make `brotli` an *optional* dependency ([#2716](https://github.com/mikf/gallery-dl/issues/2716))
- limit path length for `--write-pages` output on Windows ([#2733](https://github.com/mikf/gallery-dl/issues/2733))
### Removals
- [foolfuuka] remove archive.wakarimasen.moe

## 1.22.3 - 2022-06-28
### Changes
- [twitter] revert strategy changes for user URLs ([#2712](https://github.com/mikf/gallery-dl/issues/2712), [#2710](https://github.com/mikf/gallery-dl/issues/2710))
- update default User-Agent headers

## 1.22.2 - 2022-06-27
### Additions
- [cyberdrop] add fallback URLs ([#2668](https://github.com/mikf/gallery-dl/issues/2668))
- [horne] add support for horne.red ([#2700](https://github.com/mikf/gallery-dl/issues/2700))
- [itaku] add `gallery` and `image` extractors ([#1842](https://github.com/mikf/gallery-dl/issues/1842))
- [poipiku] add `user` and `post` extractors ([#1602](https://github.com/mikf/gallery-dl/issues/1602))
- [skeb] add `following` extractor ([#2698](https://github.com/mikf/gallery-dl/issues/2698))
- [twitter] implement `expand` option ([#2665](https://github.com/mikf/gallery-dl/issues/2665))
- [twitter] implement `csrf` option ([#2676](https://github.com/mikf/gallery-dl/issues/2676))
- [unsplash] add `collection_title` and `collection_id` metadata fields ([#2670](https://github.com/mikf/gallery-dl/issues/2670))
- [weibo] support `tabtype=video` listings ([#2601](https://github.com/mikf/gallery-dl/issues/2601))
- [formatter] implement slice operator as format specifier
- support cygwin/BSD/etc for `--cookies-from-browser`
### Fixes
- [instagram] improve metadata generated by `_parse_post_api()` ([#2695](https://github.com/mikf/gallery-dl/issues/2695), [#2660](https://github.com/mikf/gallery-dl/issues/2660))
- [instagram} fix `tag` extractor ([#2659](https://github.com/mikf/gallery-dl/issues/2659))
- [instagram] automatically invalidate expired login sessions
- [twitter] fix pagination for conversion tweets
- [twitter] improve `"replies": "self"` ([#2665](https://github.com/mikf/gallery-dl/issues/2665))
- [twitter] improve strategy for user URLs ([#2665](https://github.com/mikf/gallery-dl/issues/2665))
- [vk] take URLs from `*_src` entries ([#2535](https://github.com/mikf/gallery-dl/issues/2535))
- [weibo] fix URLs generated by `user` extractor ([#2601](https://github.com/mikf/gallery-dl/issues/2601))
- [weibo] fix retweets ([#2601](https://github.com/mikf/gallery-dl/issues/2601))
- [downloader:ytdl] update `_set_outtmpl()` ([#2692](https://github.com/mikf/gallery-dl/issues/2692))
- [formatter] fix `!j` conversion for non-serializable types ([#2624](https://github.com/mikf/gallery-dl/issues/2624))
- [snap] Fix missing libslang dependency ([#2655](https://github.com/mikf/gallery-dl/issues/2655))

## 1.22.1 - 2022-06-04
### Additions
- [gfycat] add support for collections ([#2629](https://github.com/mikf/gallery-dl/issues/2629))
- [instagram] support specifying users by ID
- [paheal] extract more metadata ([#2641](https://github.com/mikf/gallery-dl/issues/2641))
- [reddit] add `home` extractor ([#2614](https://github.com/mikf/gallery-dl/issues/2614))
- [weibo] support usernames in URLs ([#1662](https://github.com/mikf/gallery-dl/issues/1662))
- [weibo] support `livephoto` and `gif` files ([#2146](https://github.com/mikf/gallery-dl/issues/2146))
- [weibo] add support for several different `tabtype` listings ([#686](https://github.com/mikf/gallery-dl/issues/686), [#2601](https://github.com/mikf/gallery-dl/issues/2601))
- [postprocessor:metadata] write to stdout by setting filename to "-" ([#2624](https://github.com/mikf/gallery-dl/issues/2624))
- implement `output.ansi` option ([#2628](https://github.com/mikf/gallery-dl/issues/2628))
- support user-defined `output.mode` settings ([#2529](https://github.com/mikf/gallery-dl/issues/2529))
### Changes
- [readcomiconline] remove default `browser` setting ([#2625](https://github.com/mikf/gallery-dl/issues/2625))
- [weibo] switch to desktop API ([#2601](https://github.com/mikf/gallery-dl/issues/2601))
- fix command-line argument name of `--cookies-from-browser` ([#1606](https://github.com/mikf/gallery-dl/issues/1606), [#2630](https://github.com/mikf/gallery-dl/issues/2630))
### Fixes
- [bunkr] change domain to `app.bunkr.is` ([#2634](https://github.com/mikf/gallery-dl/issues/2634))
- [deviantart] fix folder listings with `"pagination": "manual"` ([#2488](https://github.com/mikf/gallery-dl/issues/2488))
- [gofile] fix 401 Unauthorized errors ([#2632](https://github.com/mikf/gallery-dl/issues/2632))
- [hypnohub] move to gelbooru_v02 instances ([#2631](https://github.com/mikf/gallery-dl/issues/2631))
- [instagram] fix and update extractors ([#2644](https://github.com/mikf/gallery-dl/issues/2644))
- [nozomi] remove slashes from search terms ([#2653](https://github.com/mikf/gallery-dl/issues/2653))
- [pixiv] include `.gif` in background fallback URLs ([#2495](https://github.com/mikf/gallery-dl/issues/2495))
- [sankaku] extend URL patterns ([#2647](https://github.com/mikf/gallery-dl/issues/2647))
- [subscribestar] fix `date` metadata ([#2642](https://github.com/mikf/gallery-dl/issues/2642))

## 1.22.0 - 2022-05-25
### Additions
- [gelbooru_v01] add `favorite` extractor ([#2546](https://github.com/mikf/gallery-dl/issues/2546))
- [Instagram] add `tagged_users` to keywords for stories ([#2582](https://github.com/mikf/gallery-dl/issues/2582), [#2584](https://github.com/mikf/gallery-dl/issues/2584))
- [lolisafe] implement `domain` option ([#2575](https://github.com/mikf/gallery-dl/issues/2575))
- [naverwebtoon] support (best)challenge comics ([#2542](https://github.com/mikf/gallery-dl/issues/2542))
- [nijie] support /history_nuita.php listings ([#2541](https://github.com/mikf/gallery-dl/issues/2541))
- [pixiv] provide more data when `metadata` is enabled ([#2594](https://github.com/mikf/gallery-dl/issues/2594))
- [shopify] support several more sites by default ([#2089](https://github.com/mikf/gallery-dl/issues/2089))
- [twitter] extract alt texts as `description` ([#2617](https://github.com/mikf/gallery-dl/issues/2617))
- [twitter] recognize vxtwitter URLs ([#2621](https://github.com/mikf/gallery-dl/issues/2621))
- [weasyl] implement `metadata` option ([#2610](https://github.com/mikf/gallery-dl/issues/2610))
- implement `--cookies-from-browser` ([#1606](https://github.com/mikf/gallery-dl/issues/1606))
- implement `output.colors` options ([#2532](https://github.com/mikf/gallery-dl/issues/2532))
- implement string literals in replacement fields
- support using extended format strings for archive keys
### Changes
- [foolfuuka] match 4chan filenames ([#2577](https://github.com/mikf/gallery-dl/issues/2577))
- [pixiv] implement `include` option
  - provide `avatar`/`background` downloads as separate extractors ([#2495](https://github.com/mikf/gallery-dl/issues/2495))
- [twitter] use a better strategy for user URLs
- [twitter] disable `cards` by default
- delay directory creation ([#2461](https://github.com/mikf/gallery-dl/issues/2461), [#2474](https://github.com/mikf/gallery-dl/issues/2474))
- flush writes to stdout/stderr ([#2529](https://github.com/mikf/gallery-dl/issues/2529))
- build executables on GitHub Actions with Python 3.10
### Fixes
- [artstation] use `"browser": "firefox"` by default ([#2527](https://github.com/mikf/gallery-dl/issues/2527))
- [imgur] prevent exception with empty albums ([#2557](https://github.com/mikf/gallery-dl/issues/2557))
- [instagram] report redirects to captcha challenges ([#2543](https://github.com/mikf/gallery-dl/issues/2543))
- [khinsider] fix metadata extraction ([#2611](https://github.com/mikf/gallery-dl/issues/2611))
- [mangafox] send Referer headers ([#2592](https://github.com/mikf/gallery-dl/issues/2592))
- [mangahere] send Referer headers ([#2592](https://github.com/mikf/gallery-dl/issues/2592))
- [mangasee] use randomly generated PHPSESSID cookie ([#2560](https://github.com/mikf/gallery-dl/issues/2560))
- [pixiv] make retrieving ugoira metadata non-fatal ([#2562](https://github.com/mikf/gallery-dl/issues/2562))
- [readcomiconline] update deobfuscation code ([#2481](https://github.com/mikf/gallery-dl/issues/2481))
- [realbooru] fix extraction ([#2530](https://github.com/mikf/gallery-dl/issues/2530))
- [vk] handle photos without width/height info ([#2535](https://github.com/mikf/gallery-dl/issues/2535))
- [vk] fix user ID extraction ([#2535](https://github.com/mikf/gallery-dl/issues/2535))
- [webtoons] extract real episode numbers ([#2591](https://github.com/mikf/gallery-dl/issues/2591))
- create missing directories for archive files ([#2597](https://github.com/mikf/gallery-dl/issues/2597))
- detect circular references with `-K` ([#2609](https://github.com/mikf/gallery-dl/issues/2609))
- replace "\f" in `--filename` arguments with a form feed character ([#2396](https://github.com/mikf/gallery-dl/issues/2396))
### Removals
- [gelbooru_v01] remove tlb.booru.org from supported domains

## 1.21.2 - 2022-04-27
### Additions
- [deviantart] implement `pagination` option ([#2488](https://github.com/mikf/gallery-dl/issues/2488))
- [pixiv] implement `background` option ([#623](https://github.com/mikf/gallery-dl/issues/623), [#1124](https://github.com/mikf/gallery-dl/issues/1124), [#2495](https://github.com/mikf/gallery-dl/issues/2495))
- [postprocessor:ugoira] report ffmpeg/mkvmerge errors ([#2487](https://github.com/mikf/gallery-dl/issues/2487))
### Fixes
- [cyberdrop] match cyberdrop.to URLs ([#2496](https://github.com/mikf/gallery-dl/issues/2496))
- [e621] fix 403 errors ([#2533](https://github.com/mikf/gallery-dl/issues/2533))
- [issuu] fix extraction ([#2483](https://github.com/mikf/gallery-dl/issues/2483))
- [mangadex] download from available chapters despite `externalUrl` ([#2503](https://github.com/mikf/gallery-dl/issues/2503))
- [photovogue] update domain and api endpoint ([#2494](https://github.com/mikf/gallery-dl/issues/2494))
- [sexcom] add fallback for empty files ([#2485](https://github.com/mikf/gallery-dl/issues/2485))
- [twitter] improve syndication video selection ([#2354](https://github.com/mikf/gallery-dl/issues/2354))
- [twitter] fix various syndication issues ([#2499](https://github.com/mikf/gallery-dl/issues/2499), [#2354](https://github.com/mikf/gallery-dl/issues/2354))
- [vk] fix extraction ([#2512](https://github.com/mikf/gallery-dl/issues/2512))
- [weibo] fix infinite retries for deleted accounts ([#2521](https://github.com/mikf/gallery-dl/issues/2521))
- [postprocessor:ugoira] use compatible paths with mkvmerge ([#2487](https://github.com/mikf/gallery-dl/issues/2487))
- [postprocessor:ugoira] do not auto-select the `image2` demuxer ([#2492](https://github.com/mikf/gallery-dl/issues/2492))

## 1.21.1 - 2022-04-08
### Additions
- [gofile] add gofile.io extractor ([#2364](https://github.com/mikf/gallery-dl/issues/2364))
- [instagram] add `previews` option ([#2135](https://github.com/mikf/gallery-dl/issues/2135))
- [kemonoparty] add `duplicates` option ([#2440](https://github.com/mikf/gallery-dl/issues/2440))
- [pinterest] add extractor for created pins ([#2452](https://github.com/mikf/gallery-dl/issues/2452))
- [pinterest] support multiple files per pin ([#1619](https://github.com/mikf/gallery-dl/issues/1619), [#2452](https://github.com/mikf/gallery-dl/issues/2452))
- [telegraph] Add telegra.ph extractor ([#2312](https://github.com/mikf/gallery-dl/issues/2312))
- [twitter] add `syndication` option ([#2354](https://github.com/mikf/gallery-dl/issues/2354))
- [twitter] accept fxtwitter.com URLs ([#2484](https://github.com/mikf/gallery-dl/issues/2484))
- [downloader:http] support using an arbitrary method and sending POST data ([#2433](https://github.com/mikf/gallery-dl/issues/2433))
- [postprocessor:metadata] implement archive options ([#2421](https://github.com/mikf/gallery-dl/issues/2421))
- [postprocessor:ugoira] add `mtime` option ([#2307](https://github.com/mikf/gallery-dl/issues/2307))
- [postprocessor:ugoira] support setting timecodes with `mkvmerge` ([#1550](https://github.com/mikf/gallery-dl/issues/1550))
- [formatter] support evaluating f-string literals
- add `--ugoira-conv-copy` command-line option ([#1550](https://github.com/mikf/gallery-dl/issues/1550))
- implement a `contains()` function for filter statements ([#2446](https://github.com/mikf/gallery-dl/issues/2446))
### Fixes
- [aryion] provide correct `date` metadata independent of DST
- [furaffinity] fix search result pagination ([#2402](https://github.com/mikf/gallery-dl/issues/2402))
- [hitomi] update and fix metadata extraction ([#2444](https://github.com/mikf/gallery-dl/issues/2444))
- [kissgoddess] extract all images ([#2473](https://github.com/mikf/gallery-dl/issues/2473))
- [mangasee] unescape manga names ([#2454](https://github.com/mikf/gallery-dl/issues/2454))
- [newgrounds] update and fix pagination ([#2456](https://github.com/mikf/gallery-dl/issues/2456))
- [newgrounds] warn about age-restricted posts ([#2456](https://github.com/mikf/gallery-dl/issues/2456))
- [pinterest] do not force `m3u8_native` for video downloads ([#2436](https://github.com/mikf/gallery-dl/issues/2436))
- [twibooru] fix posts without `name` ([#2434](https://github.com/mikf/gallery-dl/issues/2434))
- [unsplash] replace dash with space in search API queries ([#2429](https://github.com/mikf/gallery-dl/issues/2429))
- [postprocessor:mtime] fix timestamps from datetime objects ([#2307](https://github.com/mikf/gallery-dl/issues/2307))
- fix yet another bug in `_check_cookies()` ([#2372](https://github.com/mikf/gallery-dl/issues/2372))
- fix loading/storing cookies without domain

## 1.21.0 - 2022-03-14
### Additions
- [fantia] add `num` enumeration index ([#2377](https://github.com/mikf/gallery-dl/issues/2377))
- [fantia] support "Blog Post" content ([#2381](https://github.com/mikf/gallery-dl/issues/2381))
- [imagebam] add support for /view/ paths ([#2378](https://github.com/mikf/gallery-dl/issues/2378))
- [kemonoparty] match beta.kemono.party URLs ([#2348](https://github.com/mikf/gallery-dl/issues/2348))
- [kissgoddess] add `gallery` and `model` extractors ([#1052](https://github.com/mikf/gallery-dl/issues/1052), [#2304](https://github.com/mikf/gallery-dl/issues/2304))
- [mememuseum] add `tag` and `post` extractors ([#2264](https://github.com/mikf/gallery-dl/issues/2264))
- [newgrounds] add `post_url` metadata field ([#2328](https://github.com/mikf/gallery-dl/issues/2328))
- [patreon] add `image_large` file type ([#2257](https://github.com/mikf/gallery-dl/issues/2257))
- [toyhouse] support `art` listings ([#1546](https://github.com/mikf/gallery-dl/issues/1546), [#2331](https://github.com/mikf/gallery-dl/issues/2331))
- [twibooru] add extractors for searches, galleries, and posts ([#2219](https://github.com/mikf/gallery-dl/issues/2219))
- [postprocessor:metadata] implement `mtime` option ([#2307](https://github.com/mikf/gallery-dl/issues/2307))
- [postprocessor:mtime] add `event` option ([#2307](https://github.com/mikf/gallery-dl/issues/2307))
- add fish shell completion ([#2363](https://github.com/mikf/gallery-dl/issues/2363))
- add `timedelta` class to global namespace in filter expressions
### Changes
- [seiga] require authentication with `user_session` cookie ([#2372](https://github.com/mikf/gallery-dl/issues/2372))
  - remove username & password login due to 2FA
- refactor proxy support ([#2357](https://github.com/mikf/gallery-dl/issues/2357))
  - allow gallery-dl proxy settings to overwrite environment proxies
  - allow specifying different proxies for data extraction and download
### Fixes
- [bunkr] fix mp4 downloads ([#2239](https://github.com/mikf/gallery-dl/issues/2239))
- [fanbox] fetch data for each individual post ([#2388](https://github.com/mikf/gallery-dl/issues/2388))
- [hentaicosplays] send `Referer` header ([#2317](https://github.com/mikf/gallery-dl/issues/2317))
- [imagebam] set `nsfw_inter` cookie ([#2334](https://github.com/mikf/gallery-dl/issues/2334))
- [kemonoparty] limit default filename length ([#2373](https://github.com/mikf/gallery-dl/issues/2373))
- [mangadex] fix chapters without `translatedLanguage` ([#2352](https://github.com/mikf/gallery-dl/issues/2352))
- [newgrounds] fix video descriptions ([#2328](https://github.com/mikf/gallery-dl/issues/2328))
- [skeb] add `sent-requests` option ([#2322](https://github.com/mikf/gallery-dl/issues/2322), [#2330](https://github.com/mikf/gallery-dl/issues/2330))
- [slideshare] fix extraction
- [subscribestar] unescape attachment URLs ([#2370](https://github.com/mikf/gallery-dl/issues/2370))
- [twitter] fix handling of 429 Too Many Requests responses ([#2339](https://github.com/mikf/gallery-dl/issues/2339))
- [twitter] warn about age-restricted Tweets ([#2354](https://github.com/mikf/gallery-dl/issues/2354))
- [twitter] handle Tweets with "softIntervention" entries
- [twitter] update query hashes
- fix another bug in `_check_cookies()` ([#2160](https://github.com/mikf/gallery-dl/issues/2160))

## 1.20.5 - 2022-02-14
### Additions
- [furaffinity] add `layout` option ([#2277](https://github.com/mikf/gallery-dl/issues/2277))
- [lightroom] add Lightroom gallery extractor ([#2263](https://github.com/mikf/gallery-dl/issues/2263))
- [reddit] support standalone submissions on personal user pages ([#2301](https://github.com/mikf/gallery-dl/issues/2301))
- [redgifs] support i.redgifs.com URLs ([#2300](https://github.com/mikf/gallery-dl/issues/2300))
- [wallpapercave] add extractor for images and search results ([#2205](https://github.com/mikf/gallery-dl/issues/2205))
- add `signals-ignore` option ([#2296](https://github.com/mikf/gallery-dl/issues/2296))
### Changes
- [danbooru] merge `danbooru` and `e621` extractors
  - support `atfbooru` ([#2283](https://github.com/mikf/gallery-dl/issues/2283))
  - remove support for old e621 tag search URLs
### Fixes
- [furaffinity] improve new/old layout detection ([#2277](https://github.com/mikf/gallery-dl/issues/2277))
- [imgbox] fix ImgboxExtractor ([#2281](https://github.com/mikf/gallery-dl/issues/2281))
- [inkbunny] rename search parameters to their API equivalents
- [kemonoparty] handle files without names ([#2276](https://github.com/mikf/gallery-dl/issues/2276))
- [twitter] fix extraction ([#2275](https://github.com/mikf/gallery-dl/issues/2275), [#2295](https://github.com/mikf/gallery-dl/issues/2295))
- [vk] fix infinite pagination loops ([#2297](https://github.com/mikf/gallery-dl/issues/2297))
- [downloader:ytdl] make `ImportError`s non-fatal ([#2273](https://github.com/mikf/gallery-dl/issues/2273))

## 1.20.4 - 2022-02-06
### Additions
- [e621] add `favorite` extractor ([#2250](https://github.com/mikf/gallery-dl/issues/2250))
- [hitomi] add `format` option ([#2260](https://github.com/mikf/gallery-dl/issues/2260))
- [kohlchan] add Kohlchan extractors ([#2251](https://github.com/mikf/gallery-dl/issues/2251))
- [sexcom] add `pins` extractor ([#2265](https://github.com/mikf/gallery-dl/issues/2265))
- [twitter] add `warnings` option ([#2258](https://github.com/mikf/gallery-dl/issues/2258))
- add ability to disable TLS 1.2 ([#2243](https://github.com/mikf/gallery-dl/issues/2243))
- add examples for custom gelbooru instances ([#2262](https://github.com/mikf/gallery-dl/issues/2262))
### Fixes
- [bunkr] fix mp4 downloads ([#2239](https://github.com/mikf/gallery-dl/issues/2239))
- [gelbooru] improve and fix pagination ([#2230](https://github.com/mikf/gallery-dl/issues/2230), [#2232](https://github.com/mikf/gallery-dl/issues/2232))
- [hitomi] "fix" 403 errors ([#2260](https://github.com/mikf/gallery-dl/issues/2260))
- [kemonoparty] fix downloading smaller text files ([#2267](https://github.com/mikf/gallery-dl/issues/2267))
- [patreon] disable TLS 1.2 by default ([#2249](https://github.com/mikf/gallery-dl/issues/2249))
- [twitter] restore errors for protected timelines etc ([#2237](https://github.com/mikf/gallery-dl/issues/2237))
- [twitter] restore `logout` functionality ([#1719](https://github.com/mikf/gallery-dl/issues/1719))
- [twitter] provide fallback URLs for card images
- [weibo] update pagination code ([#2244](https://github.com/mikf/gallery-dl/issues/2244))

## 1.20.3 - 2022-01-26
### Fixes
- [kemonoparty] fix DMs extraction ([#2008](https://github.com/mikf/gallery-dl/issues/2008))
- [twitter] fix crash on Tweets with deleted quotes ([#2225](https://github.com/mikf/gallery-dl/issues/2225))
- [twitter] fix crash on suspended Tweets without `legacy` entry ([#2216](https://github.com/mikf/gallery-dl/issues/2216))
- [twitter] fix crash on unified cards without `type`
- [twitter] prevent crash on invalid/deleted Retweets ([#2225](https://github.com/mikf/gallery-dl/issues/2225))
- [twitter] update query hashes

## 1.20.2 - 2022-01-24
### Additions
- [twitter] add `event` extractor (closes [#2109](https://github.com/mikf/gallery-dl/issues/2109))
- [twitter] support image_carousel_website unified cards
- add `--source-address` command-line option ([#2206](https://github.com/mikf/gallery-dl/issues/2206))
- add environment variable syntax to formatting.md ([#2065](https://github.com/mikf/gallery-dl/issues/2065))
### Changes
- [twitter] changes to `cards` option
  - enable `cards` by default
  - require `cards` to be set to `"ytdl"` to invoke youtube-dl/yt-dlp on unsupported cards
### Fixes
- [blogger] support new image domain ([#2204](https://github.com/mikf/gallery-dl/issues/2204))
- [gelbooru] improve video file detection ([#2188](https://github.com/mikf/gallery-dl/issues/2188))
- [hitomi] fix `tag` extraction ([#2189](https://github.com/mikf/gallery-dl/issues/2189))
- [instagram] fix highlights extraction ([#2197](https://github.com/mikf/gallery-dl/issues/2197))
- [mangadex] re-enable warning for external chapters ([#2193](https://github.com/mikf/gallery-dl/issues/2193))
- [newgrounds] set suitabilities filter before starting a search ([#2173](https://github.com/mikf/gallery-dl/issues/2173))
- [philomena] fix search parameter escaping ([#2215](https://github.com/mikf/gallery-dl/issues/2215))
- [reddit] allow downloading from quarantined subreddits ([#2180](https://github.com/mikf/gallery-dl/issues/2180))
- [sexcom] extend URL pattern ([#2220](https://github.com/mikf/gallery-dl/issues/2220))
- [twitter] update to GraphQL API ([#2212](https://github.com/mikf/gallery-dl/issues/2212))

## 1.20.1 - 2022-01-08
### Additions
- [newgrounds] add `search` extractor ([#2161](https://github.com/mikf/gallery-dl/issues/2161))
### Changes
- restore `-d/--dest` functionality from before 1.20.0 ([#2148](https://github.com/mikf/gallery-dl/issues/2148))
- change short option for `--directory` to `-D`
### Fixes
- [gelbooru] handle changed API response format ([#2157](https://github.com/mikf/gallery-dl/issues/2157))
- [hitomi] fix image URLs ([#2153](https://github.com/mikf/gallery-dl/issues/2153))
- [mangadex] fix extraction ([#2177](https://github.com/mikf/gallery-dl/issues/2177))
- [rule34] use `https://api.rule34.xxx` for API requests
- fix cookie checks for patreon, fanbox, fantia
- improve UNC path handling ([#2126](https://github.com/mikf/gallery-dl/issues/2126))

## 1.20.0 - 2021-12-29
### Additions
- [500px] add `favorite` extractor ([#1927](https://github.com/mikf/gallery-dl/issues/1927))
- [exhentai] add `source` option
- [fanbox] support pixiv redirects ([#2122](https://github.com/mikf/gallery-dl/issues/2122))
- [inkbunny] add `search` extractor ([#2094](https://github.com/mikf/gallery-dl/issues/2094))
- [kemonoparty] support coomer.party ([#2100](https://github.com/mikf/gallery-dl/issues/2100))
- [lolisafe] add generic album extractor for lolisafe/chibisafe instances ([#2038](https://github.com/mikf/gallery-dl/issues/2038), [#2105](https://github.com/mikf/gallery-dl/issues/2105))
- [rule34us] add `tag` and `post` extractors ([#1527](https://github.com/mikf/gallery-dl/issues/1527))
- add a generic extractor ([#735](https://github.com/mikf/gallery-dl/issues/735), [#683](https://github.com/mikf/gallery-dl/issues/683))
- add `-d/--directory` and `-f/--filename` command-line options
- add `--sleep-request` and `--sleep-extractor` command-line options
- allow specifying `sleep-*` options as string
### Changes
- [cyberdrop] include file ID in default filenames
- [hitomi] disable `metadata` by default
- [kemonoparty] use `service` as subcategory ([#2147](https://github.com/mikf/gallery-dl/issues/2147))
- [kemonoparty] change default `files` order to `attachments,file,inline` ([#1991](https://github.com/mikf/gallery-dl/issues/1991))
- [output] write download progress indicator to stderr
- [ytdl] prefer yt-dlp over youtube-dl ([#1850](https://github.com/mikf/gallery-dl/issues/1850), [#2028](https://github.com/mikf/gallery-dl/issues/2028))
- rename `--write-infojson` to `--write-info-json`
### Fixes
- [500px] create directories per photo
- [artstation] create directories per asset ([#2136](https://github.com/mikf/gallery-dl/issues/2136))
- [deviantart] use `/browse/newest` for most-recent searches ([#2096](https://github.com/mikf/gallery-dl/issues/2096))
- [hitomi] fix image URLs
- [instagram] fix error when PostPage data is not in GraphQL format ([#2037](https://github.com/mikf/gallery-dl/issues/2037))
- [instagran] match post URLs with usernames ([#2085](https://github.com/mikf/gallery-dl/issues/2085))
- [instagram] allow downloading specific stories ([#2088](https://github.com/mikf/gallery-dl/issues/2088))
- [furaffinity] warn when no session cookies were found
- [pixiv] respect date ranges in search URLs ([#2133](https://github.com/mikf/gallery-dl/issues/2133))
- [sexcom] fix and improve embed extraction ([#2145](https://github.com/mikf/gallery-dl/issues/2145))
- [tumblrgallery] fix extraction ([#2112](https://github.com/mikf/gallery-dl/issues/2112))
- [tumblrgallery] improve `id` extraction ([#2115](https://github.com/mikf/gallery-dl/issues/2115))
- [tumblrgallery] improve search pagination ([#2132](https://github.com/mikf/gallery-dl/issues/2132))
- [twitter] include `4096x4096` as a default image fallback ([#1881](https://github.com/mikf/gallery-dl/issues/1881), [#2107](https://github.com/mikf/gallery-dl/issues/2107))
- [ytdl] update argument parsing to latest yt-dlp changes ([#2124](https://github.com/mikf/gallery-dl/issues/2124))
- handle UNC paths ([#2113](https://github.com/mikf/gallery-dl/issues/2113))

## 1.19.3 - 2021-11-27
### Additions
- [dynastyscans] add `manga` extractor ([#2035](https://github.com/mikf/gallery-dl/issues/2035))
- [instagram] include user metadata for `tagged` downloads ([#2024](https://github.com/mikf/gallery-dl/issues/2024))
- [kemonoparty] implement `files` option ([#1991](https://github.com/mikf/gallery-dl/issues/1991))
- [kemonoparty] add `dms` option ([#2008](https://github.com/mikf/gallery-dl/issues/2008))
- [mangadex] always provide `artist`, `author`, and `group` metadata fields ([#2049](https://github.com/mikf/gallery-dl/issues/2049))
- [philomena] support furbooru.org ([#1995](https://github.com/mikf/gallery-dl/issues/1995))
- [reactor] support thatpervert.com ([#2029](https://github.com/mikf/gallery-dl/issues/2029))
- [shopify] support loungeunderwear.com ([#2053](https://github.com/mikf/gallery-dl/issues/2053))
- [skeb] add `thumbnails` option ([#2047](https://github.com/mikf/gallery-dl/issues/2047), [#2051](https://github.com/mikf/gallery-dl/issues/2051))
- [subscribestar] add `num` enumeration index ([#2040](https://github.com/mikf/gallery-dl/issues/2040))
- [subscribestar] emit metadata for posts without media ([#1569](https://github.com/mikf/gallery-dl/issues/1569))
- [ytdl] implement `cmdline-args` and `config-file` options to allow parsing ytdl command-line options ([#1680](https://github.com/mikf/gallery-dl/issues/1680))
- [formatter] implement `D` format specifier
- extend `blacklist`/`whitelist` syntax ([#2025](https://github.com/mikf/gallery-dl/issues/2025))
### Fixes
- [dynastyscans] provide `date` as datetime object ([#2050](https://github.com/mikf/gallery-dl/issues/2050))
- [exhentai] fix extraction for disowned galleries ([#2055](https://github.com/mikf/gallery-dl/issues/2055))
- [gelbooru] apply workaround for pagination limits
- [kemonoparty] skip duplicate files ([#2032](https://github.com/mikf/gallery-dl/issues/2032), [#1991](https://github.com/mikf/gallery-dl/issues/1991), [#1899](https://github.com/mikf/gallery-dl/issues/1899))
- [kemonoparty] provide `date` metadata for gumroad ([#2007](https://github.com/mikf/gallery-dl/issues/2007))
- [mangoxo] fix metadata extraction
- [twitter] distinguish between fatal & nonfatal errors ([#2020](https://github.com/mikf/gallery-dl/issues/2020))
- [twitter] fix extractor for direct image links ([#2030](https://github.com/mikf/gallery-dl/issues/2030))
- [webtoons] use download URLs that do not require a `Referer` header ([#2005](https://github.com/mikf/gallery-dl/issues/2005))
- [ytdl] improve error handling ([#1680](https://github.com/mikf/gallery-dl/issues/1680))
- [downloader:ytdl] prevent crash in `_progress_hook()` ([#1680](https://github.com/mikf/gallery-dl/issues/1680))
### Removals
- [seisoparty] remove module

## 1.19.2 - 2021-11-05
### Additions
- [kemonoparty] add `comments` option ([#1980](https://github.com/mikf/gallery-dl/issues/1980))
- [skeb] add `user` and `post` extractors ([#1031](https://github.com/mikf/gallery-dl/issues/1031), [#1971](https://github.com/mikf/gallery-dl/issues/1971))
- [twitter] add `pinned` option
- support accessing environment variables and the current local datetime in format strings ([#1968](https://github.com/mikf/gallery-dl/issues/1968))
- add special type format strings to docs ([#1987](https://github.com/mikf/gallery-dl/issues/1987))
### Fixes
- [cyberdrop] fix video extraction ([#1993](https://github.com/mikf/gallery-dl/issues/1993))
- [deviantart] fix `index` values for stashed deviations
- [gfycat] provide consistent `userName` values for `user` downloads ([#1962](https://github.com/mikf/gallery-dl/issues/1962))
- [gfycat] show warning when there are no available formats
- [hitomi] fix image URLs ([#1975](https://github.com/mikf/gallery-dl/issues/1975), [#1982](https://github.com/mikf/gallery-dl/issues/1982), [#1988](https://github.com/mikf/gallery-dl/issues/1988))
- [instagram] update query hashes
- [mangakakalot] update domain and fix extraction
- [mangoxo] fix login and extraction
- [reddit] prevent crash for galleries with no `media_metadata` ([#2001](https://github.com/mikf/gallery-dl/issues/2001))
- [redgifs] update to API v2 ([#1984](https://github.com/mikf/gallery-dl/issues/1984))
- fix calculating retry sleep times ([#1990](https://github.com/mikf/gallery-dl/issues/1990))

## 1.19.1 - 2021-10-24
### Additions
- [inkbunny] add `following` extractor ([#515](https://github.com/mikf/gallery-dl/issues/515))
- [inkbunny] add `pool` extractor ([#1937](https://github.com/mikf/gallery-dl/issues/1937))
- [kemonoparty] add `discord` extractor ([#1827](https://github.com/mikf/gallery-dl/issues/1827), [#1940](https://github.com/mikf/gallery-dl/issues/1940))
- [nhentai] add `tag` extractor ([#1950](https://github.com/mikf/gallery-dl/issues/1950), [#1955](https://github.com/mikf/gallery-dl/issues/1955))
- [patreon] add `files` option ([#1935](https://github.com/mikf/gallery-dl/issues/1935))
- [picarto] add `gallery` extractor ([#1931](https://github.com/mikf/gallery-dl/issues/1931))
- [pixiv] add `sketch` extractor ([#1497](https://github.com/mikf/gallery-dl/issues/1497))
- [seisoparty] add `favorite` extractor ([#1906](https://github.com/mikf/gallery-dl/issues/1906))
- [twitter] add `size` option ([#1881](https://github.com/mikf/gallery-dl/issues/1881))
- [vk] add `album` extractor ([#474](https://github.com/mikf/gallery-dl/issues/474), [#1952](https://github.com/mikf/gallery-dl/issues/1952))
- [postprocessor:compare] add `equal` option ([#1592](https://github.com/mikf/gallery-dl/issues/1592))
### Fixes
- [cyberdrop] extract direct download URLs ([#1943](https://github.com/mikf/gallery-dl/issues/1943))
- [deviantart] update `search` argument handling ([#1911](https://github.com/mikf/gallery-dl/issues/1911))
- [deviantart] full resolution for non-downloadable images ([#293](https://github.com/mikf/gallery-dl/issues/293))
- [furaffinity] unquote search queries ([#1958](https://github.com/mikf/gallery-dl/issues/1958))
- [inkbunny] match "long" URLs for pools and favorites ([#1937](https://github.com/mikf/gallery-dl/issues/1937))
- [kemonoparty] improve inline extraction ([#1899](https://github.com/mikf/gallery-dl/issues/1899))
- [mangadex] update parameter handling for API requests ([#1908](https://github.com/mikf/gallery-dl/issues/1908))
- [patreon] better filenames for `content` images ([#1954](https://github.com/mikf/gallery-dl/issues/1954))
- [redgifs][gfycat] provide fallback URLs ([#1962](https://github.com/mikf/gallery-dl/issues/1962))
- [downloader:ytdl] prevent crash in `_progress_hook()`
- restore SOCKS support for Windows executables

## 1.19.0 - 2021-10-01
### Additions
- [aryion] add `tag` extractor ([#1849](https://github.com/mikf/gallery-dl/issues/1849))
- [desktopography] implement desktopography extractors ([#1740](https://github.com/mikf/gallery-dl/issues/1740))
- [deviantart] implement `auto-unwatch` option ([#1466](https://github.com/mikf/gallery-dl/issues/1466), [#1757](https://github.com/mikf/gallery-dl/issues/1757))
- [fantia] add `date` metadata field ([#1853](https://github.com/mikf/gallery-dl/issues/1853))
- [fappic] add `image` extractor ([#1898](https://github.com/mikf/gallery-dl/issues/1898))
- [gelbooru_v02] add `favorite` extractor ([#1834](https://github.com/mikf/gallery-dl/issues/1834))
- [kemonoparty] add `favorite` extractor ([#1824](https://github.com/mikf/gallery-dl/issues/1824))
- [kemonoparty] implement login with username & password ([#1824](https://github.com/mikf/gallery-dl/issues/1824))
- [mastodon] add `following` extractor ([#1891](https://github.com/mikf/gallery-dl/issues/1891))
- [mastodon] support specifying accounts by ID
- [twitter] support `/with_replies` URLs ([#1833](https://github.com/mikf/gallery-dl/issues/1833))
- [twitter] add `quote_by` metadata field ([#1481](https://github.com/mikf/gallery-dl/issues/1481))
- [postprocessor:compare] extend `action` option ([#1592](https://github.com/mikf/gallery-dl/issues/1592))
- implement a download progress indicator ([#1519](https://github.com/mikf/gallery-dl/issues/1519))
- implement a `page-reverse` option ([#1854](https://github.com/mikf/gallery-dl/issues/1854))
- implement a way to specify extended format strings
- allow specifying a minimum/maximum for `sleep-*` options ([#1835](https://github.com/mikf/gallery-dl/issues/1835))
- add a `--write-infojson` command-line option
### Changes
- [cyberdrop] change directory name format ([#1871](https://github.com/mikf/gallery-dl/issues/1871))
- [instagram] update default delay to 6-12 seconds ([#1835](https://github.com/mikf/gallery-dl/issues/1835))
- [reddit] extend subcategory depending on input URL ([#1836](https://github.com/mikf/gallery-dl/issues/1836))
- move util.Formatter and util.PathFormat into their own modules
### Fixes
- [artstation] use `/album/all` view for user portfolios ([#1826](https://github.com/mikf/gallery-dl/issues/1826))
- [aryion] update/improve pagination ([#1849](https://github.com/mikf/gallery-dl/issues/1849))
- [deviantart] fix bug with fetching premium content ([#1879](https://github.com/mikf/gallery-dl/issues/1879))
- [deviantart] update default archive_fmt for single deviations ([#1874](https://github.com/mikf/gallery-dl/issues/1874))
- [erome] send Referer header for file downloads ([#1829](https://github.com/mikf/gallery-dl/issues/1829))
- [hiperdex] fix extraction
- [kemonoparty] update file download URLs ([#1902](https://github.com/mikf/gallery-dl/issues/1902), [#1903](https://github.com/mikf/gallery-dl/issues/1903))
- [mangadex] fix extraction ([#1852](https://github.com/mikf/gallery-dl/issues/1852))
- [mangadex] fix retrieving chapters from "pornographic" titles ([#1908](https://github.com/mikf/gallery-dl/issues/1908))
- [nozomi] preserve case of search tags ([#1860](https://github.com/mikf/gallery-dl/issues/1860))
- [redgifs][gfycat] remove webtoken code ([#1907](https://github.com/mikf/gallery-dl/issues/1907))
- [twitter] ensure card entries have a `url` ([#1868](https://github.com/mikf/gallery-dl/issues/1868))
- implement a way to correctly shorten displayed filenames containing east-asian characters ([#1377](https://github.com/mikf/gallery-dl/issues/1377))

## 1.18.4 - 2021-09-04
### Additions
- [420chan] add `thread` and `board` extractors ([#1773](https://github.com/mikf/gallery-dl/issues/1773))
- [deviantart] add `tag` extractor ([#1803](https://github.com/mikf/gallery-dl/issues/1803))
- [deviantart] add `comments` option ([#1800](https://github.com/mikf/gallery-dl/issues/1800))
- [deviantart] implement a `auto-watch` option ([#1466](https://github.com/mikf/gallery-dl/issues/1466), [#1757](https://github.com/mikf/gallery-dl/issues/1757))
- [foolfuuka] add `gallery` extractor ([#1785](https://github.com/mikf/gallery-dl/issues/1785))
- [furaffinity] expand URL pattern for searches ([#1780](https://github.com/mikf/gallery-dl/issues/1780))
- [kemonoparty] automatically generate required DDoS-GUARD cookies ([#1779](https://github.com/mikf/gallery-dl/issues/1779))
- [nhentai] add `favorite` extractor ([#1814](https://github.com/mikf/gallery-dl/issues/1814))
- [shopify] support windsorstore.com ([#1793](https://github.com/mikf/gallery-dl/issues/1793))
- [twitter] add `url` to user objects ([#1787](https://github.com/mikf/gallery-dl/issues/1787), [#1532](https://github.com/mikf/gallery-dl/issues/1532))
- [twitter] expand t.co links in user descriptions ([#1787](https://github.com/mikf/gallery-dl/issues/1787), [#1532](https://github.com/mikf/gallery-dl/issues/1532))
- show a warning if an extractor doesn`t yield any results ([#1428](https://github.com/mikf/gallery-dl/issues/1428), [#1759](https://github.com/mikf/gallery-dl/issues/1759))
- add a `j` format string conversion
- implement a `fallback` option ([#1770](https://github.com/mikf/gallery-dl/issues/1770))
- implement a `path-strip` option
### Changes
- [shopify] use API for product listings ([#1793](https://github.com/mikf/gallery-dl/issues/1793))
- update default User-Agent headers
### Fixes
- [deviantart] prevent exceptions for "empty" videos ([#1796](https://github.com/mikf/gallery-dl/issues/1796))
- [exhentai] improve image limits check ([#1808](https://github.com/mikf/gallery-dl/issues/1808))
- [inkbunny] fix extraction ([#1816](https://github.com/mikf/gallery-dl/issues/1816))
- [mangadex] prevent exceptions for manga without English title ([#1815](https://github.com/mikf/gallery-dl/issues/1815))
- [oauth] use defaults when config values are set to `null` ([#1778](https://github.com/mikf/gallery-dl/issues/1778))
- [pixiv] fix pixivision title extraction
- [reddit] delay RedditAPI initialization ([#1813](https://github.com/mikf/gallery-dl/issues/1813))
- [twitter] improve error reporting ([#1759](https://github.com/mikf/gallery-dl/issues/1759))
- [twitter] fix issue when filtering quote tweets ([#1792](https://github.com/mikf/gallery-dl/issues/1792))
- [twitter] fix `logout` option ([#1719](https://github.com/mikf/gallery-dl/issues/1719))
### Removals
- [deviantart] remove the "you need session cookies to download mature scraps" warning ([#1777](https://github.com/mikf/gallery-dl/issues/1777), [#1776](https://github.com/mikf/gallery-dl/issues/1776))
- [foolslide] remove entry for kobato.hologfx.com

## 1.18.3 - 2021-08-13
### Additions
- [bbc] add `width` option ([#1706](https://github.com/mikf/gallery-dl/issues/1706))
- [danbooru] add `external` option ([#1747](https://github.com/mikf/gallery-dl/issues/1747))
- [furaffinity] add `external` option ([#1492](https://github.com/mikf/gallery-dl/issues/1492))
- [luscious] add `gif` option ([#1701](https://github.com/mikf/gallery-dl/issues/1701))
- [newgrounds] add `format` option ([#1729](https://github.com/mikf/gallery-dl/issues/1729))
- [reactor] add `gif` option ([#1701](https://github.com/mikf/gallery-dl/issues/1701))
- [twitter] warn about suspended accounts ([#1759](https://github.com/mikf/gallery-dl/issues/1759))
- [twitter] extend `replies` option ([#1254](https://github.com/mikf/gallery-dl/issues/1254))
- [twitter] add option to log out and retry when blocked ([#1719](https://github.com/mikf/gallery-dl/issues/1719))
- [wikieat] add `thread` and `board` extractors ([#1699](https://github.com/mikf/gallery-dl/issues/1699), [#1607](https://github.com/mikf/gallery-dl/issues/1607))
### Changes
- [instagram] increase default delay between HTTP requests from 5s to 8s ([#1732](https://github.com/mikf/gallery-dl/issues/1732))
### Fixes
- [bbc] improve image dimensions ([#1706](https://github.com/mikf/gallery-dl/issues/1706))
- [bbc] support multi-page gallery listings ([#1730](https://github.com/mikf/gallery-dl/issues/1730))
- [behance] fix `collection` extraction
- [deviantart] get original files for GIF previews ([#1731](https://github.com/mikf/gallery-dl/issues/1731))
- [furaffinity] fix errors when using `category-transfer` ([#1274](https://github.com/mikf/gallery-dl/issues/1274))
- [hitomi] fix image URLs ([#1765](https://github.com/mikf/gallery-dl/issues/1765))
- [instagram] use custom User-Agent header for video downloads ([#1682](https://github.com/mikf/gallery-dl/issues/1682), [#1623](https://github.com/mikf/gallery-dl/issues/1623), [#1580](https://github.com/mikf/gallery-dl/issues/1580))
- [kemonoparty] fix username extraction ([#1750](https://github.com/mikf/gallery-dl/issues/1750))
- [kemonoparty] update file server domain ([#1764](https://github.com/mikf/gallery-dl/issues/1764))
- [newgrounds] fix errors when using `category-transfer` ([#1274](https://github.com/mikf/gallery-dl/issues/1274))
- [nsfwalbum] retry backend requests when extracting image URLs ([#1733](https://github.com/mikf/gallery-dl/issues/1733), [#1271](https://github.com/mikf/gallery-dl/issues/1271))
- [vk] prevent exception for empty/private profiles ([#1742](https://github.com/mikf/gallery-dl/issues/1742))

## 1.18.2 - 2021-07-23
### Additions
- [bbc] add `gallery` and `programme` extractors ([#1706](https://github.com/mikf/gallery-dl/issues/1706))
- [comicvine] add extractor ([#1712](https://github.com/mikf/gallery-dl/issues/1712))
- [kemonoparty] add `max-posts` option ([#1674](https://github.com/mikf/gallery-dl/issues/1674))
- [kemonoparty] parse `o` query parameters ([#1674](https://github.com/mikf/gallery-dl/issues/1674))
- [mastodon] add `reblogs` and `replies` options ([#1669](https://github.com/mikf/gallery-dl/issues/1669))
- [pixiv] add extractor for `pixivision` articles ([#1672](https://github.com/mikf/gallery-dl/issues/1672))
- [ytdl] add experimental extractor for sites supported by youtube-dl ([#1680](https://github.com/mikf/gallery-dl/issues/1680), [#878](https://github.com/mikf/gallery-dl/issues/878))
- extend `parent-metadata` functionality ([#1687](https://github.com/mikf/gallery-dl/issues/1687), [#1651](https://github.com/mikf/gallery-dl/issues/1651), [#1364](https://github.com/mikf/gallery-dl/issues/1364))
- add `archive-prefix` option ([#1711](https://github.com/mikf/gallery-dl/issues/1711))
- add `url-metadata` option ([#1659](https://github.com/mikf/gallery-dl/issues/1659), [#1073](https://github.com/mikf/gallery-dl/issues/1073))
### Changes
- [kemonoparty] skip duplicated patreon files ([#1689](https://github.com/mikf/gallery-dl/issues/1689), [#1667](https://github.com/mikf/gallery-dl/issues/1667))
- [mangadex] use custom User-Agent header ([#1535](https://github.com/mikf/gallery-dl/issues/1535))
### Fixes
- [hitomi] fix image URLs ([#1679](https://github.com/mikf/gallery-dl/issues/1679))
- [imagevenue] fix extraction ([#1677](https://github.com/mikf/gallery-dl/issues/1677))
- [instagram] fix extraction of `/explore/tags/` posts ([#1666](https://github.com/mikf/gallery-dl/issues/1666))
- [moebooru] fix `tags` ending with a `+` when logged in ([#1702](https://github.com/mikf/gallery-dl/issues/1702))
- [naverwebtoon] fix comic extraction
- [pururin] update domain and fix extraction
- [vk] improve metadata extraction and URL pattern ([#1691](https://github.com/mikf/gallery-dl/issues/1691))
- [downloader:ytdl] fix `outtmpl` setting for yt-dlp ([#1680](https://github.com/mikf/gallery-dl/issues/1680))

## 1.18.1 - 2021-07-04
### Additions
- [mangafox] add `manga` extractor ([#1633](https://github.com/mikf/gallery-dl/issues/1633))
- [mangasee] add `chapter` and `manga` extractors
- [mastodon] implement `text-posts` option ([#1569](https://github.com/mikf/gallery-dl/issues/1569), [#1669](https://github.com/mikf/gallery-dl/issues/1669))
- [seisoparty] add `user` and `post` extractors ([#1635](https://github.com/mikf/gallery-dl/issues/1635))
- implement conditional directories ([#1394](https://github.com/mikf/gallery-dl/issues/1394))
- add `T` format string conversion ([#1646](https://github.com/mikf/gallery-dl/issues/1646))
- document format string syntax
### Changes
- [twitter] set `retweet_id` for original retweets ([#1481](https://github.com/mikf/gallery-dl/issues/1481))
### Fixes
- [directlink] manually encode Referer URLs ([#1647](https://github.com/mikf/gallery-dl/issues/1647))
- [hiperdex] use domain from input URL
- [kemonoparty] fix `username` extraction ([#1652](https://github.com/mikf/gallery-dl/issues/1652))
- [kemonoparty] warn about missing DDoS-GUARD cookies
- [twitter] ensure guest tokens are returned as string ([#1665](https://github.com/mikf/gallery-dl/issues/1665))
- [webtoons] match arbitrary language codes ([#1643](https://github.com/mikf/gallery-dl/issues/1643))
- fix depth counter in UrlJob when specifying `-g` multiple times

## 1.18.0 - 2021-06-19
### Additions
- [foolfuuka] support `archive.wakarimasen.moe` ([#1595](https://github.com/mikf/gallery-dl/issues/1595))
- [mangadex] implement login with username & password ([#1535](https://github.com/mikf/gallery-dl/issues/1535))
- [mangadex] add extractor for a user's followed feed ([#1535](https://github.com/mikf/gallery-dl/issues/1535))
- [pixiv] support fetching privately followed users ([#1628](https://github.com/mikf/gallery-dl/issues/1628))
- implement conditional filenames ([#1394](https://github.com/mikf/gallery-dl/issues/1394))
- implement `filter` option for post processors ([#1460](https://github.com/mikf/gallery-dl/issues/1460))
- add `-T/--terminate` command-line option ([#1399](https://github.com/mikf/gallery-dl/issues/1399))
- add `-P/--postprocessor` command-line option ([#1583](https://github.com/mikf/gallery-dl/issues/1583))
### Changes
- [kemonoparty] update default filenames and archive IDs ([#1514](https://github.com/mikf/gallery-dl/issues/1514))
- [twitter] update default settings
  - change `retweets` and `quoted` options from `true` to `false`
  - change directory format for search results to the same as other extractors
- require an argument for `--clear-cache`
### Fixes
- [500px] update GraphQL queries
- [furaffinity] improve metadata extraction ([#1630](https://github.com/mikf/gallery-dl/issues/1630))
- [hitomi] update image URL generation ([#1637](https://github.com/mikf/gallery-dl/issues/1637))
- [idolcomplex] improve and fix pagination ([#1594](https://github.com/mikf/gallery-dl/issues/1594), [#1601](https://github.com/mikf/gallery-dl/issues/1601))
- [instagram] fix login ([#1631](https://github.com/mikf/gallery-dl/issues/1631))
- [instagram] update query hashes
- [mangadex] update to API v5 ([#1535](https://github.com/mikf/gallery-dl/issues/1535))
- [mangafox] improve URL pattern ([#1608](https://github.com/mikf/gallery-dl/issues/1608))
- [oauth] prevent exceptions when reporting errors ([#1603](https://github.com/mikf/gallery-dl/issues/1603))
- [philomena] fix tag escapes handling ([#1629](https://github.com/mikf/gallery-dl/issues/1629))
- [redgifs] update API server address ([#1632](https://github.com/mikf/gallery-dl/issues/1632))
- [sankaku] handle empty tags ([#1617](https://github.com/mikf/gallery-dl/issues/1617))
- [subscribestar] improve attachment filenames ([#1609](https://github.com/mikf/gallery-dl/issues/1609))
- [unsplash] update collections URL pattern ([#1627](https://github.com/mikf/gallery-dl/issues/1627))
- [postprocessor:metadata] handle dicts in `mode:tags` ([#1598](https://github.com/mikf/gallery-dl/issues/1598))

## 1.17.5 - 2021-05-30
### Additions
- [kemonoparty] add `metadata` option ([#1548](https://github.com/mikf/gallery-dl/issues/1548))
- [kemonoparty] add `type` metadata field ([#1556](https://github.com/mikf/gallery-dl/issues/1556))
- [mangapark] recognize v2.mangapark URLs ([#1578](https://github.com/mikf/gallery-dl/issues/1578))
- [patreon] extract user-defined `tags` ([#1539](https://github.com/mikf/gallery-dl/issues/1539), [#1540](https://github.com/mikf/gallery-dl/issues/1540))
- [pillowfort] implement login with username & password ([#846](https://github.com/mikf/gallery-dl/issues/846))
- [pillowfort] add `inline` and `external` options ([#846](https://github.com/mikf/gallery-dl/issues/846))
- [pixiv] implement `max-posts` option ([#1558](https://github.com/mikf/gallery-dl/issues/1558))
- [pixiv] add `metadata` option ([#1551](https://github.com/mikf/gallery-dl/issues/1551))
- [twitter] add `text-tweets` option ([#570](https://github.com/mikf/gallery-dl/issues/570))
- [weibo] extend `retweets` option ([#1542](https://github.com/mikf/gallery-dl/issues/1542))
- [postprocessor:ugoira] support using the `image2` demuxer ([#1550](https://github.com/mikf/gallery-dl/issues/1550))
- [postprocessor:ugoira] add `repeat-last-frame` option ([#1550](https://github.com/mikf/gallery-dl/issues/1550))
- support `XDG_CONFIG_HOME` ([#1545](https://github.com/mikf/gallery-dl/issues/1545))
- implement `parent-skip` and `"skip": "terminate"` options ([#1399](https://github.com/mikf/gallery-dl/issues/1399))
### Changes
- [twitter] resolve `t.co` URLs in `content` ([#1532](https://github.com/mikf/gallery-dl/issues/1532))
### Fixes
- [500px] update query hashes ([#1573](https://github.com/mikf/gallery-dl/issues/1573))
- [aryion] find text posts in `recursive=false` mode ([#1568](https://github.com/mikf/gallery-dl/issues/1568))
- [imagebam] fix extraction of NSFW images ([#1534](https://github.com/mikf/gallery-dl/issues/1534))
- [imgur] update URL patterns ([#1561](https://github.com/mikf/gallery-dl/issues/1561))
- [manganelo] update domain to `manganato.com`
- [reactor] skip deleted/empty posts
- [twitter] add missing retweet media entities ([#1555](https://github.com/mikf/gallery-dl/issues/1555))
- fix ISO 639-1 code for Japanese (`jp` -> `ja`)

## 1.17.4 - 2021-05-07
### Additions
- [gelbooru] add extractor for `/redirect.php` URLs ([#1530](https://github.com/mikf/gallery-dl/issues/1530))
- [inkbunny] add `favorite` extractor ([#1521](https://github.com/mikf/gallery-dl/issues/1521))
- add `output.skip` option
- add an optional argument to `--clear-cache` to select which cache entries to remove ([#1230](https://github.com/mikf/gallery-dl/issues/1230))
### Changes
- [pixiv] update `translated-tags` option ([#1507](https://github.com/mikf/gallery-dl/issues/1507))
  - rename to `tags`
  - accept `"japanese"`, `"translated"`, and `"original"` as values
### Fixes
- [500px] update query hashes
- [kemonoparty] fix download URLs ([#1514](https://github.com/mikf/gallery-dl/issues/1514))
- [imagebam] fix extraction
- [instagram] update query hashes
- [nozomi] update default archive-fmt for `tag` and `search` extractors ([#1529](https://github.com/mikf/gallery-dl/issues/1529))
- [pixiv] remove duplicate translated tags ([#1507](https://github.com/mikf/gallery-dl/issues/1507))
- [readcomiconline] change domain to `readcomiconline.li` ([#1517](https://github.com/mikf/gallery-dl/issues/1517))
- [sankaku] update invalid-token detection ([#1515](https://github.com/mikf/gallery-dl/issues/1515))
- fix crash when using `--no-download` with `--ugoira-conv` ([#1507](https://github.com/mikf/gallery-dl/issues/1507))

## 1.17.3 - 2021-04-25
### Additions
- [danbooru] add option for extended metadata extraction ([#1458](https://github.com/mikf/gallery-dl/issues/1458))
- [fanbox] add extractors ([#1459](https://github.com/mikf/gallery-dl/issues/1459))
- [fantia] add extractors ([#1459](https://github.com/mikf/gallery-dl/issues/1459))
- [gelbooru] add an option to extract notes ([#1457](https://github.com/mikf/gallery-dl/issues/1457))
- [hentaicosplays] add extractor ([#907](https://github.com/mikf/gallery-dl/issues/907), [#1473](https://github.com/mikf/gallery-dl/issues/1473), [#1483](https://github.com/mikf/gallery-dl/issues/1483))
- [instagram] add extractor for `tagged` posts ([#1439](https://github.com/mikf/gallery-dl/issues/1439))
- [naverwebtoon] ignore non-comic images
- [pixiv] also save untranslated tags when `translated-tags` is enabled ([#1501](https://github.com/mikf/gallery-dl/issues/1501))
- [shopify] support omgmiamiswimwear.com ([#1280](https://github.com/mikf/gallery-dl/issues/1280))
- implement `output.fallback` option
- add archive format to InfoJob output ([#875](https://github.com/mikf/gallery-dl/issues/875))
- build executables with SOCKS proxy support ([#1424](https://github.com/mikf/gallery-dl/issues/1424))
### Fixes
- [500px] update query hashes
- [8muses] fix JSON deobfuscation
- [artstation] download `/4k/` images ([#1422](https://github.com/mikf/gallery-dl/issues/1422))
- [deviantart] fix pagination for Eclipse results ([#1444](https://github.com/mikf/gallery-dl/issues/1444))
- [deviantart] improve folder name matching ([#1451](https://github.com/mikf/gallery-dl/issues/1451))
- [erome] skip deleted albums ([#1447](https://github.com/mikf/gallery-dl/issues/1447))
- [exhentai] fix image limit detection ([#1437](https://github.com/mikf/gallery-dl/issues/1437))
- [exhentai] restore `limits` option ([#1487](https://github.com/mikf/gallery-dl/issues/1487))
- [gelbooru] fix tag category extraction ([#1455](https://github.com/mikf/gallery-dl/issues/1455))
- [instagram] update query hashes
- [komikcast] fix extraction
- [simplyhentai] fix extraction
- [slideshare] fix extraction
- [webtoons] update agegate/GDPR cookies ([#1431](https://github.com/mikf/gallery-dl/issues/1431))
- fix `category-transfer` option
### Removals
- [yuki] remove module for yuki.la

## 1.17.2 - 2021-04-02
### Additions
- [deviantart] add support for posts from watched users ([#794](https://github.com/mikf/gallery-dl/issues/794))
- [manganelo] add `chapter` and `manga` extractors ([#1415](https://github.com/mikf/gallery-dl/issues/1415))
- [pinterest] add `search` extractor ([#1411](https://github.com/mikf/gallery-dl/issues/1411))
- [sankaku] add `tag_string` metadata field ([#1388](https://github.com/mikf/gallery-dl/issues/1388))
- [sankaku] add enumeration index for books ([#1388](https://github.com/mikf/gallery-dl/issues/1388))
- [tapas] add `series` and `episode` extractors ([#692](https://github.com/mikf/gallery-dl/issues/692))
- [tapas] implement login with username & password ([#692](https://github.com/mikf/gallery-dl/issues/692))
- [twitter] allow specifying a custom format for user results ([#1337](https://github.com/mikf/gallery-dl/issues/1337))
- [twitter] add extractor for direct image links ([#1417](https://github.com/mikf/gallery-dl/issues/1417))
- [vk] add support for albums ([#474](https://github.com/mikf/gallery-dl/issues/474))
### Fixes
- [aryion] unescape paths ([#1414](https://github.com/mikf/gallery-dl/issues/1414))
- [bcy] improve pagination
- [deviantart] update `watch` URL pattern ([#794](https://github.com/mikf/gallery-dl/issues/794))
- [deviantart] fix arguments for search/popular results ([#1408](https://github.com/mikf/gallery-dl/issues/1408))
- [deviantart] use fallback for `/intermediary/` URLs
- [exhentai] improve and simplify image limit checks
- [komikcast] fix extraction
- [pixiv] fix `favorite` URL pattern ([#1405](https://github.com/mikf/gallery-dl/issues/1405))
- [sankaku] simplify `pool` tags ([#1388](https://github.com/mikf/gallery-dl/issues/1388))
- [twitter] improve error message when trying to log in with 2FA ([#1409](https://github.com/mikf/gallery-dl/issues/1409))
- [twitter] don't use youtube-dl for cards when videos are disabled ([#1416](https://github.com/mikf/gallery-dl/issues/1416))

## 1.17.1 - 2021-03-19
### Additions
- [architizer] add `project` and `firm` extractors ([#1369](https://github.com/mikf/gallery-dl/issues/1369))
- [deviantart] add `watch` extractor ([#794](https://github.com/mikf/gallery-dl/issues/794))
- [exhentai] support `/tag/` URLs ([#1363](https://github.com/mikf/gallery-dl/issues/1363))
- [gelbooru_v01] support `drawfriends.booru.org`, `vidyart.booru.org`, and `tlb.booru.org` by default
- [nozomi] support `/index-N.html` URLs ([#1365](https://github.com/mikf/gallery-dl/issues/1365))
- [philomena] add generalized extractors for philomena sites ([#1379](https://github.com/mikf/gallery-dl/issues/1379))
- [philomena] support post URLs without `/images/`
- [twitter] implement `users` option ([#1337](https://github.com/mikf/gallery-dl/issues/1337))
- implement `parent-metadata` option ([#1364](https://github.com/mikf/gallery-dl/issues/1364))
### Changes
- [deviantart] revert previous changes to `extra` option ([#1356](https://github.com/mikf/gallery-dl/issues/1356), [#1387](https://github.com/mikf/gallery-dl/issues/1387))
### Fixes
- [exhentai] improve favorites count extraction ([#1360](https://github.com/mikf/gallery-dl/issues/1360))
- [gelbooru] update domain for video downloads ([#1368](https://github.com/mikf/gallery-dl/issues/1368))
- [hentaifox] improve image and metadata extraction ([#1366](https://github.com/mikf/gallery-dl/issues/1366), [#1378](https://github.com/mikf/gallery-dl/issues/1378))
- [imgur] fix and improve rate limit handling ([#1386](https://github.com/mikf/gallery-dl/issues/1386))
- [weasyl] improve favorites URL pattern ([#1374](https://github.com/mikf/gallery-dl/issues/1374))
- use type check before applying `browser` option ([#1358](https://github.com/mikf/gallery-dl/issues/1358))
- ensure `-s/--simulate` always prints filenames ([#1360](https://github.com/mikf/gallery-dl/issues/1360))
### Removals
- [hentaicafe]  remove module
- [hentainexus] remove module
- [mangareader] remove module
- [mangastream] remove module

## 1.17.0 - 2021-03-05
### Additions
- [cyberdrop] add support for `https://cyberdrop.me/` ([#1328](https://github.com/mikf/gallery-dl/issues/1328))
- [exhentai] add `metadata` option; extract more metadata from gallery pages ([#1325](https://github.com/mikf/gallery-dl/issues/1325))
- [hentaicafe] add `search` and `tag` extractors ([#1345](https://github.com/mikf/gallery-dl/issues/1345))
- [hentainexus] add `original` option ([#1322](https://github.com/mikf/gallery-dl/issues/1322))
- [instagram] support `/user/reels/` URLs ([#1329](https://github.com/mikf/gallery-dl/issues/1329))
- [naverwebtoon] add support for `https://comic.naver.com/` ([#1331](https://github.com/mikf/gallery-dl/issues/1331))
- [pixiv] add `translated-tags` option ([#1354](https://github.com/mikf/gallery-dl/issues/1354))
- [tbib] add support for `https://tbib.org/` ([#473](https://github.com/mikf/gallery-dl/issues/473), [#1082](https://github.com/mikf/gallery-dl/issues/1082))
- [tumblrgallery] add support for `https://tumblrgallery.xyz/` ([#1298](https://github.com/mikf/gallery-dl/issues/1298))
- [twitter] add extractor for followed users ([#1337](https://github.com/mikf/gallery-dl/issues/1337))
- [twitter] add option to download all media from conversations ([#1319](https://github.com/mikf/gallery-dl/issues/1319))
- [wallhaven] add `collections` extractor ([#1351](https://github.com/mikf/gallery-dl/issues/1351))
- [snap] allow access to user's .netrc for site authentication ([#1352](https://github.com/mikf/gallery-dl/issues/1352))
- add extractors for Gelbooru v0.1 sites ([#234](https://github.com/mikf/gallery-dl/issues/234), [#426](https://github.com/mikf/gallery-dl/issues/426), [#473](https://github.com/mikf/gallery-dl/issues/473), [#767](https://github.com/mikf/gallery-dl/issues/767), [#1238](https://github.com/mikf/gallery-dl/issues/1238))
- add `-E/--extractor-info` command-line option ([#875](https://github.com/mikf/gallery-dl/issues/875))
- add GitHub Actions workflow for building standalone executables ([#1312](https://github.com/mikf/gallery-dl/issues/1312))
- add `browser` and `headers` options ([#1117](https://github.com/mikf/gallery-dl/issues/1117))
- add option to use different youtube-dl forks ([#1330](https://github.com/mikf/gallery-dl/issues/1330))
- support using multiple input files at once ([#1353](https://github.com/mikf/gallery-dl/issues/1353))
### Changes
- [deviantart] extend `extra` option to also download embedded DeviantArt posts.
- [exhentai] rename metadata fields to match API results ([#1325](https://github.com/mikf/gallery-dl/issues/1325))
- [mangadex] use `api.mangadex.org` as default API server
- [mastodon] cache OAuth tokens ([#616](https://github.com/mikf/gallery-dl/issues/616))
- replace `wait-min` and `wait-max` with `sleep-request`
### Fixes
- [500px] skip unavailable photos ([#1335](https://github.com/mikf/gallery-dl/issues/1335))
- [komikcast] fix extraction
- [readcomiconline] download high quality image versions ([#1347](https://github.com/mikf/gallery-dl/issues/1347))
- [twitter] update GraphQL endpoints
- fix crash when `base-directory` is an empty string ([#1339](https://github.com/mikf/gallery-dl/issues/1339))
### Removals
- remove support for formerly deprecated options
- remove `cloudflare` module

## 1.16.5 - 2021-02-14
### Additions
- [behance] support `video` modules ([#1282](https://github.com/mikf/gallery-dl/issues/1282))
- [erome] add `album`, `user`, and `search` extractors ([#409](https://github.com/mikf/gallery-dl/issues/409))
- [hentaifox] support searching by group ([#1294](https://github.com/mikf/gallery-dl/issues/1294))
- [imgclick] add `image` extractor ([#1307](https://github.com/mikf/gallery-dl/issues/1307))
- [kemonoparty] extract inline images ([#1286](https://github.com/mikf/gallery-dl/issues/1286))
- [kemonoparty] support URLs with non-numeric user and post IDs ([#1303](https://github.com/mikf/gallery-dl/issues/1303))
- [pillowfort] add `user` and `post` extractors ([#846](https://github.com/mikf/gallery-dl/issues/846))
### Changes
- [kemonoparty] include `service` in directories and archive keys
- [pixiv] require a `refresh-token` to login ([#1304](https://github.com/mikf/gallery-dl/issues/1304))
- [snap] use `core18` as base
### Fixes
- [500px] update query hashes
- [deviantart] update parameters for `/browse/popular` ([#1267](https://github.com/mikf/gallery-dl/issues/1267))
- [deviantart] provide filename extension for original file downloads ([#1272](https://github.com/mikf/gallery-dl/issues/1272))
- [deviantart] fix `folders` option ([#1302](https://github.com/mikf/gallery-dl/issues/1302))
- [inkbunny] add `sid` parameter to private file downloads ([#1281](https://github.com/mikf/gallery-dl/issues/1281))
- [kemonoparty] fix absolute file URLs
- [mangadex] revert to `https://mangadex.org/api/` and add `api-server` option ([#1310](https://github.com/mikf/gallery-dl/issues/1310))
- [nsfwalbum] use fallback for deleted content ([#1259](https://github.com/mikf/gallery-dl/issues/1259))
- [sankaku] update `invalid token` detection ([#1309](https://github.com/mikf/gallery-dl/issues/1309))
- [slideshare] fix extraction
- [postprocessor:metadata] fix crash with `extension-format` ([#1285](https://github.com/mikf/gallery-dl/issues/1285))

## 1.16.4 - 2021-01-23
### Additions
- [furaffinity] add `descriptions` option ([#1231](https://github.com/mikf/gallery-dl/issues/1231))
- [kemonoparty] add `user` and `post` extractors ([#1216](https://github.com/mikf/gallery-dl/issues/1216))
- [nozomi] add `num` enumeration index ([#1239](https://github.com/mikf/gallery-dl/issues/1239))
- [photovogue] added portfolio extractor ([#1253](https://github.com/mikf/gallery-dl/issues/1253))
- [twitter] match `/i/user/ID` URLs
- [unsplash] add extractors ([#1197](https://github.com/mikf/gallery-dl/issues/1197))
- [vipr] add image extractor ([#1258](https://github.com/mikf/gallery-dl/issues/1258))
### Changes
- [derpibooru] use "Everything" filter by default ([#862](https://github.com/mikf/gallery-dl/issues/862))
### Fixes
- [derpibooru] update `date` parsing
- [foolfuuka] stop search when results are exhausted ([#1174](https://github.com/mikf/gallery-dl/issues/1174))
- [instagram] fix regex for `/saved` URLs ([#1251](https://github.com/mikf/gallery-dl/issues/1251))
- [mangadex] update API URLs
- [mangakakalot] fix extraction
- [newgrounds] fix flash file extraction ([#1257](https://github.com/mikf/gallery-dl/issues/1257))
- [sankaku] simplify login process
- [twitter] fix retries after hitting rate limit

## 1.16.3 - 2021-01-10
### Fixes
- fix crash when using a `dict` for `path-restrict`
- [postprocessor:metadata] sanitize custom filenames

## 1.16.2 - 2021-01-09
### Additions
- [derpibooru] add `search` and `gallery` extractors ([#862](https://github.com/mikf/gallery-dl/issues/862))
- [foolfuuka] add `board` and `search` extractors ([#1044](https://github.com/mikf/gallery-dl/issues/1044), [#1174](https://github.com/mikf/gallery-dl/issues/1174))
- [gfycat] add `date` metadata field ([#1138](https://github.com/mikf/gallery-dl/issues/1138))
- [pinterest] add support for getting all boards of a user ([#1205](https://github.com/mikf/gallery-dl/issues/1205))
- [sankaku] add support for book searches ([#1204](https://github.com/mikf/gallery-dl/issues/1204))
- [twitter] fetch media from pinned tweets ([#1203](https://github.com/mikf/gallery-dl/issues/1203))
- [wikiart] add extractor for single paintings ([#1233](https://github.com/mikf/gallery-dl/issues/1233))
- [downloader:http] add MIME type and signature for `.ico` files ([#1211](https://github.com/mikf/gallery-dl/issues/1211))
- add `d` format string conversion for timestamp values
- add `"ascii"` as a special `path-restrict` value
### Fixes
- [hentainexus] fix extraction ([#1234](https://github.com/mikf/gallery-dl/issues/1234))
- [instagram] categorize single highlight URLs as `highlights` ([#1222](https://github.com/mikf/gallery-dl/issues/1222))
- [redgifs] fix search results
- [twitter] fix login with username & password
- [twitter] fetch tweets from `homeConversation` entries

## 1.16.1 - 2020-12-27
### Additions
- [instagram] add `include` option ([#1180](https://github.com/mikf/gallery-dl/issues/1180))
- [pinterest] implement video support ([#1189](https://github.com/mikf/gallery-dl/issues/1189))
- [sankaku] reimplement login support ([#1176](https://github.com/mikf/gallery-dl/issues/1176), [#1182](https://github.com/mikf/gallery-dl/issues/1182))
- [sankaku] add support for sankaku.app URLs ([#1193](https://github.com/mikf/gallery-dl/issues/1193))
### Changes
- [e621] return pool posts in order ([#1195](https://github.com/mikf/gallery-dl/issues/1195))
- [hentaicafe] prefer title of `/hc.fyi/` pages ([#1106](https://github.com/mikf/gallery-dl/issues/1106))
- [hentaicafe] simplify default filenames
- [sankaku] normalize `created_at` metadata ([#1190](https://github.com/mikf/gallery-dl/issues/1190))
- [postprocessor:exec] do not add missing `{}` to command ([#1185](https://github.com/mikf/gallery-dl/issues/1185))
### Fixes
- [booru] improve error handling
- [instagram] warn about private profiles ([#1187](https://github.com/mikf/gallery-dl/issues/1187))
- [keenspot] improve redirect handling
- [mangadex] respect `chapter-reverse` settings ([#1194](https://github.com/mikf/gallery-dl/issues/1194))
- [pixiv] output debug message on failed login attempts ([#1192](https://github.com/mikf/gallery-dl/issues/1192))
- increase SQLite connection timeouts ([#1173](https://github.com/mikf/gallery-dl/issues/1173))
### Removals
- [mangapanda] remove module

## 1.16.0 - 2020-12-12
### Additions
- [booru] implement generalized extractors for `*booru` and `moebooru` sites
  - add support for sakugabooru.com ([#1136](https://github.com/mikf/gallery-dl/issues/1136))
  - add support for lolibooru.moe ([#1050](https://github.com/mikf/gallery-dl/issues/1050))
  - provide formattable `date` metadata fields ([#1138](https://github.com/mikf/gallery-dl/issues/1138))
- [postprocessor:metadata] add `event` and `filename` options ([#315](https://github.com/mikf/gallery-dl/issues/315), [#866](https://github.com/mikf/gallery-dl/issues/866), [#984](https://github.com/mikf/gallery-dl/issues/984))
- [postprocessor:exec] add `event` option ([#992](https://github.com/mikf/gallery-dl/issues/992))
### Changes
- [flickr] update default directories and improve metadata consistency ([#828](https://github.com/mikf/gallery-dl/issues/828))
- [sankaku] use API endpoints from `beta.sankakucomplex.com`
- [downloader:http] improve filename extension handling ([#776](https://github.com/mikf/gallery-dl/issues/776))
- replace all JPEG filename extensions with `jpg` by default
### Fixes
- [hentainexus] fix extraction ([#1166](https://github.com/mikf/gallery-dl/issues/1166))
- [instagram] rewrite ([#1113](https://github.com/mikf/gallery-dl/issues/1113), [#1122](https://github.com/mikf/gallery-dl/issues/1122), [#1128](https://github.com/mikf/gallery-dl/issues/1128), [#1130](https://github.com/mikf/gallery-dl/issues/1130), [#1149](https://github.com/mikf/gallery-dl/issues/1149))
- [mangadex] handle external chapters ([#1154](https://github.com/mikf/gallery-dl/issues/1154))
- [nozomi] handle empty `date` fields  ([#1163](https://github.com/mikf/gallery-dl/issues/1163))
- [paheal] create directory for each post ([#1147](https://github.com/mikf/gallery-dl/issues/1147))
- [piczel] update API URLs
- [twitter] update image URL format ([#1145](https://github.com/mikf/gallery-dl/issues/1145))
- [twitter] improve `x-csrf-token` header handling ([#1170](https://github.com/mikf/gallery-dl/issues/1170))
- [webtoons] update `ageGate` cookies
### Removals
- [sankaku] remove login support

## 1.15.4 - 2020-11-27
### Fixes
- [2chan] skip external links
- [hentainexus] fix extraction ([#1125](https://github.com/mikf/gallery-dl/issues/1125))
- [mangadex] switch to API v2 ([#1129](https://github.com/mikf/gallery-dl/issues/1129))
- [mangapanda] use http://
- [mangoxo] fix extraction
- [reddit] skip invalid gallery items ([#1127](https://github.com/mikf/gallery-dl/issues/1127))

## 1.15.3 - 2020-11-13
### Additions
- [sankakucomplex] extract videos and embeds ([#308](https://github.com/mikf/gallery-dl/issues/308))
- [twitter] add support for lists ([#1096](https://github.com/mikf/gallery-dl/issues/1096))
- [postprocessor:metadata] accept string-lists for `content-format` ([#1080](https://github.com/mikf/gallery-dl/issues/1080))
- implement `modules` and `extension-map` options
### Fixes
- [500px] update query hashes
- [8kun] fix file URLs of older posts ([#1101](https://github.com/mikf/gallery-dl/issues/1101))
- [exhentai] update image URL parsing ([#1094](https://github.com/mikf/gallery-dl/issues/1094))
- [hentaifoundry] update `YII_CSRF_TOKEN` cookie handling ([#1083](https://github.com/mikf/gallery-dl/issues/1083))
- [hentaifoundry] use scheme from input URLs ([#1095](https://github.com/mikf/gallery-dl/issues/1095))
- [mangoxo] fix metadata extraction
- [paheal] fix extraction ([#1088](https://github.com/mikf/gallery-dl/issues/1088))
- collect post processors from `basecategory` entries ([#1084](https://github.com/mikf/gallery-dl/issues/1084))

## 1.15.2 - 2020-10-24
### Additions
- [pinterest] implement login support ([#1055](https://github.com/mikf/gallery-dl/issues/1055))
- [reddit] add `date` metadata field ([#1068](https://github.com/mikf/gallery-dl/issues/1068))
- [seiga] add metadata for single image downloads ([#1063](https://github.com/mikf/gallery-dl/issues/1063))
- [twitter] support media from Cards ([#937](https://github.com/mikf/gallery-dl/issues/937), [#1005](https://github.com/mikf/gallery-dl/issues/1005))
- [weasyl] support api-key authentication ([#1057](https://github.com/mikf/gallery-dl/issues/1057))
- add a `t` format string conversion for trimming whitespace ([#1065](https://github.com/mikf/gallery-dl/issues/1065))
### Fixes
- [blogger] handle URLs with specified width/height ([#1061](https://github.com/mikf/gallery-dl/issues/1061))
- [fallenangels] fix extraction of `.5` chapters
- [gelbooru] rewrite mp4 video URLs ([#1048](https://github.com/mikf/gallery-dl/issues/1048))
- [hitomi] fix image URLs and gallery URL pattern
- [mangadex] unescape more metadata fields ([#1066](https://github.com/mikf/gallery-dl/issues/1066))
- [mangahere] ensure download URLs have a scheme ([#1070](https://github.com/mikf/gallery-dl/issues/1070))
- [mangakakalot] ignore "Go Home" buttons in chapter pages
- [newgrounds] handle embeds without scheme ([#1033](https://github.com/mikf/gallery-dl/issues/1033))
- [newgrounds] provide fallback URLs for video downloads ([#1042](https://github.com/mikf/gallery-dl/issues/1042))
- [xhamster] fix user profile extraction

## 1.15.1 - 2020-10-11
### Additions
- [hentaicafe] add `manga_id` metadata field ([#1036](https://github.com/mikf/gallery-dl/issues/1036))
- [hentaifoundry] add support for stories ([#734](https://github.com/mikf/gallery-dl/issues/734))
- [hentaifoundry] add `include` option
- [newgrounds] extract image embeds ([#1033](https://github.com/mikf/gallery-dl/issues/1033))
- [nijie] add `include` option ([#1018](https://github.com/mikf/gallery-dl/issues/1018))
- [reactor] match URLs without subdomain ([#1053](https://github.com/mikf/gallery-dl/issues/1053))
- [twitter] extend `retweets` option ([#1026](https://github.com/mikf/gallery-dl/issues/1026))
- [weasyl] add extractors ([#977](https://github.com/mikf/gallery-dl/issues/977))
### Fixes
- [500px] update query hashes
- [behance] fix `collection` extraction
- [newgrounds] fix video extraction ([#1042](https://github.com/mikf/gallery-dl/issues/1042))
- [twitter] improve twitpic extraction ([#1019](https://github.com/mikf/gallery-dl/issues/1019))
- [weibo] handle posts with more than 9 images ([#926](https://github.com/mikf/gallery-dl/issues/926))
- [xvideos] fix `title` extraction
- fix crash when using `--download-archive` with `--no-skip` ([#1023](https://github.com/mikf/gallery-dl/issues/1023))
- fix issues with `blacklist`/`whitelist` defaults ([#1051](https://github.com/mikf/gallery-dl/issues/1051), [#1056](https://github.com/mikf/gallery-dl/issues/1056))
### Removals
- [kissmanga] remove module

## 1.15.0 - 2020-09-20
### Additions
- [deviantart] support watchers-only/paid deviations ([#995](https://github.com/mikf/gallery-dl/issues/995))
- [myhentaigallery] add gallery extractor ([#1001](https://github.com/mikf/gallery-dl/issues/1001))
- [twitter] support specifying users by ID ([#980](https://github.com/mikf/gallery-dl/issues/980))
- [twitter] support `/intent/user?user_id=…` URLs ([#980](https://github.com/mikf/gallery-dl/issues/980))
- add `--no-skip` command-line option ([#986](https://github.com/mikf/gallery-dl/issues/986))
- add `blacklist` and `whitelist` options ([#492](https://github.com/mikf/gallery-dl/issues/492), [#844](https://github.com/mikf/gallery-dl/issues/844))
- add `filesize-min` and `filesize-max` options ([#780](https://github.com/mikf/gallery-dl/issues/780))
- add `sleep-extractor` and `sleep-request` options ([#788](https://github.com/mikf/gallery-dl/issues/788))
- write skipped files to archive ([#550](https://github.com/mikf/gallery-dl/issues/550))
### Changes
- [exhentai] update wait time before original image downloads ([#978](https://github.com/mikf/gallery-dl/issues/978))
- [imgur] use new API endpoints for image/album data
- [tumblr] create directories for each post ([#965](https://github.com/mikf/gallery-dl/issues/965))
- support format string replacement fields in download archive paths ([#985](https://github.com/mikf/gallery-dl/issues/985))
- reduce wait time growth rate for HTTP retries from exponential to linear
### Fixes
- [500px] update query hash
- [aryion] improve post ID extraction ([#981](https://github.com/mikf/gallery-dl/issues/981), [#982](https://github.com/mikf/gallery-dl/issues/982))
- [danbooru] handle posts without `id` ([#1004](https://github.com/mikf/gallery-dl/issues/1004))
- [furaffinity] update download URL extraction ([#988](https://github.com/mikf/gallery-dl/issues/988))
- [imgur] fix image/album detection for galleries
- [postprocessor:zip] defer zip file creation ([#968](https://github.com/mikf/gallery-dl/issues/968))
### Removals
- [jaiminisbox] remove extractors
- [worldthree] remove extractors

## 1.14.5 - 2020-08-30
### Additions
- [aryion] add username/password support ([#960](https://github.com/mikf/gallery-dl/issues/960))
- [exhentai] add ability to specify a custom image limit ([#940](https://github.com/mikf/gallery-dl/issues/940))
- [furaffinity] add `search` extractor ([#915](https://github.com/mikf/gallery-dl/issues/915))
- [imgur] add `search` and `tag` extractors ([#934](https://github.com/mikf/gallery-dl/issues/934))
### Fixes
- [500px] fix extraction and update URL patterns ([#956](https://github.com/mikf/gallery-dl/issues/956))
- [aryion] update folder mime type list ([#945](https://github.com/mikf/gallery-dl/issues/945))
- [gelbooru] fix extraction without API
- [hentaihand] update to new site layout
- [hitomi] fix redirect processing
- [reddit] handle deleted galleries ([#953](https://github.com/mikf/gallery-dl/issues/953))
- [reddit] improve gallery extraction ([#955](https://github.com/mikf/gallery-dl/issues/955))

## 1.14.4 - 2020-08-15
### Additions
- [blogger] add `search` extractor ([#925](https://github.com/mikf/gallery-dl/issues/925))
- [blogger] support searching posts by labels ([#925](https://github.com/mikf/gallery-dl/issues/925))
- [inkbunny] add `user` and `post` extractors ([#283](https://github.com/mikf/gallery-dl/issues/283))
- [instagram] support `/reel/` URLs
- [pinterest] support `pinterest.co.uk` URLs ([#914](https://github.com/mikf/gallery-dl/issues/914))
- [reddit] support gallery posts ([#920](https://github.com/mikf/gallery-dl/issues/920))
- [subscribestar] extract attached media files ([#852](https://github.com/mikf/gallery-dl/issues/852))
### Fixes
- [blogger] improve error messages for missing posts/blogs ([#903](https://github.com/mikf/gallery-dl/issues/903))
- [exhentai] adjust image limit costs ([#940](https://github.com/mikf/gallery-dl/issues/940))
- [gfycat] skip malformed gfycat responses ([#902](https://github.com/mikf/gallery-dl/issues/902))
- [imgur] handle 403 overcapacity responses ([#910](https://github.com/mikf/gallery-dl/issues/910))
- [instagram] wait before GraphQL requests ([#901](https://github.com/mikf/gallery-dl/issues/901))
- [mangareader] fix extraction
- [mangoxo] fix login
- [pixnet] detect password-protected albums ([#177](https://github.com/mikf/gallery-dl/issues/177))
- [simplyhentai] fix `gallery_id` extraction
- [subscribestar] update `date` parsing
- [vsco] handle missing `description` fields
- [xhamster] fix extraction ([#917](https://github.com/mikf/gallery-dl/issues/917))
- allow `parent-directory` to work recursively ([#905](https://github.com/mikf/gallery-dl/issues/905))
- skip external OAuth tests ([#908](https://github.com/mikf/gallery-dl/issues/908))
### Removals
- [bobx] remove module

## 1.14.3 - 2020-07-18
### Additions
- [8muses] support `comics.8muses.com` URLs
- [artstation] add `following` extractor ([#888](https://github.com/mikf/gallery-dl/issues/888))
- [exhentai] add `domain` option ([#897](https://github.com/mikf/gallery-dl/issues/897))
- [gfycat] add `user` and `search` extractors
- [imgur] support all `/t/...` URLs ([#880](https://github.com/mikf/gallery-dl/issues/880))
- [khinsider] add `format` option ([#840](https://github.com/mikf/gallery-dl/issues/840))
- [mangakakalot] add `manga` and `chapter` extractors ([#876](https://github.com/mikf/gallery-dl/issues/876))
- [redgifs] support `gifsdeliverynetwork.com` URLs ([#874](https://github.com/mikf/gallery-dl/issues/874))
- [subscribestar] add `user` and `post` extractors ([#852](https://github.com/mikf/gallery-dl/issues/852))
- [twitter] add support for nitter.net URLs ([#890](https://github.com/mikf/gallery-dl/issues/890))
- add Zsh completion script ([#150](https://github.com/mikf/gallery-dl/issues/150))
### Fixes
- [gfycat] retry 404'ed videos on redgifs.com ([#874](https://github.com/mikf/gallery-dl/issues/874))
- [newgrounds] fix favorites extraction
- [patreon] yield images and attachments before post files ([#871](https://github.com/mikf/gallery-dl/issues/871))
- [reddit] fix AttributeError when using `recursion` ([#879](https://github.com/mikf/gallery-dl/issues/879))
- [twitter] raise proper exception if a user doesn't exist ([#891](https://github.com/mikf/gallery-dl/issues/891))
- defer directory creation ([#722](https://github.com/mikf/gallery-dl/issues/722))
- set pseudo extension for Metadata messages ([#865](https://github.com/mikf/gallery-dl/issues/865))
- prevent exception on Cloudflare challenges ([#868](https://github.com/mikf/gallery-dl/issues/868))

## 1.14.2 - 2020-06-27
### Additions
- [artstation] add `date` metadata field ([#839](https://github.com/mikf/gallery-dl/issues/839))
- [mastodon] add `date` metadata field ([#839](https://github.com/mikf/gallery-dl/issues/839))
- [pinterest] add support for board sections ([#835](https://github.com/mikf/gallery-dl/issues/835))
- [twitter] add extractor for liked tweets ([#837](https://github.com/mikf/gallery-dl/issues/837))
- [twitter] add option to filter media from quoted tweets ([#854](https://github.com/mikf/gallery-dl/issues/854))
- [weibo] add `date` metadata field to `status` objects ([#829](https://github.com/mikf/gallery-dl/issues/829))
### Fixes
- [aryion] fix user gallery extraction ([#832](https://github.com/mikf/gallery-dl/issues/832))
- [imgur] build directory paths for each file ([#842](https://github.com/mikf/gallery-dl/issues/842))
- [tumblr] prevent errors when using `reblogs=same-blog` ([#851](https://github.com/mikf/gallery-dl/issues/851))
- [twitter] always provide an `author` metadata field ([#831](https://github.com/mikf/gallery-dl/issues/831), [#833](https://github.com/mikf/gallery-dl/issues/833))
- [twitter] don't download video previews ([#833](https://github.com/mikf/gallery-dl/issues/833))
- [twitter] improve handling of deleted tweets ([#838](https://github.com/mikf/gallery-dl/issues/838))
- [twitter] fix search results ([#847](https://github.com/mikf/gallery-dl/issues/847))
- [twitter] improve handling of quoted tweets ([#854](https://github.com/mikf/gallery-dl/issues/854))
- fix config lookups when multiple locations are involved ([#843](https://github.com/mikf/gallery-dl/issues/843))
- improve output of `-K/--list-keywords` for parent extractors ([#825](https://github.com/mikf/gallery-dl/issues/825))
- call `flush()` after writing JSON in `DataJob()` ([#727](https://github.com/mikf/gallery-dl/issues/727))

## 1.14.1 - 2020-06-12
### Additions
- [furaffinity] add `artist_url` metadata field ([#821](https://github.com/mikf/gallery-dl/issues/821))
- [redgifs] add `user` and `search` extractors ([#724](https://github.com/mikf/gallery-dl/issues/724))
### Changes
- [deviantart] extend `extra` option; also search journals for sta.sh links ([#712](https://github.com/mikf/gallery-dl/issues/712))
- [twitter] rewrite; use new interface ([#806](https://github.com/mikf/gallery-dl/issues/806), [#740](https://github.com/mikf/gallery-dl/issues/740))
### Fixes
- [kissmanga] work around CAPTCHAs ([#818](https://github.com/mikf/gallery-dl/issues/818))
- [nhentai] fix extraction ([#819](https://github.com/mikf/gallery-dl/issues/819))
- [webtoons] generalize comic extraction code ([#820](https://github.com/mikf/gallery-dl/issues/820))

## 1.14.0 - 2020-05-31
### Additions
- [imagechest] add new extractor for imgchest.com ([#750](https://github.com/mikf/gallery-dl/issues/750))
- [instagram] add `post_url`, `tags`, `location`, `tagged_users` metadata ([#743](https://github.com/mikf/gallery-dl/issues/743))
- [redgifs] add image extractor ([#724](https://github.com/mikf/gallery-dl/issues/724))
- [webtoons] add new extractor for webtoons.com ([#761](https://github.com/mikf/gallery-dl/issues/761))
- implement `--write-pages` option ([#736](https://github.com/mikf/gallery-dl/issues/736))
- extend `path-restrict` option ([#662](https://github.com/mikf/gallery-dl/issues/662))
- implement `path-replace` option ([#662](https://github.com/mikf/gallery-dl/issues/662), [#755](https://github.com/mikf/gallery-dl/issues/755))
- make `path` and `keywords` available in logging messages ([#574](https://github.com/mikf/gallery-dl/issues/574), [#575](https://github.com/mikf/gallery-dl/issues/575))
### Changes
- [danbooru] change default value of `ugoira` to `false`
- [downloader:ytdl] change default value of `forward-cookies` to `false`
- [downloader:ytdl] fix file extensions when merging into `.mkv` ([#720](https://github.com/mikf/gallery-dl/issues/720))
- write OAuth tokens to cache ([#616](https://github.com/mikf/gallery-dl/issues/616))
- use `%APPDATA%\gallery-dl` for config files and cache on Windows
- use `util.Formatter` for formatting logging messages
- reuse HTTP connections from parent extractors
### Fixes
- [deviantart] use private access tokens for Journals ([#738](https://github.com/mikf/gallery-dl/issues/738))
- [gelbooru] simplify and fix pool extraction
- [imgur] fix extraction of animated images without `mp4` entry
- [imgur] treat `/t/unmuted/` URLs as galleries
- [instagram] fix login with username & password ([#756](https://github.com/mikf/gallery-dl/issues/756), [#771](https://github.com/mikf/gallery-dl/issues/771), [#797](https://github.com/mikf/gallery-dl/issues/797), [#803](https://github.com/mikf/gallery-dl/issues/803))
- [reddit] don't send OAuth headers for file downloads ([#729](https://github.com/mikf/gallery-dl/issues/729))
- fix/improve Cloudflare bypass code ([#728](https://github.com/mikf/gallery-dl/issues/728), [#757](https://github.com/mikf/gallery-dl/issues/757))
- reset filenames on empty file extensions ([#733](https://github.com/mikf/gallery-dl/issues/733))

## 1.13.6 - 2020-05-02
### Additions
- [patreon] respect filters and sort order in query parameters ([#711](https://github.com/mikf/gallery-dl/issues/711))
- [speakerdeck] add a new extractor for speakerdeck.com ([#726](https://github.com/mikf/gallery-dl/issues/726))
- [twitter] add `replies` option ([#705](https://github.com/mikf/gallery-dl/issues/705))
- [weibo] add `videos` option
- [downloader:http] add MIME types for `.psd` files ([#714](https://github.com/mikf/gallery-dl/issues/714))
### Fixes
- [artstation] improve embed extraction ([#720](https://github.com/mikf/gallery-dl/issues/720))
- [deviantart] limit API wait times ([#721](https://github.com/mikf/gallery-dl/issues/721))
- [newgrounds] fix URLs produced by the `following` extractor ([#684](https://github.com/mikf/gallery-dl/issues/684))
- [patreon] improve file hash extraction ([#713](https://github.com/mikf/gallery-dl/issues/713))
- [vsco] fix user gallery extraction
- fix/improve Cloudflare bypass code ([#728](https://github.com/mikf/gallery-dl/issues/728))

## 1.13.5 - 2020-04-27
### Additions
- [500px] recognize `web.500px.com` URLs
- [aryion] support downloading from folders ([#694](https://github.com/mikf/gallery-dl/issues/694))
- [furaffinity] add extractor for followed users ([#515](https://github.com/mikf/gallery-dl/issues/515))
- [hitomi] add extractor for tag searches ([#697](https://github.com/mikf/gallery-dl/issues/697))
- [instagram] add `post_id` and `num` metadata fields ([#698](https://github.com/mikf/gallery-dl/issues/698))
- [newgrounds] add extractor for followed users ([#684](https://github.com/mikf/gallery-dl/issues/684))
- [patreon] recognize URLs with creator IDs ([#711](https://github.com/mikf/gallery-dl/issues/711))
- [twitter] add `reply` metadata field ([#705](https://github.com/mikf/gallery-dl/issues/705))
- [xhamster] recognize `xhamster.porncache.net` URLs ([#700](https://github.com/mikf/gallery-dl/issues/700))
### Fixes
- [gelbooru] improve post ID extraction in pool listings
- [hitomi] fix extraction of galleries without tags
- [jaiminisbox] update metadata decoding procedure ([#702](https://github.com/mikf/gallery-dl/issues/702))
- [mastodon] fix pagination ([#701](https://github.com/mikf/gallery-dl/issues/701))
- [mastodon] improve account searches ([#704](https://github.com/mikf/gallery-dl/issues/704))
- [patreon] fix hash extraction from download URLs ([#693](https://github.com/mikf/gallery-dl/issues/693))
- improve parameter extraction when solving Cloudflare challenges

## 1.13.4 - 2020-04-12
### Additions
- [aryion] add `gallery` and `post` extractors ([#390](https://github.com/mikf/gallery-dl/issues/390), [#673](https://github.com/mikf/gallery-dl/issues/673))
- [deviantart] detect and handle folders in sta.sh listings ([#659](https://github.com/mikf/gallery-dl/issues/659))
- [hentainexus] add `circle`, `event`, and `title_conventional` metadata fields ([#661](https://github.com/mikf/gallery-dl/issues/661))
- [hiperdex] add `artist` extractor ([#606](https://github.com/mikf/gallery-dl/issues/606))
- [mastodon] add access tokens for `mastodon.social` and `baraag.net` ([#665](https://github.com/mikf/gallery-dl/issues/665))
### Changes
- [deviantart] retrieve *all* download URLs through the OAuth API
- automatically read config files in PyInstaller executable directories ([#682](https://github.com/mikf/gallery-dl/issues/682))
### Fixes
- [deviantart] handle "Request blocked" errors ([#655](https://github.com/mikf/gallery-dl/issues/655))
- [deviantart] improve JPEG quality replacement pattern
- [hiperdex] fix extraction
- [mastodon] handle API rate limits ([#665](https://github.com/mikf/gallery-dl/issues/665))
- [mastodon] update OAuth credentials for pawoo.net ([#665](https://github.com/mikf/gallery-dl/issues/665))
- [myportfolio] fix extraction of galleries without title
- [piczel] fix extraction of single images
- [vsco] fix collection extraction
- [weibo] accept status URLs with non-numeric IDs ([#664](https://github.com/mikf/gallery-dl/issues/664))

## 1.13.3 - 2020-03-28
### Additions
- [instagram] Add support for user's saved medias ([#644](https://github.com/mikf/gallery-dl/issues/644))
- [nozomi] support multiple images per post ([#646](https://github.com/mikf/gallery-dl/issues/646))
- [35photo] add `tag` extractor
### Changes
- [mangadex] transform timestamps from `date` fields to datetime objects
### Fixes
- [deviantart] handle decode errors for `extended_fetch` results ([#655](https://github.com/mikf/gallery-dl/issues/655))
- [e621] fix bug in API rate limiting and improve pagination ([#651](https://github.com/mikf/gallery-dl/issues/651))
- [instagram] update pattern for user profile URLs
- [mangapark] fix metadata extraction
- [nozomi] sort search results ([#646](https://github.com/mikf/gallery-dl/issues/646))
- [piczel] fix extraction
- [twitter] fix typo in `x-twitter-auth-type` header ([#625](https://github.com/mikf/gallery-dl/issues/625))
- remove trailing dots from Windows directory names ([#647](https://github.com/mikf/gallery-dl/issues/647))
- fix crash with missing `stdout`/`stderr`/`stdin` handles ([#653](https://github.com/mikf/gallery-dl/issues/653))

## 1.13.2 - 2020-03-14
### Additions
- [furaffinity] extract more metadata
- [instagram] add `post_shortcode` metadata field ([#525](https://github.com/mikf/gallery-dl/issues/525))
- [kabeuchi] add extractor ([#561](https://github.com/mikf/gallery-dl/issues/561))
- [newgrounds] add extractor for favorited posts ([#394](https://github.com/mikf/gallery-dl/issues/394))
- [pixiv] implement `avatar` option ([#595](https://github.com/mikf/gallery-dl/issues/595), [#623](https://github.com/mikf/gallery-dl/issues/623))
- [twitter] add extractor for bookmarked Tweets ([#625](https://github.com/mikf/gallery-dl/issues/625))
### Fixes
- [bcy] reduce number of HTTP requests during data extraction
- [e621] update to new interface ([#635](https://github.com/mikf/gallery-dl/issues/635))
- [exhentai] handle incomplete MIME types ([#632](https://github.com/mikf/gallery-dl/issues/632))
- [hitomi] improve metadata extraction
- [mangoxo] fix login
- [newgrounds] improve error handling when extracting post data

## 1.13.1 - 2020-03-01
### Additions
- [hentaihand] add extractors ([#605](https://github.com/mikf/gallery-dl/issues/605))
- [hiperdex] add chapter and manga extractors ([#606](https://github.com/mikf/gallery-dl/issues/606))
- [oauth] implement option to write DeviantArt refresh-tokens to cache ([#616](https://github.com/mikf/gallery-dl/issues/616))
- [downloader:http] add more MIME types for `.bmp` and `.rar` files ([#621](https://github.com/mikf/gallery-dl/issues/621), [#628](https://github.com/mikf/gallery-dl/issues/628))
- warn about expired cookies
### Fixes
- [bcy] fix partial image URLs ([#613](https://github.com/mikf/gallery-dl/issues/613))
- [danbooru] fix Ugoira downloads and metadata
- [deviantart] check availability of `/intermediary/` URLs ([#609](https://github.com/mikf/gallery-dl/issues/609))
- [hitomi] follow multiple redirects & fix image URLs
- [piczel] improve and update
- [tumblr] replace `-` with ` ` in tag searches ([#611](https://github.com/mikf/gallery-dl/issues/611))
- [vsco] update gallery URL pattern
- fix `--verbose` and `--quiet` command-line options

## 1.13.0 - 2020-02-16
### Additions
- Support for
  - `furaffinity` - https://www.furaffinity.net/ ([#284](https://github.com/mikf/gallery-dl/issues/284))
  - `8kun`        - https://8kun.top/            ([#582](https://github.com/mikf/gallery-dl/issues/582))
  - `bcy`         - https://bcy.net/             ([#592](https://github.com/mikf/gallery-dl/issues/592))
- [blogger] implement video extraction ([#587](https://github.com/mikf/gallery-dl/issues/587))
- [oauth] add option to specify port number used by local server ([#604](https://github.com/mikf/gallery-dl/issues/604))
- [pixiv] add `rating` metadata field ([#595](https://github.com/mikf/gallery-dl/issues/595))
- [pixiv] recognize tags at the end of new bookmark URLs
- [reddit] add `videos` option
- [weibo] use youtube-dl to download from m3u8 manifests
- implement `parent-directory` option ([#551](https://github.com/mikf/gallery-dl/issues/551))
- extend filename formatting capabilities:
  - implement field name alternatives ([#525](https://github.com/mikf/gallery-dl/issues/525))
  - allow multiple "special" format specifiers per replacement field ([#595](https://github.com/mikf/gallery-dl/issues/595))
  - allow for numeric list and string indices
### Changes
- [reddit] handle reddit-hosted images and videos natively ([#551](https://github.com/mikf/gallery-dl/issues/551))
- [twitter] change default value for `videos` to `true`
### Fixes
- [cloudflare] unescape challenge URLs
- [deviantart] fix video extraction from `extended_fetch` results
- [hitomi] implement workaround for "broken" redirects
- [khinsider] fix and improve metadata extraction
- [patreon] filter duplicate files per post ([#590](https://github.com/mikf/gallery-dl/issues/590))
- [piczel] fix extraction
- [pixiv] fix user IDs for bookmarks API calls ([#596](https://github.com/mikf/gallery-dl/issues/596))
- [sexcom] fix image URLs
- [twitter] force old login page layout ([#584](https://github.com/mikf/gallery-dl/issues/584), [#598](https://github.com/mikf/gallery-dl/issues/598))
- [vsco] skip "invalid" entities
- improve functions to load/save cookies.txt files ([#586](https://github.com/mikf/gallery-dl/issues/586))
### Removals
- [yaplog] remove module

## 1.12.3 - 2020-01-19
### Additions
- [hentaifoundry] extract more metadata ([#565](https://github.com/mikf/gallery-dl/issues/565))
- [twitter] add option to extract TwitPic embeds ([#579](https://github.com/mikf/gallery-dl/issues/579))
- implement a post-processor module to compare file versions ([#530](https://github.com/mikf/gallery-dl/issues/530))
### Fixes
- [hitomi] update image URL generation
- [mangadex] revert domain to `mangadex.org`
- [pinterest] improve detection of invalid pin.it links
- [pixiv] update URL patterns for user profiles and bookmarks ([#568](https://github.com/mikf/gallery-dl/issues/568))
- [twitter] Fix stop before real end ([#573](https://github.com/mikf/gallery-dl/issues/573))
- remove temp files before downloading from fallback URLs
### Removals
- [erolord] remove extractor

## 1.12.2 - 2020-01-05
### Additions
- [deviantart] match new search/popular URLs ([#538](https://github.com/mikf/gallery-dl/issues/538))
- [deviantart] match `/favourites/all` URLs ([#555](https://github.com/mikf/gallery-dl/issues/555))
- [deviantart] add extractor for followed users ([#515](https://github.com/mikf/gallery-dl/issues/515))
- [pixiv] support listing followed users ([#515](https://github.com/mikf/gallery-dl/issues/515))
- [imagefap] handle beta.imagefap.com URLs ([#552](https://github.com/mikf/gallery-dl/issues/552))
- [postprocessor:metadata] add `directory` option ([#520](https://github.com/mikf/gallery-dl/issues/520))
### Fixes
- [artstation] fix search result pagination ([#537](https://github.com/mikf/gallery-dl/issues/537))
- [directlink] send Referer headers ([#536](https://github.com/mikf/gallery-dl/issues/536))
- [exhentai] restrict default directory name length ([#545](https://github.com/mikf/gallery-dl/issues/545))
- [mangadex] change domain to mangadex.cc ([#559](https://github.com/mikf/gallery-dl/issues/559))
- [mangahere] send `isAdult` cookies ([#556](https://github.com/mikf/gallery-dl/issues/556))
- [newgrounds] fix tags metadata extraction
- [pixiv] retry after rate limit errors ([#535](https://github.com/mikf/gallery-dl/issues/535))
- [twitter] handle quoted tweets ([#526](https://github.com/mikf/gallery-dl/issues/526))
- [twitter] handle API rate limits ([#526](https://github.com/mikf/gallery-dl/issues/526))
- [twitter] fix URLs forwarded to youtube-dl ([#540](https://github.com/mikf/gallery-dl/issues/540))
- prevent infinite recursion when spawning new extractors ([#489](https://github.com/mikf/gallery-dl/issues/489))
- improve output of `--list-keywords` for "parent" extractors ([#548](https://github.com/mikf/gallery-dl/issues/548))
- provide fallback for SQLite versions with missing `WITHOUT ROWID` support ([#553](https://github.com/mikf/gallery-dl/issues/553))

## 1.12.1 - 2019-12-22
### Additions
- [4chan] add extractor for entire boards ([#510](https://github.com/mikf/gallery-dl/issues/510))
- [realbooru] add extractors for pools, posts, and tag searches ([#514](https://github.com/mikf/gallery-dl/issues/514))
- [instagram] implement a `videos` option ([#521](https://github.com/mikf/gallery-dl/issues/521))
- [vsco] implement a `videos` option
- [postprocessor:metadata] implement a `bypost` option for downloading the metadata of an entire post ([#511](https://github.com/mikf/gallery-dl/issues/511))
### Changes
- [reddit] change the default value for `comments` to `0`
- [vsco] improve image resolutions
- make filesystem-related errors during file downloads non-fatal ([#512](https://github.com/mikf/gallery-dl/issues/512))
### Fixes
- [foolslide] add fallback for chapter data extraction
- [instagram] ignore errors during post-page extraction
- [patreon] avoid errors when fetching user info ([#508](https://github.com/mikf/gallery-dl/issues/508))
- [patreon] improve URL pattern for single posts
- [reddit] fix errors with `t1` submissions
- [vsco] fix user profile extraction … again
- [weibo] handle unavailable/deleted statuses
- [downloader:http] improve rate limit handling
- retain trailing zeroes in Cloudflare challenge answers

## 1.12.0 - 2019-12-08
### Additions
- [flickr] support 3k, 4k, 5k, and 6k photo sizes ([#472](https://github.com/mikf/gallery-dl/issues/472))
- [imgur] add extractor for subreddit links ([#500](https://github.com/mikf/gallery-dl/issues/500))
- [newgrounds] add extractors for `audio` listings and general `media` files ([#394](https://github.com/mikf/gallery-dl/issues/394))
- [newgrounds] implement login support ([#394](https://github.com/mikf/gallery-dl/issues/394))
- [postprocessor:metadata] implement a `extension-format` option ([#477](https://github.com/mikf/gallery-dl/issues/477))
- `--exec-after`
### Changes
- [deviantart] ensure consistent username capitalization ([#455](https://github.com/mikf/gallery-dl/issues/455))
- [directlink] split `{path}` into `{path}/{filename}.{extension}`
- [twitter] update metadata fields with user/author information
- [postprocessor:metadata] filter private entries & rename `format` to `content-format`
- Enable `cookies-update` by default
### Fixes
- [2chan] fix metadata extraction
- [behance] get images from 'media_collection' modules
- [bobx] fix image downloads by randomly generating session cookies ([#482](https://github.com/mikf/gallery-dl/issues/482))
- [deviantart] revert to getting download URLs from OAuth API calls ([#488](https://github.com/mikf/gallery-dl/issues/488))
- [deviantart] fix URL generation from '/extended_fetch' results ([#505](https://github.com/mikf/gallery-dl/issues/505))
- [flickr] adjust OAuth redirect URI ([#503](https://github.com/mikf/gallery-dl/issues/503))
- [hentaifox] fix extraction
- [imagefap] adapt to new image URL format
- [imgbb] fix error in galleries without user info ([#471](https://github.com/mikf/gallery-dl/issues/471))
- [instagram] prevent errors with missing 'video_url' fields ([#479](https://github.com/mikf/gallery-dl/issues/479))
- [nijie] fix `date` parsing
- [pixiv] match new search URLs ([#507](https://github.com/mikf/gallery-dl/issues/507))
- [plurk] fix comment pagination
- [sexcom] send specific Referer headers when downloading videos
- [twitter] fix infinite loops ([#499](https://github.com/mikf/gallery-dl/issues/499))
- [vsco] fix user profile and collection extraction ([#480](https://github.com/mikf/gallery-dl/issues/480))
- Fix Cloudflare DDoS protection bypass
### Removals
- `--abort-on-skip`

## 1.11.1 - 2019-11-09
### Fixes
- Fix inclusion of bash completion and man pages in source distributions

## 1.11.0 - 2019-11-08
### Additions
- Support for
  - `blogger` - https://www.blogger.com/ ([#364](https://github.com/mikf/gallery-dl/issues/364))
  - `nozomi`  - https://nozomi.la/       ([#388](https://github.com/mikf/gallery-dl/issues/388))
  - `issuu`   - https://issuu.com/       ([#413](https://github.com/mikf/gallery-dl/issues/413))
  - `naver`   - https://blog.naver.com/  ([#447](https://github.com/mikf/gallery-dl/issues/447))
- Extractor for `twitter` search results ([#448](https://github.com/mikf/gallery-dl/issues/448))
- Extractor for `deviantart` user profiles with configurable targets ([#377](https://github.com/mikf/gallery-dl/issues/377), [#419](https://github.com/mikf/gallery-dl/issues/419))
- `--ugoira-conv-lossless` ([#432](https://github.com/mikf/gallery-dl/issues/432))
- `cookies-update` option to allow updating cookies.txt files ([#445](https://github.com/mikf/gallery-dl/issues/445))
- Optional `cloudflare` and `video` installation targets ([#460](https://github.com/mikf/gallery-dl/issues/460))
- Allow executing commands with the `exec` post-processor after all files are downloaded ([#413](https://github.com/mikf/gallery-dl/issues/413), [#421](https://github.com/mikf/gallery-dl/issues/421))
### Changes
- Rewrite `imgur` using its public API ([#446](https://github.com/mikf/gallery-dl/issues/446))
- Rewrite `luscious` using GraphQL queries ([#457](https://github.com/mikf/gallery-dl/issues/457))
- Adjust default `nijie` filenames to match `pixiv`
- Change enumeration index for gallery extractors from `page` to `num`
- Return non-zero exit status when errors occurred
- Forward proxy settings to youtube-dl downloader
- Install bash completion script into `share/bash-completion/completions`
### Fixes
- Adapt to new `instagram` page layout when logged in ([#391](https://github.com/mikf/gallery-dl/issues/391))
- Support protected `twitter` videos ([#452](https://github.com/mikf/gallery-dl/issues/452))
- Extend `hitomi` URL pattern and fix gallery extraction
- Restore OAuth2 authentication error messages
- Miscellaneous fixes for `patreon` ([#444](https://github.com/mikf/gallery-dl/issues/444)), `deviantart` ([#455](https://github.com/mikf/gallery-dl/issues/455)), `sexcom` ([#464](https://github.com/mikf/gallery-dl/issues/464)), `imgur` ([#467](https://github.com/mikf/gallery-dl/issues/467)), `simplyhentai`

## 1.10.6 - 2019-10-11
### Additions
- `--exec` command-line option to specify a command to run after each file download ([#421](https://github.com/mikf/gallery-dl/issues/421))
### Changes
- Include titles in `gfycat` default filenames ([#434](https://github.com/mikf/gallery-dl/issues/434))
### Fixes
- Fetch working download URLs for `deviantart` ([#436](https://github.com/mikf/gallery-dl/issues/436))
- Various fixes and improvements for `yaplog` blogs ([#443](https://github.com/mikf/gallery-dl/issues/443))
- Fix image URL generation for `hitomi` galleries
- Miscellaneous fixes for `behance` and `xvideos`

## 1.10.5 - 2019-09-28
### Additions
- `instagram.highlights` option to include highlighted stories when downloading user profiles ([#329](https://github.com/mikf/gallery-dl/issues/329))
- Support for `/user/` URLs on `reddit` ([#350](https://github.com/mikf/gallery-dl/issues/350))
- Support for `imgur` user profiles and favorites ([#420](https://github.com/mikf/gallery-dl/issues/420))
- Additional metadata fields on `nijie`([#423](https://github.com/mikf/gallery-dl/issues/423))
### Fixes
- Improve handling of private `deviantart` artworks ([#414](https://github.com/mikf/gallery-dl/issues/414)) and 429 status codes ([#424](https://github.com/mikf/gallery-dl/issues/424))
- Prevent fatal errors when trying to open download-archive files ([#417](https://github.com/mikf/gallery-dl/issues/417))
- Detect and ignore unavailable videos on `weibo` ([#427](https://github.com/mikf/gallery-dl/issues/427))
- Update the `scope` of new `reddit` refresh-tokens ([#428](https://github.com/mikf/gallery-dl/issues/428))
- Fix inconsistencies with the `reddit.comments` option ([#429](https://github.com/mikf/gallery-dl/issues/429))
- Extend URL patterns for `hentaicafe` manga and `pixiv` artworks
- Improve detection of unavailable albums on `luscious` and `imgbb`
- Miscellaneous fixes for `tsumino`

## 1.10.4 - 2019-09-08
### Additions
- Support for
  - `lineblog` - https://www.lineblog.me/ ([#404](https://github.com/mikf/gallery-dl/issues/404))
  - `fuskator` - https://fuskator.com/    ([#407](https://github.com/mikf/gallery-dl/issues/407))
- `ugoira` option for `danbooru` to download pre-rendered ugoira animations ([#406](https://github.com/mikf/gallery-dl/issues/406))
### Fixes
- Download the correct files from `twitter` replies ([#403](https://github.com/mikf/gallery-dl/issues/403))
- Prevent crash when trying to use unavailable downloader modules ([#405](https://github.com/mikf/gallery-dl/issues/405))
- Fix `pixiv` authentication ([#411](https://github.com/mikf/gallery-dl/issues/411))
- Improve `exhentai` image limit checks
- Miscellaneous fixes for `hentaicafe`, `simplyhentai`, `tumblr`

## 1.10.3 - 2019-08-30
### Additions
- Provide `filename` metadata for all `deviantart` files ([#392](https://github.com/mikf/gallery-dl/issues/392), [#400](https://github.com/mikf/gallery-dl/issues/400))
- Implement a `ytdl.outtmpl` option to let youtube-dl handle filenames by itself ([#395](https://github.com/mikf/gallery-dl/issues/395))
- Support `seiga` mobile URLs ([#401](https://github.com/mikf/gallery-dl/issues/401))
### Fixes
- Extract more than the first 32 posts from `piczel` galleries ([#396](https://github.com/mikf/gallery-dl/issues/396))
- Fix filenames of archives created with `--zip` ([#397](https://github.com/mikf/gallery-dl/issues/397))
- Skip unavailable images and videos on `flickr` ([#398](https://github.com/mikf/gallery-dl/issues/398))
- Fix filesystem paths on Windows with Python 3.6 and lower ([#402](https://github.com/mikf/gallery-dl/issues/402))

## 1.10.2 - 2019-08-23
### Additions
- Support for `instagram` stories and IGTV ([#371](https://github.com/mikf/gallery-dl/issues/371), [#373](https://github.com/mikf/gallery-dl/issues/373))
- Support for individual `imgbb` images ([#363](https://github.com/mikf/gallery-dl/issues/363))
- `deviantart.quality` option to set the JPEG compression quality for newer images ([#369](https://github.com/mikf/gallery-dl/issues/369))
- `enumerate` option for `extractor.skip` ([#306](https://github.com/mikf/gallery-dl/issues/306))
- `adjust-extensions` option to control filename extension adjustments
- `path-remove` option to remove control characters etc. from filesystem paths
### Changes
- Rename `restrict-filenames` to `path-restrict`
- Adjust `pixiv` metadata and default filename format ([#366](https://github.com/mikf/gallery-dl/issues/366))
  - Set `filename` to `"{category}_{user[id]}_{id}{suffix}.{extension}"` to restore the old default
- Improve and optimize directory and filename generation
### Fixes
- Allow the `classify` post-processor to handle files with unknown filename extension ([#138](https://github.com/mikf/gallery-dl/issues/138))
- Fix rate limit handling for OAuth APIs ([#368](https://github.com/mikf/gallery-dl/issues/368))
- Fix artwork and scraps extraction on `deviantart` ([#376](https://github.com/mikf/gallery-dl/issues/376), [#392](https://github.com/mikf/gallery-dl/issues/392))
- Distinguish between `imgur` album and gallery URLs ([#380](https://github.com/mikf/gallery-dl/issues/380))
- Prevent crash when using `--ugoira-conv` ([#382](https://github.com/mikf/gallery-dl/issues/382))
- Handle multi-image posts on `patreon` ([#383](https://github.com/mikf/gallery-dl/issues/383))
- Miscellaneous fixes for `*reactor`, `simplyhentai`

## 1.10.1 - 2019-08-02
### Fixes
- Use the correct domain for exhentai.org input URLs

## 1.10.0 - 2019-08-01
### Warning
- Prior to version 1.10.0 all cache files were created world readable (mode `644`)
  leading to possible sensitive information disclosure on multi-user systems
- It is recommended to restrict access permissions of already existing files
  (`/tmp/.gallery-dl.cache`) with `chmod 600`
- Windows users should not be affected
### Additions
- Support for
  - `vsco`        - https://vsco.co/             ([#331](https://github.com/mikf/gallery-dl/issues/331))
  - `imgbb`       - https://imgbb.com/           ([#361](https://github.com/mikf/gallery-dl/issues/361))
  - `adultempire` - https://www.adultempire.com/ ([#340](https://github.com/mikf/gallery-dl/issues/340))
- `restrict-filenames` option to create Windows-compatible filenames on any platform ([#348](https://github.com/mikf/gallery-dl/issues/348))
- `forward-cookies` option to control cookie forwarding to youtube-dl ([#352](https://github.com/mikf/gallery-dl/issues/352))
### Changes
- The default cache file location on non-Windows systems is now
  - `$XDG_CACHE_HOME/gallery-dl/cache.sqlite3` or
  - `~/.cache/gallery-dl/cache.sqlite3`
- New cache files are created with mode `600`
- `exhentai` extractors will always use `e-hentai.org` as domain
### Fixes
- Better handling of `exhentai` image limits and errors ([#356](https://github.com/mikf/gallery-dl/issues/356), [#360](https://github.com/mikf/gallery-dl/issues/360))
- Try to prevent ZIP file corruption ([#355](https://github.com/mikf/gallery-dl/issues/355))
- Miscellaneous fixes for `behance`, `ngomik`

## 1.9.0 - 2019-07-19
### Additions
- Support for
  - `erolord` - http://erolord.com/ ([#326](https://github.com/mikf/gallery-dl/issues/326))
- Add login support for `instagram` ([#195](https://github.com/mikf/gallery-dl/issues/195))
- Add `--no-download` and `extractor.*.download` disable file downloads ([#220](https://github.com/mikf/gallery-dl/issues/220))
- Add `-A/--abort` to specify the number of consecutive download skips before aborting
- Interpret `-1` as infinite retries ([#300](https://github.com/mikf/gallery-dl/issues/300))
- Implement custom log message formats per log-level ([#304](https://github.com/mikf/gallery-dl/issues/304))
- Implement an `mtime` post-processor that sets file modification times according to metadata fields ([#332](https://github.com/mikf/gallery-dl/issues/332))
- Implement a `twitter.content` option to enable tweet text extraction ([#333](https://github.com/mikf/gallery-dl/issues/333), [#338](https://github.com/mikf/gallery-dl/issues/338))
- Enable `date-min/-max/-format` options for `tumblr` ([#337](https://github.com/mikf/gallery-dl/issues/337))
### Changes
- Set file modification times according to their `Last-Modified` header when downloading ([#236](https://github.com/mikf/gallery-dl/issues/236), [#277](https://github.com/mikf/gallery-dl/issues/277))
  - Use `--no-mtime` or `downloader.*.mtime` to disable this behavior
- Duplicate download URLs are no longer silently ignored (controllable with `extractor.*.image-unique`)
- Deprecate `--abort-on-skip`
### Fixes
- Retry downloads on OpenSSL exceptions ([#324](https://github.com/mikf/gallery-dl/issues/324))
- Ignore unavailable pins on `sexcom` instead of raising an exception ([#325](https://github.com/mikf/gallery-dl/issues/325))
- Use Firefox's SSL/TLS ciphers to prevent Cloudflare CAPTCHAs ([#342](https://github.com/mikf/gallery-dl/issues/342))
- Improve folder name matching on `deviantart` ([#343](https://github.com/mikf/gallery-dl/issues/343))
- Forward cookies to `youtube-dl` to allow downloading private videos
- Miscellaneous fixes for `35photo`, `500px`, `newgrounds`, `simplyhentai`

## 1.8.7 - 2019-06-28
### Additions
- Support for
  - `vanillarock` - https://vanilla-rock.com/ ([#254](https://github.com/mikf/gallery-dl/issues/254))
  - `nsfwalbum`   - https://nsfwalbum.com/    ([#287](https://github.com/mikf/gallery-dl/issues/287))
- `artist` and `tags` metadata for `hentaicafe` ([#238](https://github.com/mikf/gallery-dl/issues/238))
- `description` metadata for `instagram` ([#310](https://github.com/mikf/gallery-dl/issues/310))
- Format string option to replace a substring with another - `R<old>/<new>/` ([#318](https://github.com/mikf/gallery-dl/issues/318))
### Changes
- Delete empty archives created by the `zip` post-processor ([#316](https://github.com/mikf/gallery-dl/issues/316))
### Fixes
- Handle `hitomi` Game CG galleries correctly ([#321](https://github.com/mikf/gallery-dl/issues/321))
- Miscellaneous fixes for `deviantart`, `hitomi`, `pururin`, `kissmanga`, `keenspot`, `mangoxo`, `imagefap`

## 1.8.6 - 2019-06-14
### Additions
- Support for
  - `slickpic` - https://www.slickpic.com/ ([#249](https://github.com/mikf/gallery-dl/issues/249))
  - `xhamster` - https://xhamster.com/     ([#281](https://github.com/mikf/gallery-dl/issues/281))
  - `pornhub`  - https://www.pornhub.com/  ([#282](https://github.com/mikf/gallery-dl/issues/282))
  - `8muses`   - https://www.8muses.com/   ([#305](https://github.com/mikf/gallery-dl/issues/305))
- `extra` option for `deviantart` to download Sta.sh content linked in description texts ([#302](https://github.com/mikf/gallery-dl/issues/302))
### Changes
- Detect `directlink` URLs with upper case filename extensions ([#296](https://github.com/mikf/gallery-dl/issues/296))
### Fixes
- Improved error handling for `tumblr` API calls ([#297](https://github.com/mikf/gallery-dl/issues/297))
- Fixed extraction of `livedoor` blogs ([#301](https://github.com/mikf/gallery-dl/issues/301))
- Fixed extraction of special `deviantart` Sta.sh items ([#307](https://github.com/mikf/gallery-dl/issues/307))
- Fixed pagination for specific `keenspot` comics

## 1.8.5 - 2019-06-01
### Additions
- Support for
  - `keenspot`       - http://keenspot.com/           ([#223](https://github.com/mikf/gallery-dl/issues/223))
  - `sankakucomplex` - https://www.sankakucomplex.com ([#258](https://github.com/mikf/gallery-dl/issues/258))
- `folders` option for `deviantart` to add a list of containing folders to each file ([#276](https://github.com/mikf/gallery-dl/issues/276))
- `captcha` option for `kissmanga` and `readcomiconline` to control CAPTCHA handling ([#279](https://github.com/mikf/gallery-dl/issues/279))
- `filename` metadata for files downloaded with youtube-dl ([#291](https://github.com/mikf/gallery-dl/issues/291))
### Changes
- Adjust `wallhaven` extractors to new page layout:
  - use API and add `api-key` option
  - removed traditional login support
- Provide original filenames for `patreon` downloads ([#268](https://github.com/mikf/gallery-dl/issues/268))
- Use e-hentai.org or exhentai.org depending on input URL ([#278](https://github.com/mikf/gallery-dl/issues/278))
### Fixes
- Fix pagination over `sankaku` popular listings ([#265](https://github.com/mikf/gallery-dl/issues/265))
- Fix folder and collection extraction on `deviantart` ([#271](https://github.com/mikf/gallery-dl/issues/271))
- Detect "AreYouHuman" redirects on `readcomiconline` ([#279](https://github.com/mikf/gallery-dl/issues/279))
- Miscellaneous fixes for `hentainexus`, `livedoor`, `ngomik`

## 1.8.4 - 2019-05-17
### Additions
- Support for
  - `patreon`     - https://www.patreon.com/ ([#226](https://github.com/mikf/gallery-dl/issues/226))
  - `hentainexus` - https://hentainexus.com/ ([#256](https://github.com/mikf/gallery-dl/issues/256))
- `date` metadata fields for `pixiv` ([#248](https://github.com/mikf/gallery-dl/issues/248)), `instagram` ([#250](https://github.com/mikf/gallery-dl/issues/250)), `exhentai`, and `newgrounds`
### Changes
- Improved `flickr` metadata and video extraction ([#246](https://github.com/mikf/gallery-dl/issues/246))
### Fixes
- Download original GIF animations from `deviantart` ([#242](https://github.com/mikf/gallery-dl/issues/242))
- Ignore missing `edge_media_to_comment` fields on `instagram` ([#250](https://github.com/mikf/gallery-dl/issues/250))
- Fix serialization of `datetime` objects for `--write-metadata` ([#251](https://github.com/mikf/gallery-dl/issues/251), [#252](https://github.com/mikf/gallery-dl/issues/252))
- Allow multiple post-processor command-line options at once ([#253](https://github.com/mikf/gallery-dl/issues/253))
- Prevent crash on `booru` sites when no tags are available ([#259](https://github.com/mikf/gallery-dl/issues/259))
- Fix extraction on `instagram` after `rhx_gis` field removal ([#266](https://github.com/mikf/gallery-dl/issues/266))
- Avoid Cloudflare CAPTCHAs for Python interpreters built against OpenSSL < 1.1.1
- Miscellaneous fixes for `luscious`

## 1.8.3 - 2019-05-04
### Additions
- Support for
  - `plurk`  - https://www.plurk.com/ ([#212](https://github.com/mikf/gallery-dl/issues/212))
  - `sexcom` - https://www.sex.com/   ([#147](https://github.com/mikf/gallery-dl/issues/147))
- `--clear-cache`
- `date` metadata fields for `deviantart`, `twitter`, and `tumblr` ([#224](https://github.com/mikf/gallery-dl/issues/224), [#232](https://github.com/mikf/gallery-dl/issues/232))
### Changes
- Standalone executables are now built using PyInstaller:
  - uses the latest CPython interpreter (Python 3.7.3)
  - available on several platforms (Windows, Linux, macOS)
  - includes the `certifi` CA bundle, `youtube-dl`, and `pyOpenSSL` on Windows
### Fixes
- Patch `urllib3`'s  default list of SSL/TLS ciphers to prevent Cloudflare CAPTCHAs ([#227](https://github.com/mikf/gallery-dl/issues/227))
  (Windows users need to install `pyOpenSSL` for this to take effect)
- Provide fallback URLs for `twitter` images ([#237](https://github.com/mikf/gallery-dl/issues/237))
- Send `Referer` headers when downloading from `hitomi` ([#239](https://github.com/mikf/gallery-dl/issues/239))
- Updated login procedure on `mangoxo`

## 1.8.2 - 2019-04-12
### Additions
- Support for
  - `pixnet`   - https://www.pixnet.net/  ([#177](https://github.com/mikf/gallery-dl/issues/177))
  - `wikiart`  - https://www.wikiart.org/ ([#179](https://github.com/mikf/gallery-dl/issues/179))
  - `mangoxo`  - https://www.mangoxo.com/ ([#184](https://github.com/mikf/gallery-dl/issues/184))
  - `yaplog`   - https://yaplog.jp/       ([#190](https://github.com/mikf/gallery-dl/issues/190))
  - `livedoor` - http://blog.livedoor.jp/ ([#190](https://github.com/mikf/gallery-dl/issues/190))
- Login support for `mangoxo` ([#184](https://github.com/mikf/gallery-dl/issues/184)) and `twitter` ([#214](https://github.com/mikf/gallery-dl/issues/214))
### Changes
- Increased required `Requests` version to 2.11.0
### Fixes
- Improved image quality on `reactor` sites ([#210](https://github.com/mikf/gallery-dl/issues/210))
- Support `imagebam` galleries with more than 100 images ([#219](https://github.com/mikf/gallery-dl/issues/219))
- Updated Cloudflare bypass code

## 1.8.1 - 2019-03-29
### Additions
- Support for:
  - `35photo` - https://35photo.pro/ ([#162](https://github.com/mikf/gallery-dl/issues/162))
  - `500px`   - https://500px.com/   ([#185](https://github.com/mikf/gallery-dl/issues/185))
- `instagram` extractor for hashtags ([#202](https://github.com/mikf/gallery-dl/issues/202))
- Option to get more metadata on `deviantart` ([#189](https://github.com/mikf/gallery-dl/issues/189))
- Man pages and bash completion ([#150](https://github.com/mikf/gallery-dl/issues/150))
- Snap improvements ([#197](https://github.com/mikf/gallery-dl/issues/197), [#199](https://github.com/mikf/gallery-dl/issues/199), [#207](https://github.com/mikf/gallery-dl/issues/207))
### Changes
- Better FFmpeg arguments for `--ugoira-conv`
- Adjusted metadata for `luscious` albums
### Fixes
- Proper handling of `instagram` multi-image posts ([#178](https://github.com/mikf/gallery-dl/issues/178), [#201](https://github.com/mikf/gallery-dl/issues/201))
- Fixed `tumblr` avatar URLs when not using OAuth1.0 ([#193](https://github.com/mikf/gallery-dl/issues/193))
- Miscellaneous fixes for `exhentai`, `komikcast`

## 1.8.0 - 2019-03-15
### Additions
- Support for:
  - `weibo`       - https://www.weibo.com/
  - `pururin`     - https://pururin.io/          ([#174](https://github.com/mikf/gallery-dl/issues/174))
  - `fashionnova` - https://www.fashionnova.com/ ([#175](https://github.com/mikf/gallery-dl/issues/175))
  - `shopify` sites in general ([#175](https://github.com/mikf/gallery-dl/issues/175))
- Snap packaging ([#169](https://github.com/mikf/gallery-dl/issues/169), [#170](https://github.com/mikf/gallery-dl/issues/170), [#187](https://github.com/mikf/gallery-dl/issues/187), [#188](https://github.com/mikf/gallery-dl/issues/188))
- Automatic Cloudflare DDoS protection bypass
- Extractor and Job information for logging format strings
- `dynastyscans` image and search extractors ([#163](https://github.com/mikf/gallery-dl/issues/163))
- `deviantart` scraps extractor ([#168](https://github.com/mikf/gallery-dl/issues/168))
- `artstation` extractor for artwork listings ([#172](https://github.com/mikf/gallery-dl/issues/172))
- `smugmug` video support and improved image format selection ([#183](https://github.com/mikf/gallery-dl/issues/183))
### Changes
- More metadata for `nhentai` galleries
- Combined `myportfolio` extractors into one
- Renamed `name` metadata field to `filename` and removed the original `filename` field
- Simplified and improved internal data structures
- Optimized creation of child extractors
### Fixes
- Filter empty `tumblr` URLs ([#165](https://github.com/mikf/gallery-dl/issues/165))
- Filter ads and improve connection speed on `hentaifoundry`
- Show proper error messages if `luscious` galleries are unavailable
- Miscellaneous fixes for `mangahere`, `ngomik`, `simplyhentai`, `imgspice`
### Removals
- `seaotterscans`

## 1.7.0 - 2019-02-05
- Added support for:
  - `photobucket` - http://photobucket.com/ ([#117](https://github.com/mikf/gallery-dl/issues/117))
  - `hentaifox` - https://hentaifox.com/ ([#160](https://github.com/mikf/gallery-dl/issues/160))
  - `tsumino` - https://www.tsumino.com/ ([#161](https://github.com/mikf/gallery-dl/issues/161))
- Added the ability to dynamically generate extractors based on a user's config file for
  - [`mastodon`](https://github.com/tootsuite/mastodon) instances ([#144](https://github.com/mikf/gallery-dl/issues/144))
  - [`foolslide`](https://github.com/FoolCode/FoOlSlide) based sites
  - [`foolfuuka`](https://github.com/FoolCode/FoolFuuka) based archives
- Added an extractor for `behance` collections ([#157](https://github.com/mikf/gallery-dl/issues/157))
- Added login support for `luscious` ([#159](https://github.com/mikf/gallery-dl/issues/159)) and `tsumino` ([#161](https://github.com/mikf/gallery-dl/issues/161))
- Added an option to stop downloading if the `exhentai` image limit is exceeded ([#141](https://github.com/mikf/gallery-dl/issues/141))
- Fixed extraction issues for `behance` and `mangapark`

## 1.6.3 - 2019-01-18
- Added `metadata` post-processor to write image metadata to an external file ([#135](https://github.com/mikf/gallery-dl/issues/135))
- Added option to reverse chapter order of manga extractors ([#149](https://github.com/mikf/gallery-dl/issues/149))
- Added authentication support for `danbooru` ([#151](https://github.com/mikf/gallery-dl/issues/151))
- Added tag metadata for `exhentai` and `hbrowse` galleries
- Improved `*reactor` extractors ([#148](https://github.com/mikf/gallery-dl/issues/148))
- Fixed extraction issues for `nhentai` ([#156](https://github.com/mikf/gallery-dl/issues/156)), `pinterest`, `mangapark`

## 1.6.2 - 2019-01-01
- Added support for:
  - `instagram` - https://www.instagram.com/ ([#134](https://github.com/mikf/gallery-dl/issues/134))
- Added support for multiple items on sta.sh pages ([#113](https://github.com/mikf/gallery-dl/issues/113))
- Added option to download `tumblr` avatars ([#137](https://github.com/mikf/gallery-dl/issues/137))
- Changed defaults for visited post types and inline media on `tumblr`
- Improved inline extraction of `tumblr` posts ([#133](https://github.com/mikf/gallery-dl/issues/133), [#137](https://github.com/mikf/gallery-dl/issues/137))
- Improved error handling and retry behavior of all API calls
- Improved handling of missing fields in format strings ([#136](https://github.com/mikf/gallery-dl/issues/136))
- Fixed hash extraction for unusual `tumblr` URLs ([#129](https://github.com/mikf/gallery-dl/issues/129))
- Fixed image subdomains for `hitomi` galleries ([#142](https://github.com/mikf/gallery-dl/issues/142))
- Fixed and improved miscellaneous issues for `kissmanga` ([#20](https://github.com/mikf/gallery-dl/issues/20)), `luscious`, `mangapark`, `readcomiconline`

## 1.6.1 - 2018-11-28
- Added support for:
  - `joyreactor` - http://joyreactor.cc/ ([#114](https://github.com/mikf/gallery-dl/issues/114))
  - `pornreactor` - http://pornreactor.cc/ ([#114](https://github.com/mikf/gallery-dl/issues/114))
  - `newgrounds` - https://www.newgrounds.com/ ([#119](https://github.com/mikf/gallery-dl/issues/119))
- Added extractor for search results on `luscious` ([#127](https://github.com/mikf/gallery-dl/issues/127))
- Fixed filenames of ZIP archives ([#126](https://github.com/mikf/gallery-dl/issues/126))
- Fixed extraction issues for `gfycat`, `hentaifoundry` ([#125](https://github.com/mikf/gallery-dl/issues/125)), `mangafox`

## 1.6.0 - 2018-11-17
- Added support for:
  - `wallhaven` - https://alpha.wallhaven.cc/
  - `yuki` - https://yuki.la/
- Added youtube-dl integration and video downloads for `twitter` ([#99](https://github.com/mikf/gallery-dl/issues/99)), `behance`, `artstation`
- Added per-extractor options for network connections (`retries`, `timeout`, `verify`)
- Added a `--no-check-certificate` command-line option
- Added ability to specify the number of skipped downloads before aborting/exiting ([#115](https://github.com/mikf/gallery-dl/issues/115))
- Added extractors for scraps, favorites, popular and recent images on `hentaifoundry` ([#110](https://github.com/mikf/gallery-dl/issues/110))
- Improved login procedure for `pixiv`  to avoid unwanted emails on each new login
- Improved album metadata and error handling for `flickr` ([#109](https://github.com/mikf/gallery-dl/issues/109))
- Updated default User-Agent string to Firefox 62 ([#122](https://github.com/mikf/gallery-dl/issues/122))
- Fixed `twitter` API response handling when logged in ([#123](https://github.com/mikf/gallery-dl/issues/123))
- Fixed issue when converting Ugoira using H.264
- Fixed miscellaneous issues for `2chan`, `deviantart`, `fallenangels`, `flickr`, `imagefap`, `pinterest`, `turboimagehost`, `warosu`, `yuki` ([#112](https://github.com/mikf/gallery-dl/issues/112))

## 1.5.3 - 2018-09-14
- Added support for:
  - `hentaicafe` - https://hentai.cafe/ ([#101](https://github.com/mikf/gallery-dl/issues/101))
  - `bobx` - http://www.bobx.com/dark/
- Added black-/whitelist options for post-processor modules
- Added support for `tumblr` inline videos ([#102](https://github.com/mikf/gallery-dl/issues/102))
- Fixed extraction of `smugmug` albums without owner ([#100](https://github.com/mikf/gallery-dl/issues/100))
- Fixed issues when using default config values with `reddit` extractors ([#104](https://github.com/mikf/gallery-dl/issues/104))
- Fixed pagination for user favorites on `sankaku` ([#106](https://github.com/mikf/gallery-dl/issues/106))
- Fixed a crash when processing `deviantart` journals ([#108](https://github.com/mikf/gallery-dl/issues/108))

## 1.5.2 - 2018-08-31
- Added support for `twitter` timelines ([#96](https://github.com/mikf/gallery-dl/issues/96))
- Added option to suppress FFmpeg output during ugoira conversions
- Improved filename formatter performance
- Improved inline image quality on `tumblr` ([#98](https://github.com/mikf/gallery-dl/issues/98))
- Fixed image URLs for newly released `mangadex` chapters
- Fixed a smaller issue with `deviantart` journals
- Replaced `subapics` with `ngomik`

## 1.5.1 - 2018-08-17
- Added support for:
  - `piczel` - https://piczel.tv/
- Added support for related pins on `pinterest`
- Fixed accessing "offensive" galleries on `exhentai` ([#97](https://github.com/mikf/gallery-dl/issues/97))
- Fixed extraction issues for `mangadex`, `komikcast` and `behance`
- Removed original-image functionality from `tumblr`, since "raw" images are no longer accessible

## 1.5.0 - 2018-08-03
- Added support for:
  - `behance` - https://www.behance.net/
  - `myportfolio` - https://www.myportfolio.com/ ([#95](https://github.com/mikf/gallery-dl/issues/95))
- Added custom format string options to handle long strings ([#92](https://github.com/mikf/gallery-dl/issues/92), [#94](https://github.com/mikf/gallery-dl/issues/94))
  - Slicing: `"{field[10:40]}"`
  - Replacement: `"{field:L40/too long/}"`
- Improved frame rate handling for ugoira conversions
- Improved private access token usage on `deviantart`
- Fixed metadata extraction for some images on `nijie`
- Fixed chapter extraction on `mangahere`
- Removed `whatisthisimnotgoodwithcomputers`
- Removed support for Python 3.3

## 1.4.2 - 2018-07-06
- Added image-pool extractors for `safebooru` and `rule34`
- Added option for extended tag information on `booru` sites ([#92](https://github.com/mikf/gallery-dl/issues/92))
- Added support for DeviantArt's new URL format
- Added support for `mangapark` mirrors
- Changed `imagefap` extractors to use HTTPS
- Fixed crash when skipping downloads for files without known extension

## 1.4.1 - 2018-06-22
- Added an `ugoira` post-processor to convert  `pixiv` animations to WebM
- Added `--zip` and `--ugoira-conv` command-line options
- Changed how ugoira frame information is handled
  - instead of being written to a separate file, it is now made available as metadata field of the ZIP archive
- Fixed manga and chapter titles for `mangadex`
- Fixed file deletion by post-processors

## 1.4.0 - 2018-06-08
- Added support for:
  - `simplyhentai` - https://www.simply-hentai.com/ ([#89](https://github.com/mikf/gallery-dl/issues/89))
- Added extractors for
  - `pixiv` search results and followed users
  - `deviantart` search results and popular listings
- Added post-processors to perform actions on downloaded files
- Added options to configure logging behavior
- Added OAuth support for `smugmug`
- Changed `pixiv` extractors to use the AppAPI
  - this breaks `favorite` archive IDs and changes some metadata fields
- Changed the default filename format for `tumblr` and renamed `offset` to `num`
- Fixed a possible UnicodeDecodeError during installation ([#86](https://github.com/mikf/gallery-dl/issues/86))
- Fixed extraction of `mangadex` manga with more than 100 chapters ([#84](https://github.com/mikf/gallery-dl/issues/84))
- Fixed miscellaneous issues for `imgur`, `reddit`, `komikcast`, `mangafox` and `imagebam`

## 1.3.5 - 2018-05-04
- Added support for:
  - `smugmug` - https://www.smugmug.com/
- Added title information for `mangadex` chapters
- Improved the `pinterest` API implementation ([#83](https://github.com/mikf/gallery-dl/issues/83))
- Improved error handling for `deviantart` and `tumblr`
- Removed `gomanga` and `puremashiro`

## 1.3.4 - 2018-04-20
- Added support for custom OAuth2 credentials for `pinterest`
- Improved rate limit handling for `tumblr` extractors
- Improved `hentaifoundry` extractors
- Improved `imgur` URL patterns
- Fixed miscellaneous extraction issues for `luscious` and `komikcast`
- Removed `loveisover` and `spectrumnexus`

## 1.3.3 - 2018-04-06
- Added extractors for
  - `nhentai` search results
  - `exhentai` search results and favorites
  - `nijie` doujins and favorites
- Improved metadata extraction for `exhentai` and `nijie`
- Improved `tumblr` extractors by avoiding unnecessary API calls
- Fixed Cloudflare DDoS protection bypass
- Fixed errors when trying to print unencodable characters

## 1.3.2 - 2018-03-23
- Added extractors for `artstation` albums, challenges and search results
- Improved URL and metadata extraction for `hitomi`and `nhentai`
- Fixed page transitions for `danbooru` API results ([#82](https://github.com/mikf/gallery-dl/issues/82))

## 1.3.1 - 2018-03-16
- Added support for:
  - `mangadex` - https://mangadex.org/
  - `artstation` - https://www.artstation.com/
- Added Cloudflare DDoS protection bypass to `komikcast` extractors
- Changed archive ID formats for `deviantart` folders and collections
- Improved error handling for `deviantart` API calls
- Removed `imgchili` and various smaller image hosts

## 1.3.0 - 2018-03-02
- Added `--proxy` to explicitly specify a proxy server ([#76](https://github.com/mikf/gallery-dl/issues/76))
- Added options to customize [archive ID formats](https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst#extractorarchive-format) and [undefined replacement fields](https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst#extractorkeywords-default)
- Changed various archive ID formats to improve their behavior for favorites / bookmarks / etc.
  - Affected modules are `deviantart`, `flickr`, `tumblr`, `pixiv` and all …boorus
- Improved `sankaku` and `idolcomplex` support by
  - respecting `page` and `next` URL parameters ([#79](https://github.com/mikf/gallery-dl/issues/79))
  - bypassing the page-limit for unauthenticated users
- Improved `directlink` metadata by properly unquoting it
- Fixed `pixiv` ugoira extraction ([#78](https://github.com/mikf/gallery-dl/issues/78))
- Fixed miscellaneous extraction issues for `mangastream` and `tumblr`
- Removed `yeet`, `chronos`, `coreimg`, `hosturimage`, `imageontime`, `img4ever`, `imgmaid`, `imgupload`

## 1.2.0 - 2018-02-16
- Added support for:
  - `paheal` - https://rule34.paheal.net/ ([#69](https://github.com/mikf/gallery-dl/issues/69))
  - `komikcast` - https://komikcast.com/ ([#70](https://github.com/mikf/gallery-dl/issues/70))
  - `subapics` - http://subapics.com/ ([#70](https://github.com/mikf/gallery-dl/issues/70))
- Added `--download-archive` to record downloaded files in an archive file
- Added `--write-log` to write logging output to a file
- Added a filetype check on download completion to fix incorrectly assigned filename extensions ([#63](https://github.com/mikf/gallery-dl/issues/63))
- Added the `tumblr:...` pseudo URI scheme to support custom domains for Tumblr blogs ([#71](https://github.com/mikf/gallery-dl/issues/71))
- Added fallback URLs for `tumblr` images ([#64](https://github.com/mikf/gallery-dl/issues/64))
- Added support for `reddit`-hosted images ([#68](https://github.com/mikf/gallery-dl/issues/68))
- Improved the input file format by allowing comments and per-URL options
- Fixed OAuth 1.0 signature generation for Python 3.3 and 3.4 ([#75](https://github.com/mikf/gallery-dl/issues/75))
- Fixed smaller issues for `luscious`, `hentai2read`, `hentaihere` and `imgur`
- Removed the `batoto` module

## 1.1.2 - 2018-01-12
- Added support for:
  - `puremashiro` - http://reader.puremashiro.moe/ ([#66](https://github.com/mikf/gallery-dl/issues/66))
  - `idolcomplex` - https://idol.sankakucomplex.com/
- Added an option to filter reblogs on `tumblr` ([#61](https://github.com/mikf/gallery-dl/issues/61))
- Added OAuth user authentication for `tumblr` ([#65](https://github.com/mikf/gallery-dl/issues/65))
- Added support for `slideshare` mobile URLs ([#67](https://github.com/mikf/gallery-dl/issues/67))
- Improved pagination for various …booru sites to work around page limits
- Fixed chapter information parsing for certain manga on `kissmanga` ([#58](https://github.com/mikf/gallery-dl/issues/58)) and `batoto` ([#60](https://github.com/mikf/gallery-dl/issues/60))

## 1.1.1 - 2017-12-22
- Added support for:
  - `slideshare` - https://www.slideshare.net/ ([#54](https://github.com/mikf/gallery-dl/issues/54))
- Added pool- and post-extractors for `sankaku`
- Added OAuth user authentication for `deviantart`
- Updated `luscious` to support `members.luscious.net` URLs ([#55](https://github.com/mikf/gallery-dl/issues/55))
- Updated `mangahere` to use their new domain name (mangahere.cc) and support mobile URLs
- Updated `gelbooru` to not be restricted to the first 20,000 images ([#56](https://github.com/mikf/gallery-dl/issues/56))
- Fixed extraction issues for `nhentai` and `khinsider`

## 1.1.0 - 2017-12-08
- Added the ``-r/--limit-rate`` command-line option to set a maximum download rate
- Added the ``--sleep`` command-line option to specify the number of seconds to sleep before each download
- Updated `gelbooru` to no longer use their now disabled API
- Fixed SWF extraction for `sankaku` ([#52](https://github.com/mikf/gallery-dl/issues/52))
- Fixed extraction issues for `hentai2read` and `khinsider`
- Removed the deprecated `--images` and `--chapters` options
- Removed the ``mangazuki`` module

## 1.0.2 - 2017-11-24
- Added an option to set a [custom user-agent string](https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst#extractoruser-agent)
- Improved retry behavior for failed HTTP requests
- Improved `seiga` by providing better metadata and getting more than the latest 200 images
- Improved `tumblr` by adding support for [all post types](https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst#extractortumblrposts), scanning for [inline images](https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst#extractortumblrinline) and following [external links](https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst#extractortumblrexternal) ([#48](https://github.com/mikf/gallery-dl/issues/48))
- Fixed extraction issues for `hbrowse`, `khinsider` and `senmanga`

## 1.0.1 - 2017-11-10
- Added support for:
  - `xvideos` - https://www.xvideos.com/ ([#45](https://github.com/mikf/gallery-dl/issues/45))
- Fixed exception handling during file downloads which could lead to a premature exit
- Fixed an issue with `tumblr` where not all images would be downloaded when using tags ([#48](https://github.com/mikf/gallery-dl/issues/48))
- Fixed extraction issues for `imgbox` ([#47](https://github.com/mikf/gallery-dl/issues/47)), `mangastream` ([#49](https://github.com/mikf/gallery-dl/issues/49)) and `mangahere`

## 1.0.0 - 2017-10-27
- Added support for:
  - `warosu` - https://warosu.org/
  - `b4k` - https://arch.b4k.co/
- Added support for `pixiv` ranking lists
- Added support for `booru` popular lists (`danbooru`, `e621`, `konachan`, `yandere`, `3dbooru`)
- Added the `--cookies` command-line and [`cookies`](https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst#extractorcookies) config option to load additional cookies
- Added the `--filter` and `--chapter-filter` command-line options to select individual images or manga-chapters by their metadata using simple Python expressions ([#43](https://github.com/mikf/gallery-dl/issues/43))
- Added the [`verify`](https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst#downloaderhttpverify) config option to control certificate verification during file downloads
- Added config options to overwrite internally used API credentials ([API Tokens & IDs](https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst#api-tokens-ids))
- Added `-K` as a shortcut for `--list-keywords`
- Changed the `--images` and `--chapters` command-line options to `--range` and `--chapter-range`
- Changed keyword names for various modules to make them accessible by `--filter`. In general minus signs have been replaced with underscores (e.g. `gallery-id`  -> `gallery_id`).
- Changed default filename formats for manga extractors to optionally use volume and title information
- Improved the downloader modules to use [`.part` files](https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst#downloaderpart) and support resuming incomplete downloads ([#29](https://github.com/mikf/gallery-dl/issues/29))
- Improved `deviantart` by distinguishing between users and groups ([#26](https://github.com/mikf/gallery-dl/issues/26)), always using HTTPS, and always downloading full-sized original images
- Improved `sankaku` by adding authentication support and fixing various other issues ([#44](https://github.com/mikf/gallery-dl/issues/44))
- Improved URL pattern for direct image links ([#30](https://github.com/mikf/gallery-dl/issues/30))
- Fixed an issue with `luscious` not getting original image URLs ([#33](https://github.com/mikf/gallery-dl/issues/33))
- Fixed various smaller issues for `batoto`, `hentai2read` ([#38](https://github.com/mikf/gallery-dl/issues/38)), `jaiminisbox`, `khinsider`, `kissmanga` ([#28](https://github.com/mikf/gallery-dl/issues/28), [#46](https://github.com/mikf/gallery-dl/issues/46)), `mangahere`, `pawoo`, `twitter`
- Removed `kisscomic` and `yonkouprod` modules

## 0.9.1 - 2017-07-24
- Added support for:
  - `2chan` - https://www.2chan.net/
  - `4plebs` - https://archive.4plebs.org/
  - `archivedmoe` - https://archived.moe/
  - `archiveofsins` - https://archiveofsins.com/
  - `desuarchive` - https://desuarchive.org/
  - `fireden` - https://boards.fireden.net/
  - `loveisover` - https://archive.loveisover.me/
  - `nyafuu` - https://archive.nyafuu.org/
  - `rbt` - https://rbt.asia/
  - `thebarchive` - https://thebarchive.com/
  - `mangazuki` - https://mangazuki.co/
- Improved `reddit` to allow submission filtering by ID and human-readable dates
- Improved `deviantart` to support group galleries and gallery folders ([#26](https://github.com/mikf/gallery-dl/issues/26))
- Changed `deviantart` to use better default path formats
- Fixed extraction of larger `imgur` albums
- Fixed some smaller issues for `pixiv`, `batoto` and `fallenangels`

## 0.9.0 - 2017-06-28
- Added support for:
  - `reddit` - https://www.reddit.com/ ([#15](https://github.com/mikf/gallery-dl/issues/15))
  - `flickr` - https://www.flickr.com/ ([#16](https://github.com/mikf/gallery-dl/issues/16))
  - `gfycat` - https://gfycat.com/
- Added support for direct image links
- Added user authentication via [OAuth](https://github.com/mikf/gallery-dl#52oauth) for `reddit` and `flickr`
- Added support for user authentication data from [`.netrc`](https://stackoverflow.com/tags/.netrc/info) files ([#22](https://github.com/mikf/gallery-dl/issues/22))
- Added a simple progress indicator for multiple URLs ([#19](https://github.com/mikf/gallery-dl/issues/19))
- Added the `--write-unsupported` command-line option to write unsupported URLs to a file
- Added documentation for all available config options ([configuration.rst](https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst))
- Improved `pixiv` to support tags for user downloads ([#17](https://github.com/mikf/gallery-dl/issues/17))
- Improved `pixiv` to support shortened and http://pixiv.me/... URLs ([#23](https://github.com/mikf/gallery-dl/issues/23))
- Improved `imgur` to properly handle `.gifv` images and provide better metadata
- Fixed an issue with `kissmanga` where metadata parsing for some series failed ([#20](https://github.com/mikf/gallery-dl/issues/20))
- Fixed an issue with getting filename extensions from `Content-Type` response headers

## 0.8.4 - 2017-05-21
- Added the `--abort-on-skip` option to stop extraction if a download would be skipped
- Improved the output format of the `--list-keywords` option
- Updated `deviantart` to support all media types and journals
- Updated `fallenangels` to support their [Vietnamese version](https://truyen.fascans.com/)
- Fixed an issue with multiple tags on ...booru sites
- Removed the `yomanga` module

## 0.8.3 - 2017-05-01
- Added support for https://pawoo.net/
- Added manga extractors for all [FoOlSlide](https://foolcode.github.io/FoOlSlide/)-based modules
- Added the `-q/--quiet` and `-v/--verbose` options to control output verbosity
- Added the `-j/--dump-json` option to dump extractor results in JSON format
- Added the `--ignore-config` option
- Updated the `exhentai` extractor to fall back to using the e-hentai version if no username is given
- Updated `deviantart` to support sta.sh URLs
- Fixed an issue with `kissmanga` which prevented image URLs from being decrypted properly (again)
- Fixed an issue with `pixhost` where for an image inside an album it would always download the first image of that album ([#13](https://github.com/mikf/gallery-dl/issues/13))
- Removed the `mangashare` and `readcomics` modules

## 0.8.2 - 2017-04-10
- Fixed an issue in `kissmanga` which prevented image URLs from being decrypted properly

## 0.8.1 - 2017-04-09
- Added new extractors:
  - `kireicake` - https://reader.kireicake.com/
  - `seaotterscans` - https://reader.seaotterscans.com/
- Added a favourites extractor for `deviantart`
- Re-enabled the `kissmanga` module
- Updated `nijie` to support multi-page image listings
- Updated `mangastream` to support readms.net URLs
- Updated `exhentai` to support e-hentai.org URLs
- Updated `fallenangels` to support their new domain and site layout

## 0.8.0 - 2017-03-28
- Added logging support
- Added the `-R/--retries` option to specify how often a download should be retried before giving up
- Added the `--http-timeout` option to set a timeout for HTTP connections
- Improved error handling/tolerance during HTTP file downloads ([#10](https://github.com/mikf/gallery-dl/issues/10))
- Improved option parsing and the help message from `-h/--help`
- Changed the way configuration values are used by prioritizing top-level values
  - This allows for cmdline options like `-u/--username` to overwrite values set in configuration files
- Fixed an issue with `imagefap.com` where incorrectly reported gallery sizes would cause the extractor to fail ([#9](https://github.com/mikf/gallery-dl/issues/9))
- Fixed an issue with `seiga.nicovideo.jp` where invalid characters in an API response caused the XML parser to fail
- Fixed an issue with `seiga.nicovideo.jp` where the filename extension for the first image would be used for all others
- Removed support for old configuration paths on Windows
- Removed several modules:
  - `mangamint`: site is down
  - `whentai`: now requires account with VIP status for original images
  - `kissmanga`: encrypted image URLs (will be re-added later)

## 0.7.0 - 2017-03-06
- Added `--images` and `--chapters` options
  - Specifies which images (or chapters) to download through a comma-separated list of indices or index-ranges
  - Example: `--images -2,4,6-8,10-` will select images with index 1, 2, 4, 6, 7, 8 and 10 up to the last one
- Changed the `-g`/`--get-urls` option
  - The amount of how often the -g option is given now determines up until which level URLs are resolved.
  - See 3bca86618505c21628cd9c7179ce933a78d00ca2
- Changed several option keys:
  - `directory_fmt` -> `directory`
  - `filename_fmt` -> `filename`
  - `download-original` -> `original`
- Improved [FoOlSlide](https://foolcode.github.io/FoOlSlide/)-based extractors
- Fixed URL extraction for hentai2read
- Fixed an issue with deviantart, where the API access token wouldn't get refreshed

## 0.6.4 - 2017-02-13
- Added new extractors:
  - fallenangels (famatg.com)
- Fixed url- and data-extraction for:
  - nhentai
  - mangamint
  - twitter
  - imagetwist
- Disabled InsecureConnectionWarning when no certificates are available

## 0.6.3 - 2017-01-25
- Added new extractors:
  - gomanga
  - yomanga
  - mangafox
- Fixed deviantart extractor failing - switched to using their API
- Fixed an issue with SQLite on Python 3.6
- Automated test builds via Travis CI
- Standalone executables for Windows

## 0.6.2 - 2017-01-05
- Added new extractors:
  - kisscomic
  - readcomics
  - yonkouprod
  - jaiminisbox
- Added manga extractor to batoto-module
- Added user extractor to seiga-module
- Added `-i`/`--input-file` argument to allow local files and stdin as input (like wget)
- Added basic support for `file://` URLs
  - this allows for the recursive extractor to be applied to local files:
  - `$ gallery-dl r:file://[path to file]`
- Added a utility extractor to run unit test URLs
- Updated luscious to deal with API changes
- Fixed twitter to provide the original image URL
- Minor fixes to hentaifoundry
- Removed imgclick extractor

## 0.6.1 - 2016-11-30
- Added new extractors:
  - whentai
  - readcomiconline
  - sensescans, worldthree
  - imgmaid, imagevenue, img4ever, imgspot, imgtrial, pixhost
- Added base class for extractors of [FoOlSlide](https://foolcode.github.io/FoOlSlide/)-based sites
- Changed default paths for configuration files on Windows
  - old paths are still supported, but that will change in future versions
- Fixed aborting downloads if a single one failed ([#5](https://github.com/mikf/gallery-dl/issues/5))
- Fixed cloudflare-bypass cache containing outdated cookies
- Fixed image URLs for hitomi and 8chan
- Updated deviantart to always provide the highest quality image
- Updated README.rst
- Removed doujinmode extractor

## 0.6.0 - 2016-10-08
- Added new extractors:
  - hentaihere
  - dokireader
  - twitter
  - rapidimg, picmaniac
- Added support to find filename extensions by Content-Type response header
- Fixed filename/path issues on Windows ([#4](https://github.com/mikf/gallery-dl/issues/4)):
  - Enable path names with more than 260 characters
  - Remove trailing spaces in path segments
- Updated Job class to automatically set category/subcategory keywords

## 0.5.2 - 2016-09-23
- Added new extractors:
  - pinterest
  - rule34
  - dynastyscans
  - imagebam, coreimg, imgcandy, imgtrex
- Added login capabilities for batoto
- Added `--version` cmdline argument to print the current program version and exit
- Added `--list-extractors` cmdline argument to print names of all extractor classes together with descriptions and example URLs
- Added proper error messages if an image/user does not exist
- Added unittests for every extractor

## 0.5.1 - 2016-08-22
- Added new extractors:
  - luscious
  - doujinmode
  - hentaibox
  - seiga
  - imagefap
- Changed error output to use stderr instead of stdout
- Fixed broken pipes causing an exception-dump by catching BrokenPipeErrors

## 0.5.0 - 2016-07-25

## 0.4.1 - 2015-12-03
- New modules (imagetwist, turboimagehost)
- Manga-extractors: Download entire manga and not just single chapters
- Generic extractor (provisional)
- Better and configurable console output
- Windows support

## 0.4.0 - 2015-11-26

## 0.3.3 - 2015-11-10

## 0.3.2 - 2015-11-04

## 0.3.1 - 2015-10-30

## 0.3.0 - 2015-10-05

## 0.2.0 - 2015-06-28

## 0.1.0 - 2015-05-27
