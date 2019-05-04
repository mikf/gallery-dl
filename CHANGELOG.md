# Changelog

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
