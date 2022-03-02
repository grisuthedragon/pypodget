import os

from .globals import verbose, set_verbose
from .download import pod_download
from string import Template



class Podcast:
    def __init__(self, url, folder = "." + os.sep, filename_template = "$year-$month-$day - $title.$ext" ):
        self.__url = url
        self.__folder = folder
        self.__filename_template = filename_template
        self.__filename_template_instance = Template(filename_template)

    @property
    def url(self):
        return self.__url

    @property
    def folder(self):
        return self.__folder

    @folder.setter
    def folder(self,path):
        os.makedirs(path, exist_ok = True)
        self.__folder = path

    @property
    def filename_template(self):
        return self.__filename_template

    @filename_template.setter
    def filename_template(self, template):
        self.__filename_template = template
        self.__filename_template_instance = Template(template)

