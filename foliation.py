#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# --- 80 cols ---------------------------------------------------------------- #

# Format:
# python3 -m black --line-length=80 --target-version=py310 foliation.py
# Run:
# python3 foliation.py USERNAME

import os
import sys
import json
import time
import textwrap
import re
import copy

from pathlib import Path
from datetime import datetime

DATE_FORMAT = "%a %b %d %H:%M:%S %z %Y"


def process(tweet, all_images, target_username, previous_year) -> str:
    directory = "gallery-dl"
    file_path = Path(f"{directory}/twitter/{target_username}")
    return_value = str()
    the_id = tweet["id_str"]
    created_at = tweet["created_at"]
    parsed_date = datetime.strptime(created_at, DATE_FORMAT)
    year = parsed_date.year
    full_text = tweet["full_text"]
    images = sorted([i for i in all_images if i.startswith(the_id)])
    modified_text = copy.deepcopy(full_text)
    while "...." in modified_text:
        modified_text = modified_text.replace("....", "...")
    if year != previous_year:
        return_value = f"{return_value}== {year}\n\n"
    return_value = f"{return_value}{created_at}\n\n"
    return_value = f"{return_value}....\n{modified_text}\n...."
    return_value = f"{return_value}\n\n"
    for i in images:
        return_value += f"image::{file_path}/{i}[]\n\n"
    return return_value


def get_year(tweet) -> str:
    created_at = tweet["created_at"]
    parsed_date = datetime.strptime(created_at, DATE_FORMAT)
    return parsed_date.year


def main(args) -> int:
    if len(args) < 1:
        raise ValueError("The target username argument is missing.")
    target_username = args[0].strip()
    directory = "gallery-dl"
    file_path = Path(f"{directory}/twitter/tweet_json_data/all_tweets.dat")
    all_tweets_data = list()
    previous_year = str()
    with open(file_path, "r") as f:
        all_tweets_data = [
            json.loads(i.strip()) for i in f.readlines() if i.strip() != ""
        ]
    all_tweets_data.sort(
        key=lambda x: datetime.strptime(
            x["created_at"], DATE_FORMAT
        ).timestamp()
    )
    file_path = Path(f"{directory}/twitter/{target_username}")
    all_images = os.listdir(file_path)
    the_ids = set([re.sub(r"_\d*\.\S*$", "", i.strip()) for i in all_images])
    text = f"= {target_username}\n\n:toc:\n\n"
    for tweet in all_tweets_data:
        if tweet["id_str"] in the_ids:
            year = get_year(tweet)
            if year == previous_year:
                text += "'''\n\n"
            text += str(
                process(tweet, all_images, target_username, previous_year)
            )
            previous_year = get_year(tweet)
    with open(f"{target_username}.adoc", "w") as f:
        print(text)
        f.write(text)
    return 0


if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    exit(exit_code)

# END OF LINE
