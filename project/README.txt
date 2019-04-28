Web 2.0 & Mobile Interaction -- Final Project
December 4, 2009

Olivier Jais-Nielsen (s090763)
Andrea Lai (s091088)

-------------------
The Enhanced Feed Reader uses latent semantic analysis to identify people, organizations, and places within an RSS feed and pull in relevant additional content (Google Maps, Google Search, and recent tweets) for display. 

Additionally, items identified as entities in the feed can be analyzed for similarity and associations within the elements -- this generates a tag cloud for easier visualization
-------------------

NOTE: In order to use this program, the folder "lingpipe-3.8.2" and all the associated files from the LingPipe download and installation must be in the same folder as "enhancedfeedreader.py"
Java must also be installed

== Included files ==
* enhancedfeedreader.py  (main program)

* dbaccess.py
* dbbrowser.py
* infofinders.py
* lingpipe.py
* plotmap.py
* tools.py

* dbbuilder.xsl
* displaytagcloud.xsl
* template.xsl

* style.css
* dynamic.js

* map.jpg

* sample xml file

== Required Python Modules ==
Run-time errors? Check to see if you have the following Python modules installed:
* feedparser
* geopy
* lxml
* PyQt4
* simplejson
* twython
* PIL