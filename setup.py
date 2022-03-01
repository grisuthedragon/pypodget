from setuptools import setup

setup(
   name='pypodget',
   version='0.1.0',
   author='Martin Koehler',
   author_email='aac@example.com',
   scripts=['bin/pypodget'],
   url='http://pypi.python.org/pypi/PackageName/',
   license='LICENSE.txt',
   description='An awesome package that does something',
   long_description='open(README.txt).read()',
   install_requires=[
       "requests >= 2.22",
	   "tqdm >= 4.30"
   ],
)

