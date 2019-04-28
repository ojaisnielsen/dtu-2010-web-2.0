"""
This module defines the actual algorithms used for clustering.
"""

from IMDbTools import IMDbInterface, getIMDbTop250
from WordsTools import WordVector, wordHistogramFromTextList
from ClustersTools import Tree, ClusterSet
from math import sqrt, exp
from types import ListType
import Image

def similarity(vect1, vect2, measure = "pearson"):
    """
    This function returns the similarity between the two vectors "vect1 and "vect2". The optional third argument, which is by default "pearson" specifies the kind of similarity. The other possibilies are "tanimoto" and "inverse euclidian"
    """
    s = 0.
    if measure == "pearson":
        m1 = float(sum(vect1)) / len(vect1)
        m2 = float(sum(vect2)) / len(vect2)
        n1 = 0.
        n2 = 0.
        for word in WordVector.words():
            n1 += (vect1[word] - m1)**2
            n2 += (vect2[word] - m2)**2
            s += (vect1[word] - m1) * (vect2[word] - m2)
        n1 = sqrt(n1)
        n2 = sqrt(n2)
        if (n1 * n2 != 0):
            s /= n1 * n2
        else:
            s = 1.

    elif measure == "tanimoto":
        n1 = 0.
        n2 = 0.
        for word in WordVector.words():
            n1 += vect1[word]**2
            n2 += vect2[word]**2
            s += vect1[word] * vect2[word]
        if n1 + n2 - s != 0:
            s /= n1 + n2 - s
        else:
            s = 1.

    elif measure == "euclidian inverse":
        for word in WordVector.words():
            s += (vect1[word] - vect2[word])**2
        s = sqrt(s)
        if s == 0:
            s = 1.
        else:
            s = exp(-s)
        
    return s


def mergeWordVectorsLabels(label1, label2):
    """
    This function returns the merger of two WordVector labels "label1" and "label2". A WordVector label is a couple of an ID and a WordVector. The merged label is a couple of a list containing the input IDs or a concatenation if one of these IDs was already a list, and the "pseudo" WordVector obtained as the arithmetic average of the two input WordVector instances.
    """
    id1, vect1 = label1
    id2, vect2 = label2
    if not isinstance(id1, ListType):
        id1 = [id1]
    if not isinstance(id2, ListType):
        id2 = [id2]
        
    wordHist = {}
    for word in WordVector.words():
        wordHist[word] = (vect1[word] + vect2[word]) / 2.

    return (id1 + id2, WordVector(wordHist, False))
        

def hierarchicalCluster(vectors, simMeasure):
    """
    This function computes the hierarchical clustering from the WordVector instances in the "vectors" list using the similarity measure "simMeasure". It returns a Tree with WordVector labels.
    """

    # We create an empty Tree with the appropriate label merger. It will act has the top tree.
    tree = Tree(mergeWordVectorsLabels)
    vectPairSimilarities = {}

    # For each vector, we create a leaf with the appropriate label and we add it as a branch of the top Tree.
    # These are the initial clusters.
    for vectID in vectors.keys():
        branch = Tree();
        branch.setLeaf((vectID, vectors[vectID]))
        tree.addBranch(branch)

    # While there is more than one cluster at the top level, we iterate.
    while tree.countBranches() > 1:

        # We find the highest similarity among the cluster pairs (we store the similarities in vectPairSimilarities in order to avoid calculating several times the same thing) 
        maxSimilarity = -1;
        for i in range(tree.countBranches()):
            vectIID, vectI = tree.getBranchLabel(i)

            for j in range(i + 1, tree.countBranches()):
                vectJID, vectJ = tree.getBranchLabel(j)
                sim = None
                vectIID = str(vectIID)
                vectJID = str(vectJID)
                if (vectIID, vectJID) in vectPairSimilarities.keys():
                    sim = vectPairSimilarities[(vectIID, vectJID)]
                elif (vectJID, vectIID) in vectPairSimilarities.keys():
                    sim = vectPairSimilarities[(vectJID, vectIID)]
                else:
                    sim = simMeasure(vectJ, vectI)
                vectPairSimilarities[(vectIID, vectJID)] = sim
                vectPairSimilarities[(vectJID, vectIID)] = sim
                if sim > maxSimilarity:
                    maxSimilarity = sim
                    bestI = i
                    bestJ = j
                    bestVectIID = vectIID
                    bestVectJID = vectJID

        # We merge the clusters of the corresponding pair
        tree.mergeBranches(bestI, bestJ)
        del vectPairSimilarities[(bestVectIID, bestVectJID)]
        del vectPairSimilarities[(bestVectJID, bestVectIID)]

    # Once there is only one cluster at the top level, we return it
    return tree


def kMeansClustering(vectors, simMeasure, k):
    """
    This function computes the k-mean clustering from the WordVector instances  in the "vectors" list using the similarity measure "simMeasure" and "k". It returns a ClusterSet containing WordVector instances.
    """

    # We create a ClusterSet with no clusters and with the set of vectors
    clusters = ClusterSet(vectors)

    # We create k clusters and fill them arbitrarily : the i-th vector belongs to the (i mod[k])-th cluster.
    i = 0
    for vectID in vectors.keys():
        clusters.attributeVector(vectID, i % k)
        i += 1

    # While the composition of the cluster differs from the previous iteration, we iterate.
    while clusters.hasChanged():

        # We compute the centroid of each cluster for their current composition.
        clusters.computeCentroids()

        # For each vector :
        for vectID in vectors.keys():

            # We find the highest similarity between the vector and a centroid
            maxSimilarity = -1
            for clusterID in range(k):
                currentSim = simMeasure(vectors[vectID], clusters.getCenter(clusterID))
                if currentSim >= maxSimilarity:
                    maxSimilarity = currentSim
                    bestClusterID = clusterID

            # We assign the vector to the cluster corresponding to the found centroid
            clusters.attributeVector(vectID, bestClusterID)

    # Once the composition of the clusters stops changing, we return the ClusterSet
    return clusters


if __name__ == "__main__":
    """
    Example
    """

    # We create an interface with IMDb
    interface = IMDbInterface("data.db")

    # We get the IMDb movie IDs corresponding to the Top 250
    movieIDs = getIMDbTop250()

    # We prepare dictionaries intended to contain, for each movie ID, an IMDb movie object and a WordVector
    movies = {}
    wordVectors = {}

    # For each movie ID
    for i in range(0, 50):
        id = movieIDs[i]

        # We get the IMDb movie object
        movies[id] = interface.getMovie(id)

        # We select the texts concerning the movie that we want to use
        list = [movies[id]["canonical title"]] + movies[id]["akas"] + movies[id]["genres"] + movies[id]["plot"]

        # We remove the annotations from these texts : they can be in a text, after a double colon
        list = map (lambda text: text.split("::")[0], list)

        # We compute a word histogram from the texts and a WordVector from it
        wordVectors[id] = WordVector(wordHistogramFromTextList(list))


    ## HIERARCHICAL CLUSTERING

    # We create a PIL image object intended to contain the box diagram of the hierarchical clustering
    im = Image.new("RGB", (0, 0), (255, 255, 255))

    # We compute the clusters for the choosen similarity measure
    clusters = hierarchicalCluster(wordVectors, lambda vect1, vect2: similarity(vect1, vect2, "euclidian inverse"))

    # We define an appropriate full label writer : it displays the cannonical title, the year and the rating of the corresponding movie
    clusters.setFullLabelWriter(lambda (vectID, vect): (u"%s (Year : %i Rating : %i)" % (movies[vectID]["canonical title"], movies[vectID]["year"], movies[vectID]["rating"])).encode("utf-8"))

    # We define an appropriate thumbnail accessor : it displays the corresponding movie's thumbnail
    clusters.setThumbnailAccessor(lambda (vectID, vect): interface.getThumbnail(vectID))

    # We resize the image to the appropriate size, we draw the diagram and we save the image
    im = im.resize(clusters.boxDimensions())
    clusters.drawDiagram(im)
    im.save("hierarchical_eucl.jpg")


    ## K-MEANS CLUSTERING

    # We create a PIL image object intended to contain the box diagram of the hierarchical clustering
    im = Image.new("RGB", (0, 0), (255, 255, 255))

    # We compute the clusters for the choosen similarity measure and the choosen k (here 6)
    clusters = kMeansClustering(wordVectors, lambda vect1, vect2: similarity(vect1, vect2, "euclidian inverse"), 6)


    # We define an appropriate full label writer : it displays the cannonical title, the year and the rating of the corresponding movie
    clusters.setFullLabelWriter(lambda vectID: (u"%s (Year : %i Rating : %i)" % (movies[vectID]["canonical title"], movies[vectID]["year"], movies[vectID]["rating"])).encode("utf-8"))

    # We define an appropriate thumbnail accessor : it displays the corresponding movie's thumbnail
    clusters.setThumbnailAccessor(interface.getThumbnail)

    # We resize the image to the appropriate size, we draw the diagram and we save the image
    im = im.resize(clusters.boxDimensions())
    clusters.drawDiagram(im)
    im.save("k-means_eucl.jpg")


