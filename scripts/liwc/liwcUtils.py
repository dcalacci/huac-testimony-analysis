#/usr/bin/env python
from liwc.config import liwc_dir
import os
catfile = os.path.join(liwc_dir, "catgories.txt")
featurefile = os.path.join(liwc_dir, "features.txt")
class LiwcDict:
    def __init__(self, filepath=featurefile):
        """
        l is either '', '*', or the letter this dict corresponds to.
        """
        self.filepath = filepath
        self.wordmap = {}
        self.__parseFeatureFile()
        self.pos = ["Posemo"]
        self.neg = ["Negemo", "Anx", "Anger", "Sad"]
        
    def __parseFeatureFile(self):
        "parses the feature file, populating the wordmap"
        with open(self.filepath) as featurefile:
            for line in featurefile.readlines():
                line = line.split(", ")
                category, words = line[0], line[1:]
                for word in words:
                    if self.wordmap.has_key(word):
                        self.wordmap[word].append(category)
                    else:
                        self.wordmap[word] = [category]

    def __matchesLiwcWord(self, liwc, word):
        "returns true if the given word matches the given liwc word"
        if liwc[-1] == "*":
            return word.startswith(liwc[:-1])
        else:
            return word == liwc

    def exists(self, word):
        "returns true if the given word is measured in liwc"
        for liwcWord in self.wordmap.keys():
            if self.__matchesLiwcWord(liwcWord, word):
                return True
        return False

    def getCategories(self, word):
        "returns the list of liwc categories the given word is in"
        for liwcWord in self.wordmap.keys():
            if self.__matchesLiwcWord(liwcWord, word):
                return self.wordmap[liwcWord]
        return None


    def isPosNegWord(self, word):
        "returns true if the word is a positive or negative word"
        posNegCats = self.pos + self.neg
        categories = self.getCategories(word)
        if posNegCats:
            return any(c in posNegCats for c in categories)
        else:
            return []
        

    def positiveWords(self):
        "returns a list of positive-associated words from liwc"
        poswords = []
        for word, categories in self.wordmap:
            if any(p in categories for p in self.pos):
                poswords.append(word)
        return poswords

    def negativeWords(self):
        "returns a list of negative-associated words from liwc"
        negwords = []
        for word, categories in self.wordmap:
            if any(n in categories for n in self.neg):
                negwords.append(word)
        return negwords

    def getOppositeCategory(self, category):
        "returns the 'negated' or 'opposite' category of the given category"
        opps = {}
        opps["Posemo"] = "Negemo"
        opps["Negemo"] = "Posemo"

        
        if opps.has_key(category):
            return opps[category]
        else:
            return None
        
    def isNegation(self, word):
        "returns true if the given word is a negation word"
        cats = self.getCategories(word)
        if cats:
            return 'Negate' in cats
        return None
