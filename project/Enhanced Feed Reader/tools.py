from PyQt4.QtCore import *
from os import path



def getFullUrl(context, input):
    """facilitates calling file path names"""
    return str(QUrl.fromLocalFile(path.abspath(input)).toString())

def escapeQuotesXml(input):
    """Prepares a string to be inserted into a XML document"""
    return input.replace("\"", "&quot;").replace("'", "&apos;")