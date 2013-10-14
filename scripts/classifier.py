#!/usr/bin/env python
from collections import defaultdict
import testimonyUtils
import liwc.liwcUtils as liwcUtils

liwc = liwcUtils.LiwcDict()


def classify_phrase(phrase):
    print "not implemented!"

def __getPreviousWords(sen, word):
#    sen.split() 
    index = sen.index(word)
    prevWords = sen[:index]
    if len(prevWords) > 3:
        prevWords = prevWords[2:]
    return prevWords

def __isNegated(sen, word):
    "returns true if there's a negation word before this word"
    prevWords = __getPreviousWords(sen, word)
    negations = (map(lambda w: liwc.isNegation(w), prevWords))
    return any(negations)

def __isNegWord(sen, word):
    categories = __getCategoriesForWord(sen, word)
    if categories:
        return any(map(liwc.isNegCat, categories))
    else:
        return False

def __isPosWord(sen, word):
    categories = __getCategoriesForWord(sen, word)
    if categories:
        return any(map(liwc.isPosCat, categories))
    else:
        return False

def __getCategoriesForWord(sen, word):
    "get the categories this word belongs to"
    if liwc.exists(word):
        categories = liwc.getCategories(word)

        # if the word is negated and has + or - sentiment, replace
        # any categories that have opposites
        if (liwc.isPosWord(word) or liwc.isNegWord(word)) and __isNegated(sen, word):
            def replaceCategory(c):
                opposite = liwc.getOppositeCategory(c)
                if opposite:
                    return opposite
                else: 
                    return c

            categories = map(replaceCategory, categories)
        return categories
    return None

def __classify_speechacts(speechacts):
    "converts a list of speech acts to a list of classification vectors"
    classifications = {}
    for speechact in speechacts:
        feature_vector = classify_sentence(speechact)
        classifications[speechact] = feature_vector
    return classifications

def __prep_sentence(sen):
    sen = sen.replace(".", "")
    sen = sen.replace(",", "")
    sen = sen.lower().split()
    return sen




def classify_sentence(sen):
    "returns a classification vector for a particular sentence"
    feature_vector = defaultdict(lambda: 0)
    # remove certain types of punctuation so we can match
    # words in liwc
    sen = __prep_sentence(sen)

    word_count = len(sen)
    for word in sen:
        # get the associated categories in liwc
        categories = []
        if liwc.exists(word):
            categories = __getCategoriesForWord(sen, word)

            for category in categories:
                feature_vector[category] +=1
    # # normalize feature vector
    # for feature, score in feature_vector.iteritems():
    #     feature_vector[feature] = score./word_count

    return feature_vector

def pos_neg_classify_sentence(sen):
    "returns a pos/neg feature vector"
    sen = __prep_sentence(sen)

    posNegVector = {}
    posNegVector["pos"] = 0
    posNegVector["neg"] = 0

    for word in sen:
        if __isPosWord(sen, word):
            posNegVector["pos"] += 1
        elif __isNegWord(sen, word):
            posNegVector["neg"] += 1
    return posNegVector

    # features = classify_sentence(sen)
    # for f in features:
    #     if liwc.isPosCat(f):
    #         posNegVector["pos"] += 1
    #     elif liwc.isNegCat(f):
    #         posNegVector["neg"] += 1

    # return posNegVector

def classify_speech(filepath):
    sa = testimonyUtils.get_speech_acts(filepath)
    classifications = {}
    for name in sa.keys():
        speechacts = sa[name]
        classifications[name] = __classify_speechacts(speechacts)
    return classifications
