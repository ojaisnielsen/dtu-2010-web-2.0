'''
Web 2.0 & Mobile Interaction -- Final Project
December 4, 2009

Olivier Jais-Nielsen (s090763)
Andrea Lai (s091088)

The Enhanced Feed Reader uses latent semantic analysis to identify people, organizations, and places within an RSS feed and pull in relevant additional content (Google Maps, Google Search, and recent tweets) for display.


plotmap.py allow to display a set of points on top of an image. Each point is drawn as a red circle. Overlapping points are merged into a bigger one.
'''

from math import sqrt

import ImageDraw


class Circle:
    '''
    Defines the "dot" objects.
    '''
    def __init__(self, center, baseRadius):
        self._baseRadius = baseRadius
        self._rCoef = 1
        self._c = center
		
    def radius(self):
        return self._rCoef * self._baseRadius
		
    def center(self):
        return self._c

    def coef(self):
        return self._rCoef
		
    def overlaps(self, circle):
        (x1, y1) = self.center()
        (x2, y2) = circle.center()
        d = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return d < self.radius() + self.radius()
		
    def mergeWith(self, circle):
        (x1, y1) = self.center()
        (x2, y2) = circle.center()
        self._c = (((self.coef() * x1) + (circle.coef() * x2)) / (self.coef() + circle.coef()), ((self.coef() * y1) + (circle.coef() * y2)) / (self.coef() + circle.coef()))
        self._rCoef += circle.coef()
			
	
class MapPoints:
    '''
    From a set of coordinates and a minimum radius, builds a set of dots of various radius, the bigger representing clusters of dots.
    '''
    def __init__(self, pointList, baseRadius):
        # self._baseRad = baseRad
        self._circles = []
        for point in pointList:
            self.addCircle(Circle(point, baseRadius))

    def addCircle(self, circle):
        overlap = False

        for i in range(len(self._circles)):
            if self._circles[i].overlaps(circle):
                overlap = True
                self._circles[i].mergeWith(circle)
                updatedCircle = self._circles.pop(i)
                self.addCircle(updatedCircle)
                break
        if not overlap:
            self._circles.append(circle)

    def draw(self, im):
        (w, h) = im.size
        drawer = ImageDraw.Draw(im)
        for circle in self._circles:
            (x, y) = circle.center()
            r = circle.radius()
            drawer.ellipse([(w / 2) + x - r, (h / 2) + y - r, (w / 2) + x + r, (h / 2) + y + r], fill="red")
				
	
def setCoords(im, max, coords):
    '''
    Prepare a pair of coordinates for display on an image. the maximum allowed value for each direction has to be provided.
    '''
    (mx, my) = max
    (x, y) = coords
    (w, h) = im.size
    return ((float(w) * x) / mx, -(float(h) * y) / my)
