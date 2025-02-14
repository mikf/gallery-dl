# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Helpers for interacting with youtube-dl"""

import re
import shlex
import itertools
from . import text, util, exception


def import_module(module_name):
    if module_name is None:
        try:
            return __import__("yt_dlp")
        except (ImportError, SyntaxError):
            return __import__("youtube_dl")
    return util.import_file(module_name)


def construct_YoutubeDL(module, obj, user_opts, system_opts=None):
    opts = argv = None
    config = obj.config

    cfg = config("config-file")
    if cfg:
        with open(util.expand_path(cfg)) as fp:
            contents = fp.read()
        argv = shlex.split(contents, comments=True)

    cmd = config("cmdline-args")
    if cmd:
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        argv = (argv + cmd) if argv else cmd

    try:
        opts = parse_command_line(module, argv) if argv else user_opts
    except SystemExit:
        raise exception.StopExtraction("Invalid command-line option")

    if opts.get("format") is None:
        opts["format"] = config("format")
    if opts.get("nopart") is None:
        opts["nopart"] = not config("part", True)
    if opts.get("updatetime") is None:
        opts["updatetime"] = config("mtime", True)
    if opts.get("ratelimit") is None:
        opts["ratelimit"] = text.parse_bytes(config("rate"), None)
    if opts.get("min_filesize") is None:
        opts["min_filesize"] = text.parse_bytes(config("filesize-min"), None)
    if opts.get("max_filesize") is None:
        opts["max_filesize"] = text.parse_bytes(config("filesize-max"), None)

    raw_opts = config("raw-options")
    if raw_opts:
        opts.update(raw_opts)
    if config("logging", True):
        opts["logger"] = obj.log
    if system_opts:
        opts.update(system_opts)

    return module.YoutubeDL(opts)


def parse_command_line(module, argv):
    parser, opts, args = module.parseOpts(argv)

    ytdlp = (module.__name__ == "yt_dlp")
    std_headers = module.std_headers

    try:
        parse_bytes = module.parse_bytes
    except AttributeError:
        parse_bytes = module.FileDownloader.parse_bytes

    # HTTP headers
    if opts.user_agent is not None:
        std_headers["User-Agent"] = opts.user_agent
    if opts.referer is not None:
        std_headers["Referer"] = opts.referer
    if opts.headers:
        if isinstance(opts.headers, dict):
            std_headers.update(opts.headers)
        else:
            for h in opts.headers:
                key, _, value = h.partition(":")
                std_headers[key] = value

    if opts.ratelimit is not None:
        opts.ratelimit = parse_bytes(opts.ratelimit)
    if getattr(opts, "throttledratelimit", None) is not None:
        opts.throttledratelimit = parse_bytes(opts.throttledratelimit)
    if opts.min_filesize is not None:
        opts.min_filesize = parse_bytes(opts.min_filesize)
    if opts.max_filesize is not None:
        opts.max_filesize = parse_bytes(opts.max_filesize)
    if opts.max_sleep_interval is None:
        opts.max_sleep_interval = opts.sleep_interval
    if getattr(opts, "overwrites", None):
        opts.continue_dl = False
    if opts.retries is not None:
        opts.retries = parse_retries(opts.retries)
    if getattr(opts, "file_access_retries", None) is not None:
        opts.file_access_retries = parse_retries(opts.file_access_retries)
    if opts.fragment_retries is not None:
        opts.fragment_retries = parse_retries(opts.fragment_retries)
    if getattr(opts, "extractor_retries", None) is not None:
        opts.extractor_retries = parse_retries(opts.extractor_retries)
    if opts.buffersize is not None:
        opts.buffersize = parse_bytes(opts.buffersize)
    if opts.http_chunk_size is not None:
        opts.http_chunk_size = parse_bytes(opts.http_chunk_size)
    if opts.extractaudio:
        opts.audioformat = opts.audioformat.lower()
    if opts.audioquality:
        opts.audioquality = opts.audioquality.strip("kK")
    if opts.recodevideo is not None:
        opts.recodevideo = opts.recodevideo.replace(" ", "")
    if getattr(opts, "remuxvideo", None) is not None:
        opts.remuxvideo = opts.remuxvideo.replace(" ", "")
    if getattr(opts, "wait_for_video", None) is not None:
        min_wait, _, max_wait = opts.wait_for_video.partition("-")
        opts.wait_for_video = (module.parse_duration(min_wait),
                               module.parse_duration(max_wait))

    if opts.date is not None:
        date = module.DateRange.day(opts.date)
    else:
        date = module.DateRange(opts.dateafter, opts.datebefore)

    decodeOption = getattr(module, "decodeOption", util.identity)
    compat_opts = getattr(opts, "compat_opts", ())

    def _unused_compat_opt(name):
        if name not in compat_opts:
            return False
        compat_opts.discard(name)
        compat_opts.update(["*%s" % name])
        return True

    def set_default_compat(
            compat_name, opt_name, default=True, remove_compat=True):
        attr = getattr(opts, opt_name, None)
        if compat_name in compat_opts:
            if attr is None:
                setattr(opts, opt_name, not default)
                return True
            else:
                if remove_compat:
                    _unused_compat_opt(compat_name)
                return False
        elif attr is None:
            setattr(opts, opt_name, default)
        return None

    set_default_compat("abort-on-error", "ignoreerrors", "only_download")
    set_default_compat("no-playlist-metafiles", "allow_playlist_files")
    set_default_compat("no-clean-infojson", "clean_infojson")
    if "format-sort" in compat_opts:
        opts.format_sort.extend(module.InfoExtractor.FormatSort.ytdl_default)
    _video_multistreams_set = set_default_compat(
        "multistreams", "allow_multiple_video_streams",
        False, remove_compat=False)
    _audio_multistreams_set = set_default_compat(
        "multistreams", "allow_multiple_audio_streams",
        False, remove_compat=False)
    if _video_multistreams_set is False and _audio_multistreams_set is False:
        _unused_compat_opt("multistreams")

    if isinstance(opts.outtmpl, dict):
        outtmpl = opts.outtmpl
        outtmpl_default = outtmpl.get("default")
    else:
        opts.outtmpl = outtmpl = outtmpl_default = ""

    if "filename" in compat_opts:
        if outtmpl_default is None:
            outtmpl_default = outtmpl["default"] = "%(title)s-%(id)s.%(ext)s"
        else:
            _unused_compat_opt("filename")

    if opts.extractaudio and not opts.keepvideo and opts.format is None:
        opts.format = "bestaudio/best"

    if ytdlp:
        def metadataparser_actions(f):
            if isinstance(f, str):
                yield module.MetadataFromFieldPP.to_action(f)
            else:
                REPLACE = module.MetadataParserPP.Actions.REPLACE
                args = f[1:]
                for x in f[0].split(","):
                    action = [REPLACE, x]
                    action += args
                    yield action

        parse_metadata = getattr(opts, "parse_metadata", None)
        if isinstance(parse_metadata, dict):
            if opts.metafromtitle is not None:
                if "pre_process" not in parse_metadata:
                    parse_metadata["pre_process"] = []
                parse_metadata["pre_process"].append(
                    "title:%s" % opts.metafromtitle)
            opts.parse_metadata = {
                k: list(itertools.chain.from_iterable(map(
                        metadataparser_actions, v)))
                for k, v in parse_metadata.items()
            }
        else:
            if parse_metadata is None:
                parse_metadata = []
            if opts.metafromtitle is not None:
                parse_metadata.append("title:%s" % opts.metafromtitle)
            opts.parse_metadata = list(itertools.chain.from_iterable(map(
                metadataparser_actions, parse_metadata)))

        opts.metafromtitle = None
    else:
        opts.parse_metadata = ()

    download_archive_fn = module.expand_path(opts.download_archive) \
        if opts.download_archive is not None else opts.download_archive

    if getattr(opts, "getcomments", None):
        opts.writeinfojson = True

    if getattr(opts, "no_sponsorblock", None):
        opts.sponsorblock_mark = set()
        opts.sponsorblock_remove = set()
    else:
        opts.sponsorblock_mark = \
            getattr(opts, "sponsorblock_mark", None) or set()
        opts.sponsorblock_remove = \
            getattr(opts, "sponsorblock_remove", None) or set()
    opts.remove_chapters = getattr(opts, "remove_chapters", None) or ()

    try:
        postprocessors = list(module.get_postprocessors(opts))
    except AttributeError:
        postprocessors = legacy_postprocessors(
            opts, module, ytdlp, compat_opts)

    match_filter = (
        None if opts.match_filter is None
        else module.match_filter_func(opts.match_filter))

    cookiesfrombrowser = getattr(opts, "cookiesfrombrowser", None)
    if cookiesfrombrowser:
        match = re.fullmatch(r"""(?x)
            (?P<name>[^+:]+)
            (?:\s*\+\s*(?P<keyring>[^:]+))?
            (?:\s*:\s*(?!:)(?P<profile>.+?))?
            (?:\s*::\s*(?P<container>.+))?
        """, cookiesfrombrowser)
        if match:
            browser, keyring, profile, container = match.groups()
            if keyring is not None:
                keyring = keyring.upper()
            cookiesfrombrowser = (browser.lower(), profile, keyring, container)
        else:
            cookiesfrombrowser = None

    return {
        "usenetrc": opts.usenetrc,
        "netrc_location": getattr(opts, "netrc_location", None),
        "username": opts.username,
        "password": opts.password,
        "twofactor": opts.twofactor,
        "videopassword": opts.videopassword,
        "ap_mso": opts.ap_mso,
        "ap_username": opts.ap_username,
        "ap_password": opts.ap_password,
        "quiet": opts.quiet,
        "no_warnings": opts.no_warnings,
        "forceurl": opts.geturl,
        "forcetitle": opts.gettitle,
        "forceid": opts.getid,
        "forcethumbnail": opts.getthumbnail,
        "forcedescription": opts.getdescription,
        "forceduration": opts.getduration,
        "forcefilename": opts.getfilename,
        "forceformat": opts.getformat,
        "forceprint": getattr(opts, "forceprint", None) or (),
        "force_write_download_archive": getattr(
            opts, "force_write_download_archive", None),
        "simulate": opts.simulate,
        "skip_download": opts.skip_download,
        "format": opts.format,
        "allow_unplayable_formats": getattr(
            opts, "allow_unplayable_formats", None),
        "ignore_no_formats_error": getattr(
            opts, "ignore_no_formats_error", None),
        "format_sort": getattr(
            opts, "format_sort", None),
        "format_sort_force": getattr(
            opts, "format_sort_force", None),
        "allow_multiple_video_streams": opts.allow_multiple_video_streams,
        "allow_multiple_audio_streams": opts.allow_multiple_audio_streams,
        "check_formats": getattr(
            opts, "check_formats", None),
        "outtmpl": opts.outtmpl,
        "outtmpl_na_placeholder": opts.outtmpl_na_placeholder,
        "paths": getattr(opts, "paths", None),
        "autonumber_size": opts.autonumber_size,
        "autonumber_start": opts.autonumber_start,
        "restrictfilenames": opts.restrictfilenames,
        "windowsfilenames": getattr(opts, "windowsfilenames", None),
        "ignoreerrors": opts.ignoreerrors,
        "force_generic_extractor": opts.force_generic_extractor,
        "ratelimit": opts.ratelimit,
        "throttledratelimit": getattr(opts, "throttledratelimit", None),
        "overwrites": getattr(opts, "overwrites", None),
        "retries": opts.retries,
        "file_access_retries": getattr(opts, "file_access_retries", None),
        "fragment_retries": opts.fragment_retries,
        "extractor_retries": getattr(opts, "extractor_retries", None),
        "skip_unavailable_fragments": opts.skip_unavailable_fragments,
        "keep_fragments": opts.keep_fragments,
        "concurrent_fragment_downloads": getattr(
            opts, "concurrent_fragment_downloads", None),
        "buffersize": opts.buffersize,
        "noresizebuffer": opts.noresizebuffer,
        "http_chunk_size": opts.http_chunk_size,
        "continuedl": opts.continue_dl,
        "noprogress": True if opts.noprogress is None else opts.noprogress,
        "playliststart": opts.playliststart,
        "playlistend": opts.playlistend,
        "playlistreverse": opts.playlist_reverse,
        "playlistrandom": opts.playlist_random,
        "noplaylist": opts.noplaylist,
        "logtostderr": outtmpl_default == "-",
        "consoletitle": opts.consoletitle,
        "nopart": opts.nopart,
        "updatetime": opts.updatetime,
        "writedescription": opts.writedescription,
        "writeannotations": opts.writeannotations,
        "writeinfojson": opts.writeinfojson,
        "allow_playlist_files": opts.allow_playlist_files,
        "clean_infojson": opts.clean_infojson,
        "getcomments": getattr(opts, "getcomments", None),
        "writethumbnail": opts.writethumbnail is True,
        "write_all_thumbnails": getattr(opts, "write_all_thumbnails", None) or
        opts.writethumbnail == "all",
        "writelink": getattr(opts, "writelink", None),
        "writeurllink": getattr(opts, "writeurllink", None),
        "writewebloclink": getattr(opts, "writewebloclink", None),
        "writedesktoplink": getattr(opts, "writedesktoplink", None),
        "writesubtitles": opts.writesubtitles,
        "writeautomaticsub": opts.writeautomaticsub,
        "allsubtitles": opts.allsubtitles,
        "subtitlesformat": opts.subtitlesformat,
        "subtitleslangs": opts.subtitleslangs,
        "matchtitle": decodeOption(opts.matchtitle),
        "rejecttitle": decodeOption(opts.rejecttitle),
        "max_downloads": opts.max_downloads,
        "prefer_free_formats": opts.prefer_free_formats,
        "trim_file_name": getattr(opts, "trim_file_name", None),
        "verbose": opts.verbose,
        "dump_intermediate_pages": opts.dump_intermediate_pages,
        "write_pages": opts.write_pages,
        "test": opts.test,
        "keepvideo": opts.keepvideo,
        "min_filesize": opts.min_filesize,
        "max_filesize": opts.max_filesize,
        "min_views": opts.min_views,
        "max_views": opts.max_views,
        "daterange": date,
        "cachedir": opts.cachedir,
        "youtube_print_sig_code": opts.youtube_print_sig_code,
        "age_limit": opts.age_limit,
        "download_archive": download_archive_fn,
        "break_on_existing": getattr(opts, "break_on_existing", None),
        "break_on_reject": getattr(opts, "break_on_reject", None),
        "break_per_url": getattr(opts, "break_per_url", None),
        "skip_playlist_after_errors": getattr(
            opts, "skip_playlist_after_errors", None),
        "cookiefile": opts.cookiefile,
        "cookiesfrombrowser": cookiesfrombrowser,
        "nocheckcertificate": opts.no_check_certificate,
        "prefer_insecure": opts.prefer_insecure,
        "proxy": opts.proxy,
        "socket_timeout": opts.socket_timeout,
        "bidi_workaround": opts.bidi_workaround,
        "debug_printtraffic": opts.debug_printtraffic,
        "prefer_ffmpeg": opts.prefer_ffmpeg,
        "include_ads": opts.include_ads,
        "default_search": opts.default_search,
        "dynamic_mpd": getattr(opts, "dynamic_mpd", None),
        "extractor_args": getattr(opts, "extractor_args", None),
        "youtube_include_dash_manifest": getattr(
            opts, "youtube_include_dash_manifest", None),
        "youtube_include_hls_manifest": getattr(
            opts, "youtube_include_hls_manifest", None),
        "encoding": opts.encoding,
        "extract_flat": opts.extract_flat,
        "live_from_start": getattr(opts, "live_from_start", None),
        "wait_for_video": getattr(opts, "wait_for_video", None),
        "mark_watched": opts.mark_watched,
        "merge_output_format": opts.merge_output_format,
        "postprocessors": postprocessors,
        "fixup": opts.fixup,
        "source_address": opts.source_address,
        "sleep_interval_requests": getattr(
            opts, "sleep_interval_requests", None),
        "sleep_interval": opts.sleep_interval,
        "max_sleep_interval": opts.max_sleep_interval,
        "sleep_interval_subtitles": getattr(
            opts, "sleep_interval_subtitles", None),
        "external_downloader": opts.external_downloader,
        "playlist_items": opts.playlist_items,
        "xattr_set_filesize": opts.xattr_set_filesize,
        "match_filter": match_filter,
        "no_color": getattr(opts, "no_color", None),
        "ffmpeg_location": opts.ffmpeg_location,
        "hls_prefer_native": opts.hls_prefer_native,
        "hls_use_mpegts": opts.hls_use_mpegts,
        "hls_split_discontinuity": getattr(
            opts, "hls_split_discontinuity", None),
        "external_downloader_args": opts.external_downloader_args,
        "postprocessor_args": opts.postprocessor_args,
        "cn_verification_proxy": opts.cn_verification_proxy,
        "geo_verification_proxy": opts.geo_verification_proxy,
        "geo_bypass": getattr(
            opts, "geo_bypass", "default"),
        "geo_bypass_country": getattr(
            opts, "geo_bypass_country", None),
        "geo_bypass_ip_block": getattr(
            opts, "geo_bypass_ip_block", None),
        "compat_opts": compat_opts,
    }


def parse_retries(retries, name=""):
    if retries in ("inf", "infinite"):
        return float("inf")
    return int(retries)


def legacy_postprocessors(opts, module, ytdlp, compat_opts):
    postprocessors = []

    sponsorblock_query = opts.sponsorblock_mark | opts.sponsorblock_remove
    if opts.metafromtitle:
        postprocessors.append({
            "key": "MetadataFromTitle",
            "titleformat": opts.metafromtitle,
        })
    if getattr(opts, "add_postprocessors", None):
        postprocessors += list(opts.add_postprocessors)
    if sponsorblock_query:
        postprocessors.append({
            "key": "SponsorBlock",
            "categories": sponsorblock_query,
            "api": opts.sponsorblock_api,
            "when": "pre_process",
        })
    if opts.parse_metadata:
        postprocessors.append({
            "key": "MetadataParser",
            "actions": opts.parse_metadata,
            "when": "pre_process",
        })
    if opts.convertsubtitles:
        pp = {"key": "FFmpegSubtitlesConvertor",
              "format": opts.convertsubtitles}
        if ytdlp:
            pp["when"] = "before_dl"
        postprocessors.append(pp)
    if getattr(opts, "convertthumbnails", None):
        postprocessors.append({
            "key": "FFmpegThumbnailsConvertor",
            "format": opts.convertthumbnails,
            "when": "before_dl",
        })
    if getattr(opts, "exec_before_dl_cmd", None):
        postprocessors.append({
            "key": "Exec",
            "exec_cmd": opts.exec_before_dl_cmd,
            "when": "before_dl",
        })
    if opts.extractaudio:
        postprocessors.append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": opts.audioformat,
            "preferredquality": opts.audioquality,
            "nopostoverwrites": opts.nopostoverwrites,
        })
    if getattr(opts, "remuxvideo", None):
        postprocessors.append({
            "key": "FFmpegVideoRemuxer",
            "preferedformat": opts.remuxvideo,
        })
    if opts.recodevideo:
        postprocessors.append({
            "key": "FFmpegVideoConvertor",
            "preferedformat": opts.recodevideo,
        })
    if opts.embedsubtitles:
        pp = {"key": "FFmpegEmbedSubtitle"}
        if ytdlp:
            pp["already_have_subtitle"] = (
                opts.writesubtitles and "no-keep-subs" not in compat_opts)
        postprocessors.append(pp)
        if not opts.writeautomaticsub and "no-keep-subs" not in compat_opts:
            opts.writesubtitles = True
    if opts.allsubtitles and not opts.writeautomaticsub:
        opts.writesubtitles = True
    remove_chapters_patterns, remove_ranges = [], []
    for regex in opts.remove_chapters:
        if regex.startswith("*"):
            dur = list(map(module.parse_duration, regex[1:].split("-")))
            if len(dur) == 2 and all(t is not None for t in dur):
                remove_ranges.append(tuple(dur))
                continue
        remove_chapters_patterns.append(re.compile(regex))
    if opts.remove_chapters or sponsorblock_query:
        postprocessors.append({
            "key": "ModifyChapters",
            "remove_chapters_patterns": remove_chapters_patterns,
            "remove_sponsor_segments": opts.sponsorblock_remove,
            "remove_ranges": remove_ranges,
            "sponsorblock_chapter_title": opts.sponsorblock_chapter_title,
            "force_keyframes": opts.force_keyframes_at_cuts,
        })
    addchapters = getattr(opts, "addchapters", None)
    embed_infojson = getattr(opts, "embed_infojson", None)
    if opts.addmetadata or addchapters or embed_infojson:
        pp = {"key": "FFmpegMetadata"}
        if ytdlp:
            if embed_infojson is None:
                embed_infojson = "if_exists"
            pp["add_metadata"] = opts.addmetadata
            pp["add_chapters"] = addchapters
            pp["add_infojson"] = embed_infojson

        postprocessors.append(pp)
    if getattr(opts, "sponskrub", False) is not False:
        postprocessors.append({
            "key": "SponSkrub",
            "path": opts.sponskrub_path,
            "args": opts.sponskrub_args,
            "cut": opts.sponskrub_cut,
            "force": opts.sponskrub_force,
            "ignoreerror": opts.sponskrub is None,
            "_from_cli": True,
        })
    if opts.embedthumbnail:
        already_have_thumbnail = (opts.writethumbnail or
                                  getattr(opts, "write_all_thumbnails", False))
        postprocessors.append({
            "key": "EmbedThumbnail",
            "already_have_thumbnail": already_have_thumbnail,
        })
        if not already_have_thumbnail:
            opts.writethumbnail = True
            if isinstance(opts.outtmpl, dict):
                opts.outtmpl["pl_thumbnail"] = ""
    if getattr(opts, "split_chapters", None):
        postprocessors.append({
            "key": "FFmpegSplitChapters",
            "force_keyframes": opts.force_keyframes_at_cuts,
        })
    if opts.xattrs:
        postprocessors.append({"key": "XAttrMetadata"})
    if opts.exec_cmd:
        postprocessors.append({
            "key": "Exec",
            "exec_cmd": opts.exec_cmd,
            "when": "after_move",
        })

    return postprocessors
