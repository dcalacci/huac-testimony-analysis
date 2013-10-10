#!/usr/bin/env python
from collections import defaultdict
import testimonyUtils
import liwc.liwcUtils as liwcUtils

liwc = liwcUtils.LiwcDict()


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
    class_vector = defaultdict(lambda: 0)
    sen = sen.lower().split()
    for word in sen:
        if liwc.exists(word):
            categories = liwc.getCategories(word)
            for category in categories:
                class_vector[category] += 1
    return class_vector

def classify_speechacts(speechacts):
    "converts a list of speech acts to a list of classification vectors"
    classifications = {}
    for speechact in speechacts:
        class_vector = classify_sentence(speechact)
        classifications[speechact] = class_vector
    return classifications

def classify_speech(filepath):
    sa = testimonyUtils.get_speech_acts(filepath)
    print sa
    print sa.values()
    classifications = {}
    for name in sa.keys():
        speechacts = sa[name]
        classifications[name] = classify_speechacts(speechacts)
    return classifications
