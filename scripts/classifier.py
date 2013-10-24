#!/usr/bin/env python
from collections import defaultdict
import testimonyUtils
import liwc.liwcUtils as liwcUtils

liwc = liwcUtils.LiwcDict()


def classify_phrase(phrase):
    print "not implemented!"

def __getPreviousWords(sen, word):
    """
    Returns a list of length <= 3 of words that appear before
    'word' in 'sen', where 'sen' is an array of words, and 'word'
    is a string.
    """
    index = sen.index(word)
    prevWords = sen[:index]
    if len(prevWords) > 3:
        prevWords = prevWords[1:]
    return prevWords

def __isNegated(sen, word):
    "returns true if there's a negation word before this word in sen"
    prevWords = __getPreviousWords(sen, word)
    negations = (map(lambda w: liwc.isNegation(w), prevWords))
    return any(negations)

def __isNegWord(sen, word):
    "Returns true if 'word' should be counted as negative in sen"
    categories = __getCategoriesForWord(sen, word)
    if categories:
        return any(map(liwc.isNegCat, categories))
    else:
        return False

def __isPosWord(sen, word):
    "Returns true if 'word' should be counted as negative in sen"
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

def __normalize(feature_vector, word_count):
    for feature, score in feature_vector.items():
        feature_vector[feature] = score/float(word_count)
    return feature_vector

def classify_sentence(sen):
    """
    creates a classification vector for a particular sentence, 
    using all features from liwc.
    The value for each feature is normalized by the size of the
    sentence itself. Ignores entities.
    """
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

    # simple normalizing based on length of sentence
    return __normalize(feature_vector, word_count)

def pos_neg_classify_sentence(sen):
    """
    creates a classification vector for a particular sentence,
    using positive and negative categories as features.
    The value for each feature is normalized by the size of the
    sentence itself. Ignores entities.
    """
    sen = __prep_sentence(sen)

    posNegVector = {}
    posNegVector["pos"] = 0
    posNegVector["neg"] = 0

    word_count = len(sen)
    for word in sen:
        if __isPosWord(sen, word):
            posNegVector["pos"] += 1
        elif __isNegWord(sen, word):
            posNegVector["neg"] += 1
#    return posNegVector
    return __normalize(posNegVector, word_count)

# def __start_ner_server():
#     import os
#     from subprocess import call
    
#     externals = os.path.join(os.getcwd(), 'external')
#     sner = os.path.join(externals, "stanford-ner")
# #    externals = os.path.join(os.path.dirname(__file__), 'externals')
# #    current_folder_path, current_folder_name = os.path.split(os.getcwd())

#     os.chdir(sner)

#     call('ner', '-mx1000m', '-cp', 'stanford-ner.jar', 'edu.stanford.nlp.ie.NERServer', '-loadClassifier', 'classifiers/english.muc.7class.distsim.crf.ser.gz', '-port', '8080', '-outputFormat', 'inlineXML')

def __get_entities(sen):
    "produces a dict of entities in sen from the Stanford NER parser. sen must be a string."
    import ner
    tagger = ner.SocketNER(host='localhost', port=8080)
    return tagger.get_entities(sen)

def __pos_neg_classify_sen_by_entity(sen):
    "not implemented"
    #entities = __get_entities(sen)


def classify_speech(filepath):
    sa = testimonyUtils.get_speech_acts(filepath)
    classifications = {}
    for name in sa.keys():
        speechacts = sa[name]
        classifications[name] = __classify_speechacts(speechacts)
    return classifications
