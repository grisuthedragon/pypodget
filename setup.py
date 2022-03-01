#!/usr/bin/env python3

from setuptools import setup

setup(
   name='pypodget',
   version='0.1.0',
   author='Martin Koehler',
   author_email='grisuthedragon@users.noreply.github.com',
   scripts=['bin/pypodget'],
   url='http://github.com/grisuthedraong/pypodget',
   license='LICENSE.txt',
   description='A small tool to download podcasts from RSS feeds.',
   long_description=open('README.md').read(),
   install_requires=[
       "requests >= 2.22",
	   "tqdm >= 4.30",
       "eyed3 >= 0.8.10"
   ],
   package_data ={'': ['pods.ini.example']},
   include_package_data=True
)

