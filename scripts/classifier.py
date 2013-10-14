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
    prevWords = __getPreviousWords(sen, word)
    print "previous words: ", prevWords
    negations = (map(lambda w: liwc.isNegation(w), prevWords))
    print "negations? ", negations
    return any(negations)

def __getCategoriesForWord(sen, word):
    "get the categories this word belongs to"
    if liwc.exists(word):
        categories = liwc.getCategories(word)

        # if the word is negated and has + or - sentiment, replace
        # any categories that have opposites
        if liwc.isPosNegWord(word) and __isNegated(sen, word):
            print "it's positive or negative and it's negated"

            def replaceCategory(c):
                opposite = liwc.getOppositeCategory(c)
                if opposite:
                    return opposite
                else: 
                    return c

            categories = map(replaceCategory, categories)
        return categories
    return None


def classify_sentence(sen):
    "returns a classification vector for a particular sentence"
    feature_vector = defaultdict(lambda: 0)
    # remove certain types of punctuation so we can match
    # words in liwc
    sen = sen.replace(".", "")
    sen = sen.replace(",", "")
    sen = sen.lower().split()

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

def __classify_speechacts(speechacts):
    "converts a list of speech acts to a list of classification vectors"
    classifications = {}
    for speechact in speechacts:
        feature_vector = classify_sentence(speechact)
        classifications[speechact] = feature_vector
    return classifications


def classify_speech(filepath):
    sa = testimonyUtils.get_speech_acts(filepath)
    classifications = {}
    for name in sa.keys():
        speechacts = sa[name]
        classifications[name] = __classify_speechacts(speechacts)
    return classifications
