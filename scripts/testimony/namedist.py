#!/usr/bin/env python
# some functions to guess likely names from mispellings. works OK.


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

def name_distribution(matches):
        """computes a dict of name->% for all speech acts. 
        used to guess likely names from mispellings
        """
        import collections
        dist = collections.defaultdict(lambda: 0)

        total = len(matches)
        print total
        for match in matches:
            dist[match[0].lower()] += 1

            # prefer names in all caps
            if match[0].isupper():
                dist[match[0].lower()] += 10
                total += 10
        for key in dist.keys():
            dist[key] = dist[key]/float(total)
        return dist

def find_likely_name(name, dist):
    "returns the most likely name given the a distribution of names"
    maybes = dict((k, v) for k, v in dist.items() if are_close(name.lower(), 
                                                               k.lower()))
    best = max(maybes.items(), key=lambda p: p[1])
    return best[0]
