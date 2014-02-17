﻿import os
from xml.dom import minidom
import options

def get_reader():
    path = options.getOptions()[0].in_path
    in_format = options.getOptions()[0].in_format
    a = {"ISAR": XmlReader(path), "SACK": CppReader(path)}
    return a[in_format]

class CppReader(object):
    def __init__(self, sack_dir_path):
        pass


class XmlReader(object):
    files = []

    def __init__(self, xml_dir_path):
        self.tree_files = {}
        self.xml_dir = xml_dir_path

    def __open_files(self):
        for x in self.files:
            self.tree_files[x.partition('.')[0]]=self.__open_file(x)

    def __open_file(self, file):
        file_dir = os.path.join(self.xml_dir, file)
        dom_tree = minidom.parse(file_dir)
        return dom_tree

    def __set_files_to_parse(self):
        all_files = os.listdir(self.xml_dir)
        for f in all_files:    # TODO: Think about some error message, now I do not know whether the operation was successful - see the first test
            if f.endswith('.xml'):
                self.files.append(f)

    def read_files(self):
        self.__set_files_to_parse()
        self.__open_files()

    def return_tree_files(self):
        if len(self.tree_files.keys()) == 0:
            self.read_files()
        return self.tree_files
