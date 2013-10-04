#!/usr/bin/env python
import testimonyUtils



liwc_wordmap = {}
liwc_loc = "/Users/dan/attic/tools/nlp/sentiment/liwc/LIWC_Features.txt"

def parse_liwc(filepath=liwc_loc):
    "parses the liwc data into a hash of (words) -> classification"
    liwc_file = open(filepath, 'r')
    
    for line in liwc_file:
        line = line.split(", ")
        category, words = line[0], line[1:]
        for word in words:
            liwc_wordmap[word] = category

def match(liwc, word):
    "returns true if the given word matches a liwc word"
    if word[-1] == "*":
        return word.startswith(liwc[:-1])
    else:
        return word == liwc

# THIS DOESN'T WORK
# Words have several different categories.
# jesus christ dan.
def classify_sentence(sen):
    "returns a classification vector for a particular sentence"
    class_vector = {}
    sen = sen.split()
    for word in sen:
        for liwc_word in liwc_wordmap:
            print "liwc word: ", liwc_word
            if match(liwc_word, word):
                print "MATCHED"
                category = liwc_wordmap[liwc_word]
                print 'category: ', category
                if class_vector.has_key(category):
                    class_vector[category] += 1
                else: 
                    class_vector[category] = 1
    return class_vector

def classify_speechacts(speechacts):
    "converts a list of speech acts to a list of classification vectors"
    classifications = {}
    for speechact in speechacts:
        class_vector = classify_sentence(speechact)
        classifications[speechact] = class_vector
    return classifications

def classify_speech(filepath):
    parse_liwc()
    sa = testimonyUtils.get_speech_acts(filepath)
    print sa
    print sa.values()
    classifications = {}
    for name in sa.keys():
        speechacts = sa[name]
        classifications[name] = classify_speechacts(speechacts)
    return classifications
