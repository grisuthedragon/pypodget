#!/usr/bin/en python3
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

from .download import pod_download
from .podcast import Podcast
from .globals import verbose, set_verbose

__all__ = ["pod_download", "Podcast", "verbose", "set_verbose"]
