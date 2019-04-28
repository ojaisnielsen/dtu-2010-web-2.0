"""
 This module provides tools to represent and manage texts as word vectors.
"""

import re

class WordVector:
    """
    The WordVector object behaves as a dictionnary : the keys are words and the values are positive (or zero) numbers. However, a word is present among the keys only if it is associated with a value different from 0 in more than 10% and less than 50% of all the WordVector instances. Thus creating a new WordVector can change the words contained in all the WordVector instances.
    Arithmetic operations between two WordVector instances or between a WordVector and a number are possible but they return a "pseudo" WordVector : its coeficients might be negative and its creation doesn't affect the words present in the other instances.
    """

    _wordPresenceNb = {}
    _vectorsNb = 0
    _keptWords = []

    def __init__(self, wordHistogram, updateVectorType = True):
        """
        A WordVector is obtained from a word histogram "wordHistogram" which is a dictionnary associating positive  umbers to words. One can create a "pseudo" WordVector by setting the optional parameter "updateVectorType" to False.
        """
        self._wordHistogram = wordHistogram
        
        if updateVectorType:
            WordVector._vectorsNb += 1
            for word in wordHistogram.keys():
                WordVector._wordPresenceNb.setdefault(word, 0)
                WordVector._wordPresenceNb[word] += 1

            for word in WordVector._wordPresenceNb.keys():
                wordFreq = float(WordVector._wordPresenceNb[word]) / WordVector._vectorsNb
                if wordFreq > .1 and wordFreq < .5 and not(word in WordVector._keptWords):
                    WordVector._keptWords.append(word)
                elif (wordFreq < .1 or wordFreq > .5) and word in WordVector._keptWords:
                    WordVector._keptWords.remove(word)

    def __len__(self):
        """
        This method returns the dimension of the WordVector when it is considered as a dictionnary.
        """
        return len(WordVector._keptWords)

    def copy(self):
        """
        This method returns a copy as a "pseudo" WordVector.
        """
        return WordVector(self._wordHistogram.copy(), False)

    def __getitem__(self, word):
        """
        This method returns the coeficient for the key "word" of the WordVector when it is considered as a dictionary.
        """
        if (word in WordVector._keptWords and word in self._wordHistogram.keys()):
            return self._wordHistogram[word]
        elif (word in WordVector._keptWords):
            return 0
        else:
            raise IndexError

    def __iter__(self):
        """
        This method associates a WordVector with a WordVectorIterator so it can be considered as a dictionary.
        """
        return WordVectorIterator(self)

    def __add__(self, other):
        """
        This method allows addition between two WordVector instancesaor a WordVector and a number to return a "pseudo" WordVector.
        """
        if isinstance(other, WordVector):
            data = dict(zip(WordVector.words(), [self[word] + other[word] for word in WordVector.words()]))
            newVect = WordVector(data, False)
        elif isinstance(other, (int, long, float)):
            data = dict(zip(WordVector.words(), [self[word] + other for word in WordVector.words()]))
            newVect = WordVector(data, False)
        else:
            raise TypeError
        return newVect

    def __sub__(self, other):
        """
        This method allows substraction between two WordVector instances or a WordVector and a number to return a "pseudo" WordVector.
        """
        if isinstance(other, WordVector):
            data = dict(zip(WordVector.words(), [self[word] - other[word] for word in WordVector.words()]))
            newVect = WordVector(data, False)
        elif isinstance(other, (int, long, float)):
            data = dict(zip(WordVector.words(), [self[word] - other for word in WordVector.words()]))
            newVect = WordVector(data, False)
        else:
            raise TypeError
        return newVect

    def __div__(self, other):
        """
        This method allows (pointwise) division between two WordVector instances or a WordVector and a number to return a "pseudo" WordVector.
        """
        if isinstance(other, WordVector):
            data = dict(zip(WordVector.words(), [self[word] / other[word] for word in WordVector.words()]))
            newVect = WordVector(data, False)
        elif isinstance(other, (int, long, float)):
            data = dict(zip(WordVector.words(), [self[word] / other for word in WordVector.words()]))
            newVect = WordVector(data, False)
        else:
            raise TypeError
        return newVect

    def __truediv__(self, other):
        """
        This method allows (pointwise) division between two WordVector instances or a WordVector and a number to return a "pseudo" WordVector.
        """
        return self.__div__(other)

    def __mul__(self, other):
        """
        This method allows (pointwise) multiplication between two WordVector instances or a WordVector and a number to return a "pseudo" WordVector.
        """
        if isinstance(other, WordVector):
            data = dict(zip(WordVector.words(), [self[word] * other[word] for word in WordVector.words()]))
            newVect = WordVector(data, False)
        elif isinstance(other, (int, long, float)):
            data = dict(zip(WordVector.words(), [self[word] * other for word in WordVector.words()]))
            newVect = WordVector(data, False)
        else:
            raise TypeError
        return newVect

    @staticmethod
    def words():
        """
        This method returns the words that are (currently) present in all the WordVector instances.
        """
        return WordVector._keptWords


class WordVectorIterator:
    """
    This class is used internally to iterate through WordVector objects so they can be considered has dictionarries.
    """
    def __init__(self, vect):
        self._wordVector = vect
        self._currentWordInd = 0

    def __iter__(self):
        return self

    def next(self):
        if self._currentWordInd >= len(self._wordVector):
            raise StopIteration
        else:
            word = WordVector.words()[self._currentWordInd]
            self._currentWordInd += 1
            return self._wordVector[word]


def wordHistogramFromTextList(textList):
    """
    This function returns a word histogram from a list of texts "textList".
    """
    words = {}
    for text in textList:
        text = re.compile("[0-9]+", re.UNICODE).sub("", text)
        for word in re.compile("\W+", re.UNICODE).split(text):
            word = word.lower()
            if not(word == ""):
                words.setdefault(word, 0)
                words[word] += 1
    return words
