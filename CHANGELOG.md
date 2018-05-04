# Changelog

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
