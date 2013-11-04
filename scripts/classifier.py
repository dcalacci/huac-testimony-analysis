#!/usr/bin/env python
from collections import defaultdict
import testimonyUtils
import liwc.liwcUtils as liwcUtils

liwc = liwcUtils.LiwcDict()

class Sentence:
    """
    Sentence is a class that represents a single speech act.
    It includes utilities for extracting all entities in the speech act
    using the stanford NER package, and producing a list representation
    of a speech act where entities are individual list entries.

    Creating a new Sentence instance should be all you need - you can
    then access the new representation of the sentence by accessing the
    'sen' member.
    """
    def __init__(self, sen=""):
        self.orig_text = sen
        self.text = self.__prep_text(self.orig_text)
        self.entities = self.get_entities()
        self.words = self.parse_sentence_with_entities(self.entities)
        self.wordcount = len(self.orig_text)

    def __prep_text(self, text):
        """
        Removes all periods and commas from a given string,
        and lowercases all the words in the sentence.

        @type  text: string
        @param text: The string to prep

        @rtype:  string
        @return: The string text, with all commas and periods removed, lowered.
        """
        sen = text.replace(".", "")
        sen = sen.replace(",", "")
        sen = sen.lower()
        return sen

    def get_entities(self):
        """
        Generates the collections of entities for this sentence.
        populates 'self.original_entities' with the output from
        the stanford ner server. This dictionary is of the form:
        TYPE -> [Listof Entities]
        Also returns a list of all the entities stanford NER recognizes
        in this sentence, as a list of strings.

        @rtype:  list of strings
        @return: A list of entities that exist in this sentence.
        """
        import ner
        tagger = ner.SocketNER(host='localhost', port=8080)
        orig_ents = tagger.get_entities(self.orig_text)

        for key, val in orig_ents.items():
            orig_ents[key] = map(lambda s: self.__prep_text(s), val)
        self.original_entities = orig_ents

        # just a simple list of all the entities
        entities = [v[0] for k, v in orig_ents.items()]
        return entities

    def __parse_entities(self, sen, entities):
        """
        produces a list representation of the given sentence with each entity
        as its' own list element. Example:
        'i hate northesatern university, but i like john adams'
        ->
        ['i', 'hate', 'northeastern university', 'but', 'i', 'like', 'john adams']
        this will apply this transformation to multiple references to the same 
        entity, as well.

        @type  sen: list of strings
        @param sen: A list representation of the string to examine
        @type  entities: list of strings
        @param entities: A list of entities to check

        @rtype: list of string
        @return: a list representation of a sentence
        """
        # if we're done going through the list of entities,
        # just return the sentence array.
        if not entities:
            return sen.split()
        
        entity = entities[0]
        # if it's not in the list, go to the next entity.
        if sen.find(entity) == -1:
            print "didn't find ", entity,  " in ", sen
            return self.__parse_entities(sen, entities[1:])

        beg_index = sen.find(entity)
        end_index = sen.find(entity) + len(entity)

        a = sen[:beg_index] # string up to the entity
        b = sen[end_index:] # string after the entity

        a = self.__parse_entities(a, entities)
        a.append(entity) # add the entity inbetween the two parts
        b = self.__parse_entities(b, entities)

        return a + b

    def parse_sentence_with_entities(self, entities):
        "initial call to __parse_entities"
        return self.__parse_entities(self.text, self.entities)

    def distance_from_entity(self, word, entity):
        """
        Computes the distance from the given word to the given entity
        in this sentence.
        
        @type  word: string
        @param word: The word to compute distance for. Must be a word
                     that already exists in this sentence.
        @type  entity: string
        @param entity: The entity to compute the distance from. This must
                       be an entity that already exists in the sentence, and
                       can be obtained by getting this sentences' entities.
        @rtype:  list of number
        @return: A list of distances from entity to the given word. If entity
                 only appears once in the sentence, the list will be of length 1.
                 Otherwise, there will be a distance for each occurrence of entity
                 in this sentence.
        """

        # if an entity appears multiple times, compute multiple
        # distances for the same word.  then, compute the sentiment
        # for each instance of entity, and average it.

        def dist_from_entity_in_sen(sen, word, entity, dists):
            # print "sen: ", sen
            # print "word: ", word
            # print "entity: ", entity
            # print "dists: ", dists
            if entity in sen:
                entityindex = sen.index(entity)
                newdists = dists + [(abs(sen.index(word) - entityindex))]
                a, b = sen[:entityindex], sen[entityindex+1:]
                newsen = a + b
                #newsen = filter(lambda w: entity not in w, sen)
                #sen.remove(entity)
                return dist_from_entity_in_sen(newsen, word, entity, newdists)
            else: 
                return dists
        return dist_from_entity_in_sen(self.words, word, entity, [])

    def liwc_words(self):
        """
        Produces a list of all the words in this sentence that exist in liwc.

        @rtype: list
        @return: The intersection of all words that exist in thise sentence
                 and words that exist in liwc.
        """
        words = [word for word in self.words if len(word.split()) <= 1]
        return  [word for word in words if liwc.exists(word)]

def __isNegated(sen, word):
    """
    returns true if there's a negation word <=3 words before 'word' in 'sen',
    where 'sen' is a Sentence object.

    @type  sen: sentence
    @param sen: The sentence that word appears in.
    @type  word: string
    @param word: The word to examine

    @rtype:  boolean
    @return: True if word is negated in sen, False otherwise.
    """
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

    prevWords = __getPreviousWords(sen.words, word)
    negations = (map(lambda w: liwc.isNegation(w), prevWords))
    return any(negations)

def __getCategoriesForWord(sen, word):
    """
    Returns a list of categories that the given word belongs to
    given a sentence that contains the given word. If sen doesn't
    contain word, returns None.

    @type sen: sentence
    @param sen: The sentence to analyze.
    @type word: string
    @param word: The word to produce lwic categories for.
    
    @rtype: List of String or None
    @return: The list of lwic cateogires that word belongs to
    """
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

def __isNegWord(sen, word):
    """
    Checks if 'word' should be counted as negative in 'sen'

    @type  sen: sentence
    @param sen: The sentence to examine
    @type  word: string
    @param word: The word to check.

    @rtype: boolean
    @return: True if word is negative, False otherwise.
    """
    categories = __getCategoriesForWord(sen, word)
    if categories:
        return any(map(liwc.isNegCat, categories))
    else:
        return False

def __isPosWord(sen, word):
    """
    Checks if 'word' should be counted as positive in 'sen'

    @type  sen: sentence
    @param sen: The sentence to examine
    @type  word: string
    @param word: The word to check.

    @rtype: boolean
    @return: True if word is positive, False otherwise.
    """
    categories = __getCategoriesForWord(sen, word)
    if categories:
        return any(map(liwc.isPosCat, categories))
    else:
        return False

def __classify_speechacts(speechacts):
    """
    Creates a dictionary of [speechact] -> [feature vector]
    for each speech act in speechacts.

    @type  speechacts: list of strings
    @param speechacts: The list of speech acts to examine.

    @rtype: dict
    @return: a dict of [speech act] -> [feature vector], 
             where speech act is a string, and feature vector
             is a dict of [feature] -> [value]
    """
    classifications = {}
    for speechact in speechacts:
        speechact = Sentence(speechact)
        feature_vector = classify_sentence(speechact.words)
        classifications[speechact.words] = feature_vector
    return classifications

def __normalize(feature_vector, word_count):
    """
    Normalizes the given feature vector's values by word_count.
    """
    for feature, score in feature_vector.items():
        feature_vector[feature] = score/float(word_count)
    return feature_vector


def classify_sentence(sen):
    """
    creates a feature vector for a particular sentence, 
    using all features from liwc.
    The value for each feature is normalized by the size of the
    sentence itself. Ignores entities.
    
    @type  sen: sentence
    @param sen: The sentence to analyze

    @rtype: dict
    @return: a feature vector of [feature] -> [value]
    """
    feature_vector = defaultdict(lambda: 0)

    for word in sen.words:
        # get the associated categories in liwc
        categories = []
        if liwc.exists(word):
            categories = __getCategoriesForWord(sen, word)

            for category in categories:
                feature_vector[category] +=1
    #return feature_vector
    # simple normalizing based on length of sentence
    return __normalize(feature_vector, sen.wordcount)


def pos_neg_classify_sentence(sen):
    """
    creates a classification vector for a particular sentence,
    using positive and negative categories as features.
    The value for each feature is normalized by the size of the
    sentence itself. Ignores entities.

    @type  sen: sentence
    @param sen: The sentence to analyze
    
    @rtype dict
    @return: a feature vector of [feature] -> [value]
    """
    posNegVector = {}
    posNegVector["pos"] = 0
    posNegVector["neg"] = 0

    for word in sen.words:
        if __isPosWord(sen, word):
            posNegVector["pos"] += 1
        elif __isNegWord(sen, word):
            posNegVector["neg"] += 1
#    return posNegVector
    return __normalize(posNegVector, sen.wordcount)

def score(sen, entity):
    """
    Computes the sentiment score of 'sen' towards 'entity'

    @type  sen: sentence
    @param sen: The sentence to compute sentiment for
    @type  entity: string
    @param entity: The entity to compute 'sen's sentiment towards.

    @rtype: number
    @return: A sentiment score, from -1 to 1.
    """
    def get_sentiment_score(sen, word):
        if __isPosWord(sen, word):
           return 1
        elif __isNegWord(sen, word):
            return -1
        return 0

    def get_word_score(sen, word, entity):
        dists = sen.distance_from_entity(word, entity)
        # create list of sentiment scores for each occurrence of entity
        def normalize_by_dist(dist):
            if dist == 0: return 0
            return get_sentiment_score(sen, word)/float(dist)

        scores = map(normalize_by_dist, dists)
        # average the sentiment scores
        return sum(scores)/len(scores)
        
    scores = [get_word_score(sen, word, entity) for word in sen.words if __isPosWord(sen, word) or __isNegWord(sen, word)]
    # should it just be the sum, or should it be the average?
    score = sum(scores)
    return score

def score_all_entities(sen):
    """
    Computes the sentiment score of sen towards every entitity
    in sen.
    """
    scores = {}
    for entity in sen.entities:
        scores[entity] = score(sen, entity)
    return scores
