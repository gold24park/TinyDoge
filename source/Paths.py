import os
import sys


def getRootPath():
    if getattr(sys, 'frozen', False):
        # this is a Pyinstaller bundle
        return sys._MEIPASS
    else:
        # normal python process
        return os.getcwd()