#!/usr/bin/env python
from collections import defaultdict
# some functions to guess likely names from mispellings. works OK.

# TODO here - check if any sequence of starting characters
# between a and b has a levenshtein distance above some
# threshold. There are many useless hits for names like
# 'sch' or 'shor' that correspond to the name 'schoenfeld'
# and it would be good to be able to recognize that.

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
    distribution for that name.
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
