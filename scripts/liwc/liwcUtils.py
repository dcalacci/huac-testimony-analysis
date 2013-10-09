#/usr/bin/env python
import os
liwc_folder = os.path.join(os.path.abspath("."), "liwcdict")
catfile = os.path.join(liwc_folder, "catgories.txt")
featurefile = os.path.join(liwc_folder, "features.txt")
class LiwcDict:
    def __init__(self, filepath=featurefile):
        """
        l is either '', '*', or the letter this dict corresponds to.
        """
        self.filepath = filepath
        self.wordmap = {}
        self.__parseFeatureFile()
        
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

    def getWordmap(self):
        print self.wordmap

    
    def __matchesLiwcWord(self, liwc, word):
        "returns true if the given word matches the given liwc word"
        if word[-1] == "*":
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

    def isNegation(self, word):
        "returns true if the given word is a negation word"
        return 'Negate' in self.getLiwcCategories(word)
