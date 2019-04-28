"""
This module provides tools to represent and manage clusters.
"""

import ImageDraw, ImageFont
verdana = ImageFont.load("verdana.pil")
"""
This is the font used to write the vectors descriptions on the diagram.
"""

class Tree:
    """
    This class represents a very general tree. A Tree can be:
        - empty
        - a leaf
        - a list of other non empty trees (its branches)
    A leaf has a label (which can be any object).
    If a Tree isn't empty and has branches, it has a label which is obtained by merging the labels of its branches.
    A Tree can be used to represent a hierarchical clustering of word vectors. In that case, a label will be composed of an id and a WordVector.
    """

    def __init__(self, labelMerger = None):
        """
        A Tree is created empty by the constructor. The optional argument "labelMerger" is the Tree's label merger : a function that can merge two labels.
        """
        self._branches = []
        self._isLeaf = False
        self._label = None
        self._boxSpacing = 15
        self.labelMerger = labelMerger
        self.fullLabelWriter = None
        self.thumbnailAccessor = None
        self._parent = None
        self._boxDim = None

    def setFullLabelWriter(self, fullLabelWriter):
        """
        This method defines the full label writer (as "fullLabelWriter") : this is a function that from a label returns a text description of the label.
        """
        self.fullLabelWriter = fullLabelWriter

    def setThumbnailAccessor(self, thumbnailAccessor):
        """
        This method defines the thumbnail accessor (as "thumbnailAccessor") : this is a function that from a label returns a picture description of the label.
        """
        self.thumbnailAccessor = thumbnailAccessor

    def mergeLabels(self, label1, label2):
        """
        This method takes two labels ("label1" and "label2") and returns the merger of these. It uses the label merger if it is defined and otherwise, if the Tree is a branch, it uses its parent Tree's "mergeLabels" method.
        """
        if self.labelMerger != None:
            return self.labelMerger(label1, label2)
        else:
            return self._parent.mergeLabels(label1, label2)

    def fullLabel(self, label):
        """
        This method takes a label "label" and returns its text description. It uses the full label writer if it is defined and otherwise, if the Tree is a branch, it uses its parent Tree's "fullLabel" method.
        """
        if self.fullLabelWriter != None:
            return self.fullLabelWriter(label)
        else:
            return self._parent.fullLabel(label)

    def getThumbnail(self, label):
        """
        This method takes a label "label" and returns its picture description. It uses the thumbnail accessor if it is defined and otherwise, if the Tree is a branch, it uses its parent Tree's "getThumbnail" method.
        """
        if self.thumbnailAccessor != None:
            return self.thumbnailAccessor(label)
        else:
            return self._parent.getThumbnail(label)

    def countBranches(self):
        """
        This method returns the number of branches a Tree has.
        """
        return len(self._branches)

    def getLabel(self):
        """
        This method returns the Tree's label.
        """
        return self._label

    def getBranchLabel(self, i):
        """
        This method returns the i-th branch's label.
        """
        return self._branches[i].getLabel()

    def setParent(self, parent):
        """
        This method gives to a Tree that is a branch a pointer to its parent Tree ("parent"), allowing it to access its parent public methods.
        """
        self._parent = parent

    def addBranch(self, branch):
        """
        This method adds the tree "branch" to the branches of the Tree.
        """
        if self._isLeaf:
            return false
        else:
            self._branches.append(branch)
            self._branches[-1].setParent(self)
            if (self._label == None):
                self._label = branch.getLabel()
            else:
                self._label = self.mergeLabels(self._label, branch.getLabel()) #

    def setLeaf(self, label):
        """
        This method transforms the Tree into a leaf with the label "label".
        """
        self._isLeaf = True
        self._label = label

    def mergeBranches(self, i, j):
        """
        This method takes the i-th and the j-th branches of the Tree and makes a new Tree containing only these branches. It replaces these two branches with the new Tree.
        """
        if self._isLeaf:
            return false
        else:
            newBranch = Tree()
            newBranch.setParent(self)
            newBranch.addBranch(self._branches[i])
            newBranch.addBranch(self._branches[j])
            del self._branches[i]
            del self._branches[j - 1]
            self._branches.append(newBranch)

    def _computeDimensions(self):
        """
        This method calculates the width and the hight of the box representation of the tree.
        """
        if self._isLeaf:
            wt, ht = verdana.getsize(self.fullLabel(self.getLabel()))
            wi = 0
            hi = 0
            thumb = self.getThumbnail(self.getLabel())
            if (thumb != False):
                wi, hi = thumb.size
            self._boxDim = (max(wt, wi), ht + hi)
            return self._boxDim
        else:
            w = self._boxSpacing
            h = self._boxSpacing
            wBMax = 0
            hBMax = 0
            for branch in self._branches:
                wB , hB = branch.boxDimensions()
                hBMax = max(hBMax, hB)
                wBMax = max(wBMax, wB)
                h += hB + self._boxSpacing
            w += wBMax + self._boxSpacing
            self._boxDim = (w, h)
            
    def boxDimensions(self):
        """
        This method returns the width and the hight of the box representation of the Tree.
        """
        if (self._boxDim == None):
            self._computeDimensions()
        return self._boxDim
        
    def drawDiagram(self, im, topLeft = (0, 0), gray = True):
        """
        This method takes a PIL image instance "im" and draws in it the Tree's box representation.
        """
        if (self._boxDim == None):
            self._computeDimensions()
        if gray:
            color = (50, 50, 50)
        else:
            color = (0, 0, 0)
        if self._isLeaf:
            imDraw = ImageDraw.Draw(im)
            imDraw.text(topLeft, self.fullLabel(self.getLabel()), font = verdana)
            w0, h0 = topLeft
            wt, ht = verdana.getsize(self.fullLabel(self.getLabel()))
            thumb = self.getThumbnail(self.getLabel())
            if (thumb != False):
                im.paste(thumb, (w0, ht + h0))
            del imDraw
        else:
            imDraw = ImageDraw.Draw(im)
            w0, h0 = topLeft
            w, h = self._boxDim
            imDraw.rectangle((w0, h0, w0 + w, h0 + h), fill = color)
            i = 0
            h0 += self._boxSpacing
            w0 += self._boxSpacing
            for branch in self._branches:
                branch.drawDiagram(im, (w0, h0), not gray)
                wB, hB = branch._boxDim
                h0 += self._boxSpacing + hB

class ClusterSet:
    """
    The class ClusterSet defines a set of clusters, each clusters containing vectors from a specified dictionnary.
    """
    def __init__(self, vectors):
        """
        An instance is created containing no clusters, only a dictionnary of vectors defined by "vectors".
        """
        self._clusterAttribution = {}
        self._centers = {}
        self._vectors = vectors
        self._hasChanged = False
        self._boxDims = {}
        self._boxSpacing = 15

    def attributeVector(self, vectID, clusterID):
        """
        This method attributes the vector which key in the dictionnary is "vectID" to the cluster that has the ID "clusterID". If the cluster doesn't exist it is created.
        """
        if (vectID in self._clusterAttribution.keys()):
            if self._clusterAttribution[vectID] != clusterID:
                self._clusterAttribution[vectID] = clusterID
                self._hasChanged = True
        else:
                self._clusterAttribution[vectID] = clusterID
                self._hasChanged = True


    def computeCentroids(self):
        """
        This method computes the centers of each cluster.
        """
        self._centers = {}
        clusterMembers = {}
        for vectID in self._vectors.keys():
            clusterID = self._clusterAttribution[vectID]
            self._centers.setdefault(clusterID, self._vectors[vectID].copy())
            clusterMembers.setdefault(clusterID, 0.)
            clusterMembers[clusterID] += 1.
            self._centers[clusterID] = ((self._centers[clusterID] * clusterMembers[clusterID]) + self._vectors[vectID]) / (clusterMembers[clusterID] + 1)

    def getCenter(self, clusterID):
        """
        This method returns the lastly computed center of the cluster which ID is "clusterID".
        """
        return self._centers[clusterID]

    def hasChanged(self):
        """
        This method returns True if the cluster attribution has changed since the last time it was executed or the creation of the object.
        """
        status = self._hasChanged
        self._hasChanged = False
        return status

    def boxDimensions(self):
        """
        This method returns the width and the hight of the box representation of the ClusterSet.
        """
        for vectID in self._clusterAttribution.keys():
            clusterID = self._clusterAttribution[vectID]
            self._boxDims.setdefault(clusterID, (self._boxSpacing, self._boxSpacing))
            w, h = self._boxDims[clusterID]
            wt, ht = verdana.getsize(self.fullLabel(vectID))
            wi = 0
            hi = 0
            thumb = self.getThumbnail(vectID)
            if (thumb != False):
                wi, hi = thumb.size
            self._boxDims[clusterID] = (max(w, wt, wi) + self._boxSpacing, h + ht + hi + self._boxSpacing)

        w = self._boxSpacing
        h = self._boxSpacing
        for clusterID in self._boxDims.keys():
            wB, hB = self._boxDims[clusterID]
            w = max(w, wB) + self._boxSpacing
            h = h + hB + self._boxSpacing
        return (w, h)


    def drawDiagram(self, im):
        """
        This method takes a PIL image instance "im" and draws in it the ClusterSet's box representation.
        """
        imDraw = ImageDraw.Draw(im)
        topLeft = (self._boxSpacing, self._boxSpacing)
        drawnBoxesTopLeft = {}
        for vectID in self._clusterAttribution.keys():
            clusterID = self._clusterAttribution[vectID]
            if not(clusterID in drawnBoxesTopLeft.keys()):
                w0, h0 = topLeft
                w, h = self._boxDims[clusterID]
                imDraw.rectangle((w0, h0, w0 + w, h0 + h), fill = (50, 50, 50))
                drawnBoxesTopLeft[clusterID] = (w0, h0 + self._boxSpacing)
                topLeft = (w0, h0 + h + self._boxSpacing)
            w0, h0 = drawnBoxesTopLeft[clusterID]
            imDraw.text((w0, h0), self.fullLabel(vectID), font = verdana)
            wt, ht = verdana.getsize(self.fullLabel(vectID))
            wi = 0
            hi = 0
            thumb = self.getThumbnail(vectID)
            if (thumb != False):
                wi, hi = thumb.size
                im.paste(thumb, (w0, h0 + ht))
            drawnBoxesTopLeft[clusterID] = (w0, h0 + ht + hi + self._boxSpacing)


    def setFullLabelWriter(self, fullLabelWriter):
        """
        This method defines the full label writer (as "fullLabelWriter") : this is a function that from a vector ID returns a text description of the vector.
        """
        self.fullLabel = fullLabelWriter

    def setThumbnailAccessor(self, thumbnailAccessor):
        """
        This method defines the thumbnail accessor (as "thumbnailAccessor") : this is a function that from a vector ID returns a picture description of the vector.
        """
        self.getThumbnail = thumbnailAccessor




