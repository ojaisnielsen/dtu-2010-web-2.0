'''
Web 2.0 & Mobile Interaction -- Final Project
December 4, 2009

Olivier Jais-Nielsen (s090763)
Andrea Lai (s091088)

The Enhanced Feed Reader uses latent semantic analysis to identify people, organizations, and places within an RSS feed and pull in relevant additional content (Google Maps, Google Search, and recent tweets) for display. 


dbaccess.py holds the vectors associated with entities and calculates their similarities/assocations when called.
'''

from lxml import etree
from math import pi, sqrt, sin, cos, atan2
import sys
from tools import escapeQuotesXml

def distVectors(vector1, vector2):
    """calculate the distance between two vectors"""
    keys1 = set(vector1.keys())
    keys2 = set(vector2.keys())
    d = 0
    for key in (keys1 | keys2):
        if key == "coordinates":
            vector1.setdefault(key, [])
            vector2.setdefault(key, [])
            d += squareDistCoords(vector1[key], vector2[key])
        else:
            vector1.setdefault(key, 0)
            vector2.setdefault(key, 0)
            d += (vector1[key] - vector2[key])**2
    return sqrt(d)


def sphereDist((lat1, long1), (lat2, long2)):
    """calculate spherical distance between two points where the coordinates are known in longitude and latitude"""
    a = sin((lat2 - lat1) / 2)**2 + cos(lat1) * cos(lat2) * (sin((long2 - long1) / 2)**2)
    b = 2 * atan2(sqrt(a), sqrt(1 - a))
    return b / pi

def squareDistCoords(coords1, coords2):
    """ Gives average square distance of the distances for all the points in a vector to another set."""
    n = (len(coords1) + len(coords2))
    if n == 0:
        return 1
    else:
        pointToSetDists = [min([1] + [sphereDist(pt2, pt1) for pt2 in coords1]) for pt1 in coords2]
        pointToSetDists.extend([min([1] + [sphereDist(pt2, pt1) for pt2 in coords2]) for pt1 in coords1])
        averageDist = sum(pointToSetDists) / n
        return averageDist**2


class DbAccess:
    def __init__(self, entityDb):
        self._entityDb = entityDb
        self._nMax = len(self._entityDb.getroot())
        self._cacheVector = {}


    def cacheHashKey(self, subjectName, subjectType, exclude, axes):
        """prevents redundancy of calculation"""
        return (subjectName, subjectType, "".join(map(lambda (x, y): x + y, exclude)), "".join(axes))

    def getEntityVector(self, subjectName, subjectType, exclude = [], axes = []):
        """generate the vector (linking of people, places, and organizations that appear in the same feed entry) for an entity"""
        self._cacheVector.setdefault(self.cacheHashKey(subjectName, subjectType, exclude, axes), None)
        if self._cacheVector[self.cacheHashKey(subjectName, subjectType, exclude, axes)] == None:
            vector = {}
            xpathQuery = u"//entity[@type = \"%s\" and . = \"%s\"]/preceding-sibling::* | //entity[@type = \"%s\" and . = \"%s\"]/following-sibling::*" % (escapeQuotesXml(subjectType), escapeQuotesXml(subjectName), escapeQuotesXml(subjectType), escapeQuotesXml(subjectName))
            
            associatedEntities = self._entityDb.xpath(xpathQuery)
            for entity in associatedEntities:
                type = entity.get("type")
                name = entity.text
                if (axes == [] or type in axes) and not((name, type) in exclude):
                    vector.setdefault((type, name), 0)
                    vector[(type, name)] += 1. / self._nMax
                if entity.get("type") == "LOCATION" and not(entity.get("coordinates") == "") and (axes == [] or "coordinates" in axes):
                    lat, long = tuple(map(float, entity.get("coordinates").split()))
                    lat *= pi / 180.
                    long *= pi / 180.
                    vector.setdefault("coordinates", [])
                    vector["coordinates"].append((lat, long))
            self._cacheVector[self.cacheHashKey(subjectName, subjectType, exclude, axes)] = vector.copy()
            return self._cacheVector[self.cacheHashKey(subjectName, subjectType, exclude, axes)]
        else:
            return self._cacheVector[self.cacheHashKey(subjectName, subjectType, exclude, axes)]


    def simEntities(self, subjectType, subjectName1, subjectName2, axes = []):
        """Calculate the Euclidean distance between two entities of the same type."""
        vector1 = self.getEntityVector(subjectName1, subjectType, [(subjectName2, subjectType)], axes)
        vector2 = self.getEntityVector(subjectName2, subjectType, [(subjectName1, subjectType)], axes)
        d = distVectors(vector1, vector2)
        if d == 0:
            return sys.maxint
        else:
            return int(1 / d)


    def getSimsWithEntity(self, subjectName, subjectType, axes = []):
        xpathQuery = u"//entity[@type = \"%s\" and not( . = \"%s\")]" % (escapeQuotesXml(subjectType), escapeQuotesXml(subjectName))
        
        entities = set(map(lambda entity: entity.text, self._entityDb.xpath(xpathQuery)))
        return map(lambda entity: (entity, self.simEntities(subjectType, subjectName, entity, axes)), entities)

    def searchEntries(self, entities):
        """ Search feed entries for an entity. Returns only entries with items matching the search string"""
        entitiesConstraint = ""
        if len(entities) > 0:
            entitiesConstraint = u"[" + u" and ".join(map(lambda (name, type): u"head/entity[@type = \"%s\" and . = \"%s\"]" % (escapeQuotesXml(type), escapeQuotesXml(name)), entities)) + u"]"
        xpathQuery = u"//entry" + entitiesConstraint

        subDb = etree.ElementTree(etree.Element("efrDb"))
        subDb.getroot().extend(self._entityDb.xpath(xpathQuery))
        return subDb

    def getTypes(self):
        """ get entity type (person, location, or organization)"""
        xpathQuery = u"//@type[not(preceding::*/@type = .)]"
        return self._entityDb.xpath(xpathQuery)

    def getNames(self, searchType):
        """get entity name -- the specific entity (eg. Location = Denmark)"""
        xpathQuery = u"//entity[@type = \"%s\" and not(preceding::* = .)]/text()" % escapeQuotesXml(searchType)
        return self._entityDb.xpath(xpathQuery)

    def getAssociationsToEntity(self, subjectName, subjectType, axes):
        """get associations to some entity"""
        vector = self.getEntityVector(subjectName, subjectType, axes)
        return map(lambda (type, name): ((name, type), vector[(type, name)]), vector.keys())



if __name__ == "__main__":
    analysis = DbAccess(etree.parse("db.xml"))
#    print analysis.getEntityVector("India", "LOCATION")
#    print analysis.getEntityVector("India", "LOCATION", [("China", "LOCATION")])
#    print analysis.distEntities("India", "LOCATION", "Reuters", "ORGANIZATION")
#    print analysis.distEntities("India", "LOCATION", "India", "LOCATION")
    print analysis.getDists(u"Washington", u"LOCATION", ["coordinates"])




