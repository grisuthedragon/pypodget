#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# coding: utf-8
#
# pypodget - a consise tool to download podcasts from rss-feeds
# Copyright (C) 2022-2026 Martin Koehler
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
from .download import pod_download
from string import Template
import requests
import xml.etree.ElementTree as ElementTree
from datetime import datetime
import eyed3


class Episode:
    def __init__(self, parent, title, description,
                 pubdate, url, link, local_filename):
        self.__parent = parent
        self.__title = title
        self.__description = description
        self.__pubdate = pubdate
        self.__url = url

        self.__local_filename = local_filename

    def download(self):
        if self.__url is None:
            return
        if not os.path.isfile(self.__local_filename):
            pod_download(self.__url, self.__local_filename)

        eyed3.log.setLevel("ERROR")
        audiofile = eyed3.load(self.__local_filename)
        if not audiofile.tag.artist:
            audiofile.tag.artist = self.__parent.title
        if not audiofile.tag.title:
            audiofile.tag.title = self.__title
        audiofile.tag.save()


class Podcast:
    def __init__(self, url, mytitle, folder="."+os.sep,
                 filename_template="$year-$month-$day - $title.$ext"):
        self.__url = url
        self.__folder = folder
        self.__filename_template = filename_template
        self.__filename_template_instance = Template(filename_template)
        self.__mytitle = mytitle
        self.__episodes = []
        os.makedirs(folder, exist_ok=True)

        self.update()

    def update(self):
        r = requests.get(self.__url)
        if r.status_code != 200:
            raise Exception("Failed to download {:s}, return code {:d}"
                            .format(self.__url, r.status_code))

        feed = ElementTree.fromstring(r.content)
        if feed.findall('channel/title') is not None:
            self.__feed_title = feed.findall('channel/title')[0].text
        else:
            self.__feed_title = None

        if feed.findall('channel/description') is not None:
            txt = feed.findall('channel/description')[0].text
            self.__feed_description = txt
        else:
            self.__feed_description = None

        if feed.findall('channel/link') is not None:
            self.__feed_link = feed.findall('channel/link')[0].text
        else:
            self.__feed_link = None

        if feed.findall('channel/image/url') is not None:
            self.__feed_image = feed.findall('channel/image/url')[-1].text
        else:
            self.__feed_image = None

        self.__nepisodes = len(feed.findall('channel/item'))

        fcounter = 1
        bcounter = self.__nepisodes

        for feed_item in feed.iter("item"):
            title = feed_item.find("title").text
            if feed_item.find('description'):
                description = feed_item.find('description').text
            else:
                description = ""

            pubdate = datetime.strptime(feed_item.find("pubDate").text,
                                        '%a, %d %b %Y %H:%M:%S %z')

            if feed_item.find("enclosure") is None:
                epi_url = None
            else:
                epi_url = feed_item.find("enclosure").attrib["url"]

            title_unicode = title.replace('\'', '').replace('\"', '')
            title_unicode = title_unicode.replace('\\', '')
            title_unicode = title_unicode.replace('/',  '')
            title_unicode = title_unicode.replace(':', '')
            title_unicode = title_unicode.replace('!', '')

            link = feed_item.find('link').text
            ext = (epi_url.split('?')[0]).split('.')[-1]

            filename = self.__filename_template_instance.substitute(
                    year="{:04}".format(pubdate.year),
                    month="{:02}".format(pubdate.month),
                    day="{:02}".format(pubdate.day),
                    minute="{:02}".format(pubdate.minute),
                    hour="{:02}".format(pubdate.hour),
                    title=title_unicode,
                    feed_title=self.__feed_title,
                    ext=ext,
                    number=bcounter,
                    inumber=fcounter,
                    nepisodes=self.__nepisodes,
                    mytitle=self.__mytitle)
            filename = filename.replace('\\', '_')
            filename = filename.replace('/', '_')
            filename = filename.replace(':', '_')
            filename = filename.replace('?', '_')
            filename = filename.replace('*', '_')

            filename = self.__folder + os.sep + filename

            epi = Episode(self, title, description, pubdate,
                          epi_url, link, filename)
            self.__episodes.append(epi)
            fcounter = fcounter + 1
            bcounter = bcounter - 1

    def downloadall(self):
        for epi in self.__episodes:
            epi.download()

    def download(self, episode):
        if episode >= 0 and episode < len(self.__episodes):
            self.__episodes[episode].download()

    def episode(self, number):
        if number >= 0 and number < len(self.__episodes):
            return self.__episodes[number]
        else:
            return None

    @property
    def url(self):
        return self.__url

    @property
    def folder(self):
        return self.__folder

    @folder.setter
    def folder(self, path):
        os.makedirs(path, exist_ok=True)
        self.__folder = path
        self.update()

    @property
    def filename_template(self):
        return self.__filename_template

    @filename_template.setter
    def filename_template(self, template):
        self.__filename_template = template
        self.__filename_template_instance = Template(template)
        self.update()

    @property
    def nepisodes(self):
        return len(self.__episodes)

    @property
    def title(self):
        return self.__feed_title

    @property
    def description(self):
        return self.__feed_description

    @property
    def link(self):
        return self.__feed_link

    @property
    def image(self):
        return self.__feed_image

    @property
    def mytitle(self):
        return self.__mytitle
