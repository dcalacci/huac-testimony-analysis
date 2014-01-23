#!/usr/bin/env python
import lexicons.lexiconUtils as sentimentUtils
from corenlp_utils import *
liwc = sentimentUtils.LiwcDict()

def is_negated(w, sen):
    """
    sen is an annotated sentence object, word is the annotated word from sen.
    uses negation information from the annotated sentence.
    """
    wordindex = sen['words'].index(w) + 1
    dependencies = sen['indexeddependencies']
    for dependency in dependencies:
        if dependency[0] == 'neg':
            # words and indices are separated by a hyphen
            words_and_indices = map(lambda w: w.split("-"), dependency[1:])
            # if the word and index are the same, it's negated.
            for word, index in words_and_indices:
                if word == w[0] and int(index) == wordindex:
                    return True
    return False

def categories_for_word(w, sen):
    "grabs all applicable categories for the given word"
    word_text = w[1]['Lemma']
    if liwc.exists(word_text):
        categories = liwc.getCategories(word_text)
        
        if (liwc.isPosWord(word_text) or liwc.isNegWord(word_text)) and is_negated(w, sen):
            def replace_category(c):
                opposite = liwc.getOppositeCategory(c)
                if opposite:
                    return opposite
                else:
                    return c
            categories = map(replace_category, categories)
        return categories
    return None


def is_neg_word(w, sen):
    categories = categories_for_word(w, sen)
    if categories:
        return any(map(liwc.isNegCat, categories))
    else:
        return False

def is_pos_word(w, sen):
    categories = categories_for_word(w, sen)
    if categories:
        return any(map(liwc.isPosCat, categories))
    else:
        return False

def sentiment_score_for_word(w, sen):
    score = 0
    if is_pos_word(w, sen):
        score = 1
    elif is_neg_word(w, sen):
        score = -1
    return score

def score_of_word_towards_index(w, index, sen):
    wordlist = sen['words']
    word_index = wordlist.index(w)
    distance = min(map(lambda i: abs(i - word_index), [index[0], index[1]-1]))
    sentiment_score = sentiment_score_for_word(w, sen)
    score = sentiment_score/float(distance) # normalize
    return score


def sentiment_towards_all_entities_in_speechact(sen_dict):
    entities_and_refs = windices_of_named_entities_and_references(sen_dict)
    entities_scores = {}
    for entity, refs in entities_and_refs.items():
        scores = []
        for ref in refs:
            sen = sen_dict['sentences'][ref[0]]
            sen_score = sen_score_towards_index(ref[1:], sen)
            scores.append(sen_score)
        entities_scores[entity] = sum(scores)
    return entities_scores
