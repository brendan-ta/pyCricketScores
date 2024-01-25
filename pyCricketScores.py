#!/usr/bin/env python3
# Version: 0.1
# Author : Brendan Ta

import xml.etree.ElementTree as ET
import requests
import re
import time

UPDATE_RATE = 10


class colours:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class AllMatches(object):
    def __init__(self):
        self.live_rss = "https://static.cricinfo.com/rss/livescores.xml"
        self.getMatchDetails()

    def getMatchDetails(self):
        self.matchDetails = self.getHtmlRequest(self.live_rss)

    def getHtmlRequest(self, html_string):
        return requests.get(html_string)

    def retMatchDetails(self):
        return self.matchDetails.text


class ParseXML(object):
    def __init__(self, data):
        self.match_data = data
        self.all_matches = {}
        self.returnMatches()

    def returnMatches(self):
        root_node = ET.fromstring(self.match_data)
        items = root_node.findall(".//item")

        for index, item in enumerate(items, 1):
            title = item.find("title").text
            link = item.find("link").text
            self.all_matches[index] = {"title": title, "link": link}


class CronScore(object):
    def __init__(self, match):
        self.match_path = match
        self.score = ""
        self.t_score = ""
        self.details = ""
        self.t_details = ""

    def getScore(self):
        self.full_entry = requests.get(self.match_path)
        self.score = re.findall(r"<title>(.*?)</title>", self.full_entry.text)
        self.current_time = re.findall(
            r'<span class="data">Ground time:(.*?)</span>', self.full_entry.text
        )

    def pollScore(self):
        while True:
            self.getScore()
            scoreSplit = self.score[0].split(" - ")
            cScore = scoreSplit[0]
            details = scoreSplit[1]
            if self.t_details != details:
                self.t_details = details
                print("{0}{1}{2}".format(colours.UNDERLINE, details, colours.ENDC))
            if self.t_score != self.score[0]:
                self.t_score = self.score[0]
                print(
                    "{0}[{1}]{2} {3}{4}{5}".format(
                        colours.OKCYAN,
                        self.current_time[0].lstrip(),
                        colours.ENDC,
                        colours.BOLD,
                        cScore,
                        colours.ENDC,
                    )
                )
            time.sleep(UPDATE_RATE)


def main():
    ams = AllMatches()
    pXML = ParseXML(ams.retMatchDetails())

    print("Available cricket matches: \n-------------------------")

    for i, info in pXML.all_matches.items():
        print(i, info["title"])

    user_index = int(
        input("{0}Enter match number above:{1} ".format(colours.BOLD, colours.ENDC))
    )
    selected_item = pXML.all_matches.get(user_index)

    try:
        if selected_item:
            print(
                "{0}Selected match:{1} {2}\n".format(
                    colours.BOLD, colours.ENDC, selected_item["title"]
                )
            )

        cs = CronScore(selected_item["link"])
        cs.pollScore()
    except:
        print("Exception caught")


if __name__ == "__main__":
    main()
