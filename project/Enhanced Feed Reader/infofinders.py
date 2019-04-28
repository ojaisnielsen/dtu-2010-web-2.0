'''
Web 2.0 & Mobile Interaction -- Final Project
December 4, 2009

Olivier Jais-Nielsen (s090763)
Andrea Lai (s091088)

The Enhanced Feed Reader uses latent semantic analysis to identify people, organizations, and places within an RSS feed and pull in relevant additional content (Google Maps, Google Search, and recent tweets) for display. 

infofinders.py obtains the extra information for display alongside the RSS feed
'''

from lxml import etree
import urllib
import urllib2
from geopy import geocoders
import simplejson
from tools import escapeQuotesXml
try:
	from twython import twython
except ImportError:
	import twython

# initiaion for geopy -- requires Google maps API key
geocoder = geocoders.Google("ABQIAAAAxGk5YmrjBWSHyDAwYYY-MhQ_1E-tD_iqbAxovATVDR2ADdA5xxSroItyCgyEHDdZPxGVbxq0dNYa-A")
realNameCache = {}
locationCoordinatesCache = {}

def getMapUrl(context, input):
    """generates a Google map based on a search string"""
    url = "http://maps.google.com/maps?"
    url += urllib.urlencode({"q": input.encode("utf-8"), "output": "embed"})
    return url


def getWikipediaBestMatch(name):
    """searches Wikipedia for the best match to a given string. If none exists, the string is not identified as an entity."""
    search = urllib.urlencode({"go": "Go", "search": name, "title": "Special:Search"})
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    wikipediaSearch = opener.open("http://en.wikipedia.org/w/index.php", search)
    result = etree.parse(wikipediaSearch, etree.HTMLParser())
    wikipediaSearch.close()
    noExactMatch = result.xpath("count(//*[@class = 'searchresults']) > 0")
    match = ""
    if noExactMatch:
        suggestion = result.xpath("//*[@class = 'searchdidyoumean']/descendant::em")
        if (len(suggestion) > 0):
            match = getWikipediaBestMatch(suggestion[0].text)
    else:
        title = result.xpath("//title")
        try:
            title = title[0].text.split(" - Wikipedia")[0]
            match = title.strip()
        except IndexError:
            pass
    return match

def getRealName(context, input):
    """Takes the best match from Wikipedia as the real name of some input string, the tentative entity"""
    global realNameCache
    if input.strip() == "":
        return ""
    else:
        realNameCache.setdefault(input, escapeQuotesXml(getWikipediaBestMatch(input)))
        return realNameCache[input]

def getLocationCoordinates(context, input):
    """ obtains the precise location coordinates using GeoPy for similiarity analysis by spatial localization"""
    global geocoder
    global locationCoordinatesCache
    if not input in locationCoordinatesCache.keys():
        try:
            place, (lat, lng) = geocoder.geocode(input)
            locationCoordinatesCache[input] = "%s %s" %(lat, lng)
        except:
            locationCoordinatesCache[input] = ""
    return locationCoordinatesCache[input]

def loadXpathFunctions(functions, namespace):
    for function in functions:
        namespace[function.__name__] = function

        
def getGoogleSearch(context, input):
    """Returns the top two Google Search results and their descriptions for a given input"""
    
    # search Google for the input string
    input = urllib.quote_plus(input)
    url = ('http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s') % (input)
    request = urllib2.Request(url, None, {'Referer': '/localhost/'})
    response = urllib2.urlopen(request)
    results = simplejson.load(response)

    result = '<div><br/>'
        
    # # scrape first five results for item link and title
    for item in results["responseData"]["results"][0:2]:
        link = '<a href="%s"><b>' % (item["url"])
        title = item["titleNoFormatting"] + '</b></a><br/>'
        text = item["content"]
        result += link + title + text + '<br/><br/>'
    
    # # result is formatted in html, read and displayed as such
    html = etree.fromstring('%s <br/></div>' % (result))
    return html

def getTweets(context, input):
    """Returns the first 3 tweets matching a given search string"""
    
    # search Twitter for tweets matching the input string
    twitter = twython.setup()
    # take only the first 3 tweets
    search_results = twitter.searchTwitter(input, rpp="3")

    result = '<div><br/>'
    for tweet in search_results["results"]:
        ref = '<a href="http://twitter.com/%s"><b>%s </b></a>:  ' % (tweet["from_user"], tweet["from_user"])
        tweet = "%s <br/>" % (tweet["text"])
        result += ref + tweet

    # result is formatted in html, read and displayed as such
    html = etree.fromstring('%s<br/></div>' % (result))
    return html


if __name__ == "__main__":
    print getWikipediaBestMatch("barack obama")
    print getWikipediaBestMatch("obama")
    print getWikipediaBestMatch("obrama")
    print getWikipediaBestMatch("dzahdizqnjf,lengflmqeorigmq")






