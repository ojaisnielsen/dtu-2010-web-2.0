'''Web 2.0 & Mobile Interaction -- Final Project
December 4, 2009

Olivier Jais-Nielsen (s090763)
Andrea Lai (s091088)

The Enhanced Feed Reader uses latent semantic analysis to identify people, organizations, and places within an RSS feed and pull in relevant additional content (Google Maps, Google Search, and recent tweets) for display. 

Additionally, items identified as entities in the feed can be analyzed for similarity and associations within the elements -- this generates a tag cloud for easier visualization

THIS IS THE MAIN PROGRAM
'''

import sys
import webbrowser
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from lxml import etree
from lingpipe import LingPipeWarper
import feedparser
import infofinders
from infofinders import loadXpathFunctions
from dbbrowser import DbBrowser
from tools import getFullUrl, escapeQuotesXml


class EnhancedFeedReader(QMainWindow):

    def __init__(self, templatePath):
        QMainWindow.__init__(self)

        self._content = etree.ElementTree(etree.Element("content"))
        self._output = etree.ElementTree(etree.Element("html"))      
        # uses LingPipe to append entity tags to identified people, places, and organizations
        self._lingPipeWarper = LingPipeWarper("lingpipe-3.8.2")
        self._currentPage = 0
        self._efrDb = etree.ElementTree(etree.Element("efrDb"))
        self._displayedDb = self._efrDb
        self._namespace = etree.FunctionNamespace('EnhancedFeedReader')
        
        # allows methods in this class to be called from an XSL template
        loadXpathFunctions([infofinders.getRealName, infofinders.getLocationCoordinates, infofinders.getMapUrl, infofinders.getGoogleSearch, infofinders.getTweets, getFullUrl], self._namespace)
        
        # generate database
        self.addToDb = etree.XSLT(etree.parse("dbbuilder.xsl"))
        self.applyTemplate = etree.XSLT(etree.parse("template.xsl"))

        # GUI  items
        self.setWindowTitle("Enhanced Feed Reader")        
        
        menubar = self.menuBar()
        menu = menubar.addMenu("Menu")
        
        loadFeedEntry = QAction("Load feed...", self)
        menu.addAction(loadFeedEntry)
        QObject.connect(loadFeedEntry, SIGNAL("triggered()"), self.readFeed)
        
        saveFeedEntry = QAction("Save entity database...", self)
        menu.addAction(saveFeedEntry)
        QObject.connect(saveFeedEntry, SIGNAL("triggered()"), self.saveDb)
        
        loadFeedEntry = QAction("Load entity database...", self)
        menu.addAction(loadFeedEntry)
        QObject.connect(loadFeedEntry, SIGNAL("triggered()"), self.loadDb)
        
        exportPageEntry = QAction("Export current page...", self)
        menu.addAction(exportPageEntry)
        QObject.connect(exportPageEntry, SIGNAL("triggered()"), self.exportPage)        

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        layout = QVBoxLayout()
        centralWidget.setLayout(layout)
     
        buttonLayout = QHBoxLayout()
        
        previousButton = QPushButton("Previous")
        QObject.connect(previousButton, SIGNAL("clicked()"), self.previousPage)
        buttonLayout.addWidget(previousButton)

        self._feedsPerPageBox = QSpinBox()
        self._feedsPerPageBox.setValue(4)
        QObject.connect(self._feedsPerPageBox, SIGNAL("valueChanged(int)"), self.refresh)
        buttonLayout.addWidget(self._feedsPerPageBox)        
        
        nextButton = QPushButton("Next")
        QObject.connect(nextButton, SIGNAL("clicked()"), self.nextPage)
        buttonLayout.addWidget(nextButton)

        self._display = QWebView()
        self._display.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        QObject.connect(self._display, SIGNAL("linkClicked (const QUrl&)"), self.openLink)
        
        layout.addWidget(self._display)
        layout.addLayout(buttonLayout)
        
        #end GUI items

    def openLink(self, link):
        """ opens a link to one's default web browser """
        if link.scheme() == "efr":
            entities = []
            for (type, name) in  link.queryItems():
                if not unicode(name) == "":
                    entities.append((unicode(type), unicode(name)))
            dbBrowser = DbBrowser(self._efrDb, self, entities)
            dbBrowser.show()
        else:
            webbrowser.open(link.toString())

    def nextPage(self):
        """ displays the next page of RSS items. Does nothing if already on the most recent page."""
        if self._currentPage < (len(self._displayedDb.getroot()) / self._feedsPerPageBox.value()) - 1:
            self._currentPage += 1
        self.refresh()

    def previousPage(self):
        """ displays the previous page of RSS items. Does nothing if already on the oldest page."""
        if self._currentPage > 0:
            self._currentPage -= 1
        self.refresh()
        
    def setDb(self, db = None):
        if db == None:
            self._displayedDb = self._efrDb
        else:
            self._displayedDb = db
        self._currentPage = 0
        self.refresh()

    def setDisplay(self, htmlTree):
        self._display.setHtml(etree.tostring(htmlTree, encoding = "UTF-8"))

    def setDisplayUrl(self, url):
            self._display.setUrl(QUrl(url))

    def refresh(self):
        start = self._currentPage * self._feedsPerPageBox.value()
        end = (self._currentPage + 1) * self._feedsPerPageBox.value()
        self._output = self.applyTemplate(self._displayedDb, start = str(start), end = str(end))
        self._display.setHtml(etree.tostring(self._output, encoding = "UTF-8"))


    def readFeed(self):
        """reads a feed from a URL and extracts title, link, date, and summary using feedparser. It also includes a progress bar during the loading process."""
        url, ok = QInputDialog.getText(self, "Load feed", "Enter feed URL:")
        if ok:
            status = QProgressDialog("Loading enhanced feed...", "", 0, 100, self, Qt.SplashScreen)
            status.setCancelButton(None)
            status.setValue(1)
            feed = feedparser.parse(str(url))
            n = len(feed.entries)
            i = 0
            for feedEntry in feed.entries:
                status.setValue(i * 100. / n)
                self.newEntry(feedEntry.title, feedEntry.link, feedEntry.date, feedEntry.summary)
                i += 1
            status.setValue(100)
            self.refresh()


    def loadDb(self):
        """load a LingPipe parsed xml file"""
        filename = QFileDialog.getOpenFileName(self)
        if not filename == "":
            self._efrDb.parse(str(filename))
            self.refresh()

    def saveDb(self):
        """Save a LingPipe parsed file as xml"""
        filename = QFileDialog.getSaveFileName(self)
        if not filename == "":
            savedDb = open(filename, "w")
            self._efrDb.write(savedDb, encoding = "UTF-8", xml_declaration = True)
            savedDb.close()


    def exportPage(self):
        """save feed reader display (with enhanced elements) as HTML"""
        filename = QFileDialog.getSaveFileName(self)
        if not filename == "":
            savedPage = open(filename, "w")
            self._output.write(savedPage, encoding = "UTF-8")
            savedPage.close()


    def newEntry(self, title, link, date, summary):
        """create a new feed entry"""
        xpathQuery = u"count(/efrDb/entry[@link = '%s']) > 0" % link
        if not self._efrDb.xpath(xpathQuery):
            lingPipeOutput = etree.fromstring(self._lingPipeWarper.parseNamedEntities(unicode(summary), "text/html"), etree.HTMLParser())
            print title.encode("utf-8")
            entry = self.addToDb(lingPipeOutput, title = "\"%s\"" % escapeQuotesXml(title), link = "\"%s\"" % escapeQuotesXml(link), date = "\"%s\"" % escapeQuotesXml(date))
            self._efrDb.getroot().append(entry.getroot())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    # launches enhanced feed reader with the template formatting the final display
    enhancedFeedReader = EnhancedFeedReader("template.xsl")
    enhancedFeedReader.show()
    sys.exit(app.exec_())


