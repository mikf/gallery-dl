import os
import sys
import re
import sqlite3
import importlib

class ExtractorFinder():

    def __init__(self, config):
        self.config = config
        self.match_list = list()
        if "database" in config["general"]:
            path = os.path.expanduser(config["general"]["database"])
            conn = sqlite3.connect(path)
            self.load_from_database(conn)
        self.load_from_config(config)

    def match(self, url):
        for category, regex in self.match_list:
            match = regex.match(url)
            if match:
                module = importlib.import_module("."+category, __package__)
                return module.Extractor(match, self.config)
        return None

    def load_from_database(self, db):
        query = (
            "SELECT regex.re, category.name "
            "FROM   regex JOIN category "
            "ON     regex.category_id = category.id"
        )
        for row in db.execute(query):
            self.add_match(row[1], row[0])

    def load_from_config(self, conf):
        for category in conf:
            for key, value in conf[category].items():
                if(key.startswith("regex")):
                    self.add_match(category, value)

    def add_match(self, category, regex):
        try:
            # print(category, regex)
            self.match_list.append( (category, re.compile(regex)) )
        except:
            print("[Warning] [{0}] failed to compile regular expression '{1}'"
                  .format(category, regex))
