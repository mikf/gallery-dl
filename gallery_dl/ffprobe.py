# -*- coding: utf-8 -*-

# Copyright 2014-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Fetch Video Length before actually downloading a whole file"""

import subprocess
import json
import time
from datetime import timedelta
from . import util


def get_video_length(obj, url):
    minimum_frames = 10
    data = None
    tries = 0
    msg = ""

    ffprobe = util.expand_path(obj.config("ffprobe-location", "ffprobe"))

    command = [
        ffprobe,
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
    ]

    if obj.headers:
        for key, value in obj.headers.items():
            command.extend(["-headers", key + ": " + value])

    command.append(url)

    while True:
        if tries:
            obj.log.warning("%s (%s/%s)", msg, tries, obj.retries+1)
            if tries > obj.retries:
                return False
            time.sleep(tries)
        tries += 1

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            data = json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            msg = "ffprobe failed: " + e
            print(e)
            continue
        except json.JSONDecodeError:
            msg = "Failed to decode ffprobe output as JSON"
            continue

        # A file typically contains multiple streams (video, audio, subtitle).
        # Here we filter out everything that is not considered a video
        video_streams = [
            float(stream["duration"])
            for stream in data["streams"]
            if stream["codec_type"] == "video" and
            "duration" in stream and
            "avg_frame_rate" in stream and
            frame_count(stream) >= minimum_frames
        ]

        if not video_streams:
            obj.log.info(
                "No video streams found or none with a valid duration "
                "and minimum frames."
            )
            return None

        duration = timedelta(seconds=min(video_streams))
        return duration


def frame_count(stream):
    """Calculates the number of frames in the video stream."""
    try:
        duration = float(stream["duration"])
        avg_frame_rate = eval(stream["avg_frame_rate"])
        return int(duration * avg_frame_rate)
    except (ValueError, ZeroDivisionError):
        return 0
