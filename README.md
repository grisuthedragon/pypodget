pypodget 0.1.1
==============

PyPodGet is a GPL-3 licensed tool to download Podcast-RSS feeds from the command
line. Copyright (C) 2022 by Martin Koehler

Installation
------------

The tool requires Python 3.7 and the following packages:

 - requests
 - eye3
 - tqdm

The tool can be installed either by running
```shell
python3 setup.py
```
or by using `pip` and the release tarball
```shell
pip3 install pypodget-0.1.0.tar.gz
```

Usage
-----
The tool is configured using a `ini` file, where each section represents a
podcast. A section inside this file looks like the following:
```
[Podcast Name]
url = URL-OF-THE-RSS-FEED
directory = DESTINATION-FOLDER
filename = FILENAME-TEMPLATE
```
See `pods.ini.example` for details.

The filename is a template string, which is processed using Python's
string-template engine. The following fields can be used in this template:

| Placeholder | Description                                               |
|-------------|-----------------------------------------------------------|
| $year       | year of the publication                                   |
| $month      | month of the publication (with leading zeros)             |
| $day        | day of the publication (with leading zeros)               |
| $minute     | minute of the publication (with leading zeros)            |
| $hour       | hour of the publication (with leading zeros)              |
| $title      | title of the episode                                      |
| $feed_title | title of the RSS feed                                     |
| $ext        | extension of the episodes file                            |
| $number     | number of the episode                                     |
| $inumber    | inverse number of the episode ( $nepisodes - $number )    |
| $episodes   | total number of epiodes                                   |
| $mytitle    | title of the podcast from the ini file                    |

The default template string is
```
$year-$month-$day - $title.$ext
```

The tool is executed
```
pypodget -c yourconfig.ini
```
By adding `-s` to the command line pypodget enters the silent mode and displays
nothing. This can be used to avoid long outputs in cron jobs.

If not ID3 information is available in the podcast file, author and title will
be set to the feed_title and the title of the episode, respectively.


