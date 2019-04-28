'''
Web 2.0 & Mobile Interaction -- Final Project
December 4, 2009

Olivier Jais-Nielsen (s090763)
Andrea Lai (s091088)

The Enhanced Feed Reader uses latent semantic analysis to identify people, organizations, and places within an RSS feed and pull in relevant additional content (Google Maps, Google Search, and recent tweets) for display. 


dbbrowser.py sets up the interface for the search/database browser element
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from lxml import etree
from dbaccess import DbAccess
import plotmap
from PIL import Image
from math import pi
from tools import getFullUrl

class EntitySelector(QVBoxLayout):
    def __init__(self, parent, entity = None):
        QVBoxLayout.__init__(self)
        self._parent = parent

        self.setContentsMargins(0, 10, 0, 10)

        self._firstLine = QHBoxLayout()
        self.addLayout(self._firstLine)

        self._checkBox = QCheckBox()
        self._checkBox.setCheckState(Qt.Checked)
        self._firstLine.addWidget(self._checkBox)

        self._typeCombo = QComboBox()
        self._types = sorted(self._parent.dbAccess.getTypes())
        for type in self._types:
            self._typeCombo.addItem(type)
        self._firstLine.addWidget(self._typeCombo)
        QObject.connect(self._typeCombo, SIGNAL("currentIndexChanged (int)"), self.setNameCombo)

        self._nameCombo = QComboBox()
        self.setNameCombo()
        self._firstLine.addWidget(self._nameCombo)


        if not entity == None:
            (type, name) = entity
            self.setEntity(name, type)


        secondLine = QLabel("Display the other entities' similarities with the current, according to the following criteria.\nDisplay the entities most frequently associated with the current.")
        self.addWidget(secondLine)

        self._thirdLine = QHBoxLayout()
        self.addLayout(self._thirdLine)

        displaySimButton = QPushButton("Similarities")
        self._thirdLine.addWidget(displaySimButton)
        QObject.connect(displaySimButton, SIGNAL("clicked()"), self.displaySim)

        displayAssocButton = QPushButton("Associations")
        self._thirdLine.addWidget(displayAssocButton)
        QObject.connect(displayAssocButton, SIGNAL("clicked()"), self.displayAssoc)

        self._typeBox = []
        for type in self._types:
            self._typeBox.append(QCheckBox(type))
            self._thirdLine.addWidget(self._typeBox[-1])
        self._typeBox.append(QCheckBox("Spatial localization"))
        self._thirdLine.addWidget(self._typeBox[-1])
		
        displayLocButton = QPushButton("Display spatial localizations")
        self.addWidget(displayLocButton)
        QObject.connect(displayLocButton, SIGNAL("clicked()"), self.displayLoc)		


    def displayLoc(self):
        (name, type) = self.getEntity()
        self._parent.displayLoc(name, type)
		
    def setNameCombo(self):
        self._nameCombo.clear()
        for name in sorted(self._parent.dbAccess.getNames(self._typeCombo.currentText())):
            self._nameCombo.addItem(name)

    def getEntity(self):
        return (str(self._nameCombo.currentText()), str(self._typeCombo.currentText()))

    def setEntity(self, name, type):
        typeInd = self._typeCombo.findText(type)
        if typeInd >= 0:
            self._typeCombo.setCurrentIndex(typeInd)
            nameInd = self._nameCombo.findText(name)
            if nameInd >= 0:
                self._nameCombo.setCurrentIndex(nameInd)

    def isSelected(self):
        return self._checkBox.isChecked()

    def displaySim(self):
        searchItems = []
        types = self._types + ["coordinates"]
        for i in range(len(types)):
            if self._typeBox[i].isChecked():
                searchItems.append(types[i])
        if not searchItems == []:
            (name, type) = self.getEntity()
            self._parent.displaySim(name, type, searchItems)

    def displayAssoc(self):
        self._typeBox[-1].setCheckState(Qt.Unchecked)
        searchItems = []
        types = self._types
        for i in range(len(types)):
            if self._typeBox[i].isChecked():
                searchItems.append(types[i])
        if not searchItems == []:
            (name, type) = self.getEntity()
            self._parent.displayAssoc(name, type, searchItems)



class DbBrowser(QMainWindow):
    def __init__(self, efrDb, parent = None, entities = []):
        QMainWindow.__init__(self, parent, Qt.Tool)

        self._parent = parent

        self.dbAccess = DbAccess(efrDb)

        self.setWindowTitle("Entity database browser")

        centralArea = QScrollArea()
        centralWidget = QWidget()

        self.setCentralWidget(centralArea)

        self._layout = QVBoxLayout()
        centralWidget.setLayout(self._layout)

        self._layout.setAlignment(Qt.AlignTop)


        firstLine = QHBoxLayout()
        self._layout.addLayout(firstLine)
        searchButton = QPushButton("Find articles containing selected entities")
        QObject.connect(searchButton, SIGNAL("clicked()"), self.search)
        firstLine.addWidget(searchButton)
        

        addButton = QPushButton("Add entity")
        QObject.connect(addButton, SIGNAL("clicked()"), self.addEntitySelector)
        firstLine.addWidget(addButton)


        self._entitySelectors = []

        for entity in entities:
            self.addEntitySelector(entity)

        centralArea.setWidget(centralWidget)
        centralArea.setWidgetResizable(True)

        self._results = []
        

    def addEntitySelector(self, entity = None):
        self._entitySelectors.append(EntitySelector(self, entity))
        self._layout.insertLayout(1, self._entitySelectors[-1])


    def search(self):
        searchItems = []
        for entitySelector in self._entitySelectors:
            if entitySelector.isSelected():
                searchItems.append(entitySelector.getEntity())
        self._parent.setDb(self.dbAccess.searchEntries(searchItems))

    def closeEvent(self, event):
        self._parent.setDb()
		
    def displayLoc(self, name, type):
        try:
            vector = self.dbAccess.getEntityVector(name, type, [], ["coordinates"])
            im = Image.open("map.jpg")
            coords = map(lambda (lat, long): plotmap.setCoords(im, (2 * pi, pi), (long, lat)), vector["coordinates"])
            mapPoints = plotmap.MapPoints(coords, 20)
            mapPoints.draw(im)
            im.save("temp.jpg")
            self._parent.setDisplayUrl(getFullUrl(None, "temp.jpg"))
        except KeyError:
             self._parent.setDisplay(etree.ElementTree(etree.Element("html")))


    def displaySim(self, name, type, searchItems):
        grades = self.dbAccess.getSimsWithEntity(name, type, searchItems)
        title = "Similarity between %s and the other %ss" % (name, type)
        self.displayCloud(grades, title)

    def displayAssoc(self, name, type, searchItems):
        vector = self.dbAccess.getEntityVector(name, type, [], searchItems)
        grades = map(lambda (type, name): ("%s (%s)" % (name, type), vector[(type, name)]), vector.keys())
        title = "Entities frequently associated with %s" % name
        self.displayCloud(grades, title)

    def displayCloud(self, grades, title):
        names = map(lambda (x, y): x, grades)
        grades = map(lambda (x, y): y, grades)
        grades = map(lambda x: max(5, int((20. *x / max(grades)))), grades)
        input = etree.ElementTree(etree.Element("tagcloud"))
        for i in range(len(grades)):
            item = etree.Element("item", grade = str(grades[i]))
            item.text = names[i]
            input.getroot().append(item)
        template = etree.XSLT(etree.parse("displaytagcloud.xsl"))
        self._parent.setDisplay(template(input, title = "'%s'" % title.replace("'", "&apos;")))
		

