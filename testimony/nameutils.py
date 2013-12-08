#!/usr/bin/env python
from collections import defaultdict
# some functions to guess likely names from mispellings. works OK.

# TODO here - check if any sequence of starting characters
# between a and b has a levenshtein distance above some
# threshold. There are many useless hits for names like
# 'sch' or 'shor' that correspond to the name 'schoenfeld'
# and it would be good to be able to recognize that.


# code for 'who named whom' graph using fuzzy matching, which
# incorporates lower distances for strings with distinct
# substrings.


def most_likely_name(name, dist):
    """
    Computes the most likely *correct* name from the given `name`, using 
    the distribution `dist`
    """
    maybes = dict((k, v) for k, v in dist.items() if are_close_tokens(name, k))
    best = max(maybes.items(), key=lambda p: p[1])
    return best[0]

def name_distribution_with_tokens(names):
    """
    creates a distribution based on the occurrences of names in the given
    'who-named-whom' graph.
    """
    import itertools
    dist = defaultdict(lambda: 0)
    all_names = []
    for k, v in names.items():
        all_names.append(k)
        
        # flattening lists of strings
        v1 = [([x] if isinstance(x,basestring) else x) for x in v]
        v = list(itertools.chain(*v1))
        all_names.extend(v)

    for name in all_names:
        dist[name.lower()] += 1

    for name, val in dist.items():
        dist[name] = float(val)/len(dist.keys())
    return dist

def are_close_tokens(a,b):
    "returns true if the two strings are similar using fuzzy matching"
    return (fuzzy_substring(a.lower(), b.lower()) < 3) or \
        (fuzzy_substring(b.lower(), a.lower()) < 3)

# use this to find the distance from one name to another.
def fuzzy_substring(needle, haystack):
    "taken from: http://ginstrom.com/scribbles/2007/12/01/fuzzy-substring-matching-with-levenshtein-distance-in-python/"
    """Calculates the fuzzy match of needle in haystack,
    using a modified version of the Levenshtein distance
    algorithm.
    The function is modified from the levenshtein function
    in the bktree module by Adam Hupp"""
    m, n = len(needle), len(haystack)

    # base cases
    if m == 1:
        return not needle in haystack
    if not n:
        return m

    row1 = [0] * (n+1)
    for i in range(0,m):
        row2 = [i+1]
        for j in range(0,n):
            cost = ( needle[i] != haystack[j] )

            row2.append( min(row1[j+1]+1, # deletion
                               row2[j]+1, #insertion
                               row1[j]+cost) #substitution
                           )
        row1 = row2
    return min(row1)



# code for initial transcripts using levenshtein distance

def are_close( a, b):
    "returns true if the levenshtein ratio between a and b is greater than 0.6"
    import Levenshtein
    ratio = Levenshtein.ratio(a.lower(), b.lower())
    return ratio > 0.6

def has_similar(s, names):
    "returns a name of a similar name if it exists. None otherwise."
    for name in names:
        if are_close(name, s):
            return name.lower()
    return None

def name_distribution_from_matches(matches):
        """computes a dict of name->% for all speech acts. 
        used to guess likely names from mispellings
        """
        dist = defaultdict(lambda: 0)

        total = len(matches)
        for match in matches:
            dist[match[0].lower()] += 1

            # prefer names in all caps
            if match[0].isupper():
                dist[match[0].lower()] += 10
                total += 10
        for key in dist.keys():
            dist[key] = dist[key]/float(total)
        return dist

def name_distribution_from_dict(d):
    """ computes a dict of name -> % for all speech acts
    in the given dictionary. Expects that the given dict
    is of the form 'Name -> List of Speech Acts'. It determines
    the distribution by looking at the number of characters 
    attributed to particular names in the speechact dict. The more
    characters a name has associated with it, the higher the
    score for that name.
    """
    def get_number_chars(los):
        "returns the number of characters in the given list of strings"
        res = 0
        for s in los:
            res += len(s)
        return res

    dist = dict((k, get_number_chars(v)) for (k, v) in d.items())
    total = 0
    print dist
    for k, v in dist.items():
        total += v

    return dict((k, v/float(total)) for (k, v) in dist.items())

def find_likely_name(name, dist):
    "returns the most likely name given the a distribution of names"
    maybes = dict((k, v) for k, v in dist.items() if are_close(name.lower(), 
                                                               k.lower()))
    best = max(maybes.items(), key=lambda p: p[1])
    return best[0]


