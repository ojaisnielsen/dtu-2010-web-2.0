"""
This module provides specific tools to get content from IMDb
"""

import urllib, re, imdb, shelve
from urllib import urlopen
from urlparse import urlsplit
from twisted.web import microdom
from os import path
from PIL import Image


def openCachedURL(url):
    """
    This function creates a file object containing the data from the given URL "url". It downloads the content to a file which name is the URL (with the special characters encoded). If the file exists it only opens it, without downloading again.
    """
    filename = urllib.quote(url, "")
    if path.isfile(filename):
        file = open(filename, "rb")
        return file
    else:
        socket = urlopen(url)
        content = socket.read()
        file = open(filename, "wb")
        file.write(content)
        return openCachedURL(url)

def getIMDbTop250():
    """
    This functions the IMDb IDs of the movies from the Top 250. IMDbPy doesn't provide a way to do this so this function accesses the webpage displaying the Top 250 and retreives the IDs from the HTML source.
    """
    html = openCachedURL("http://www.imdb.com/chart/top").read()
    doc = microdom.parseString(html, beExtremelyLenient = 1)
    mainDiv = doc.getElementById("main")
    rows = mainDiv.getElementsByTagName("tr")
    movieIDs = []
    for row in rows[1:]:
        movieURL = row.getElementsByTagName("a")[0].getAttribute("href")
        URLElements = urlsplit(movieURL)
        URLPathElements = URLElements[2].strip("/").split("/")
        movieID = re.sub("[^0-9]", "", URLPathElements[-1])
        movieIDs.append(movieID)
    return movieIDs


class IMDbInterface:
    """
    This is some kind of a offline capable version of the IMDb access provided by IMDbPy. It download data and saves it to a local file. If the requested data is already in the file, it doesn't download it again.
    """
    def __init__(self, filename):
        """
        "filename" is the name of the file in which the data is (or will be) stored. If the file doesn't exist, it is created.
        """
        self._shelf = shelve.open(filename)
        self._IMDbAccess = imdb.IMDb()

    def getMovie(self, movieID):
        """
        This method return a IMDbPy movie object from its ID "movieID".
        """
        if not(movieID in self._shelf.keys()):
            self._shelf[movieID] = self._IMDbAccess.get_movie(movieID)
        return self._shelf[movieID]

    def getThumbnail(self, movieID, size = 100):
        """
        This method returns a thumbnail corresponding to the movie which ID is "movieID". The optional parameter "size" sets the bigest dimension of the thumbnail in pixels. Its default value is 100 pixels. If the thumbnail cannot be found, it returns "False".
        """
        movie = self.getMovie(movieID)
        if "cover url" in movie.keys():
            im = Image.open(openCachedURL(movie["cover url"]))
            im.thumbnail((size, size))
            return im
        else:
            return False

