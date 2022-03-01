#!/usr/bin/env python3

from setuptools import setup

setup(
   name='pypodget',
   version='0.1.0',
   author='Martin Koehler',
   author_email='grisuthedragon@users.noreply.github.com',
   scripts=['bin/pypodget'],
   url='http://github.com/grisuthedraong/pypodget',
   license=('LICENSE.txt',),
   description='A small tool to download podcasts from RSS feeds.',
   long_description=open('README.md').read(),
   python_requires='>3.7.0',
   install_requires=[
       "requests >= 2.22",
	   "tqdm >= 4.30",
       "eyed3 >= 0.8.10"
   ],
   package_data ={'': ['pods.ini.example']},
   include_package_data=True,
   classifiers = [
       'Development Status :: 2 - Pre-Alpha',
       'Environment :: Console',
       'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
       'Operating System :: OS Independent',
       'Programming Language :: Python :: 3',
       'Topic :: Multimedia :: Sound/Audio',
       ]
)

