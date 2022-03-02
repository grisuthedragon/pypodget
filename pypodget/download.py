#!/usr/bin/env python3
# coding: utf-8
# pypodget - a consise tool to download podcasts from rss-feeds
# Copyright (C) 2022 Martin Koehler
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

import requests
import os.path
import os
import sys
import tqdm


from .globals import verbose

# Download a file from the Web
def pod_download(url, filename=False):
    if not filename:
        local_filename = os.path.join(".",url.split('/')[-1])
    else:
        local_filename = filename

    r = requests.get(url, stream=verbose, allow_redirects=True)

    if verbose():
        file_size = int(r.headers['Content-Length'])
        chunk = 1
        chunk_size=1024
        num_bars = int(file_size / chunk_size)

        with open(local_filename, 'wb') as fp:
            for chunk in tqdm.tqdm(
                                    r.iter_content(chunk_size=chunk_size)
                                    , total= num_bars
                                    , unit = 'KB'
                                    , desc = local_filename
                                    , leave = True # progressbar stays
                                ):
                fp.write(chunk)
    else:
        open(local_filename, 'wb').write(r.content)
    return
