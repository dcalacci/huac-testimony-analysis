#!/usr/bin/env python
import re
import time
import ner
import namedist
from collections import defaultdict

#d2 = dict((k, map(lambda n: " ".join(n.split()), v)) for (k,v) in d2.items())

def clean_whitespace(name):
    return " ".join(name.split())

def nametrans(name):
    curname = name.split(",")
    if len(curname) < 2:
        print "  Period?"
        curname = name.split(".")
    print curname
    last, first = curname[0], curname[1]
    current_name = first + " " + last
    current_name = clean_whitespace(current_name)
    return current_name

def who_named_whom(filepath):
    namedict = {}
    named_regex = re.compile("(^(\s)?[A-Z]\w+[,|\.]\s*[A-Z]\w+(?:\s*[A-Z]\.)?([\s+]\w+)?)(\s*\((.*)\))?",
                             re.MULTILINE)
    not_all_caps_regex = re.compile("([a-z])")
    testimony_identifying_regex = re.compile("Testimony identifying")
    tagger = ner.SocketNER(host='localhost', port=8080)

    f = open(filepath, "r")
    lines = f.readlines()

    for i in range(len(lines)):
        current_line = lines[i]
        current_name = ""
        matches = named_regex.findall(current_line)

        # if we don't have a named line, we don't care.
        if not matches:
            continue
        orig_name = matches[0][0]
        current_name = nametrans(orig_name) # normal First Last format

        # # sometimes the regex confused locations for people
        # # the name is separated by a comma/period. NER works well for names
        # # in normal order (not with commas/periods)
        # name = current_name.split(",")
        # if len(name) < 2:
        #     name = current_name.split(".")

        # last, first = name[0], name[1]
        # current_name = first + " " + last
        # entities = tagger.get_entities(current_name)
        # if entities.has_key('LOCATION'):
        #     continue

        print "named: ", current_name

        current_line = current_line.replace(orig_name, "")

        # remove anything in parens (...) on same line as name.
        # they are usually aliases.
        reg = re.compile("\(.*\)")
        current_line = re.sub(reg, "", current_line)
        
        # get all lines from current_line until the next named name.
        # could skip i to be where j is, but we can save that for later.
        named_lines = ""
        # go from current_line forward in the file
        for j in range(i+1, len(lines)):
            if named_regex.findall(lines[j]): 
                break
            if not not_all_caps_regex.findall(lines[j]):
                break
            if testimony_identifying_regex.findall(lines[j]):
                break
            named_lines += lines[j]

        named_lines = current_line + named_lines # add the rest of the first line
        

        named_lines = named_lines.replace("\n", "")
        print "named lines for ", current_name, "are:\n", named_lines
        got_result = None
        while got_result == None:
            try:
                entities = tagger.get_entities(named_lines)
                got_result = True
            except:
                pass
                
        # get the names!
        print entities
        if not entities.has_key('PERSON'):
            continue
        names = entities['PERSON']
        names = map(clean_whitespace, names)

        # all real names are at least two tokens long.
        names = filter(lambda n: len(n.split()) > 1, names)

        # if this key doesn't have any real names associated with it, skip.
        if not names:
            continue

        print "names extracted: ", names
        print "----------------------------"

        if namedict.has_key(current_name):
            namedict[current_name].append(names)
        else:
            namedict[current_name] = names
    return namedict


def name_distribution_with_tokens(names):
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

def most_likely_name(name, dist):
    def close(n1, n2):
        return (namedist.fuzzy_substring(n1.lower(), n2.lower()) < 3) or \
            (namedist.fuzzy_substring(n2.lower(), n1.lower()) < 3)
    maybes = dict((k, v) for k, v in dist.items() if close(name, k))
    best = max(maybes.items(), key=lambda p: p[1])
    return best[0]


def test_ner():
    a = range(1, 30)
    tagger = ner.HttpNER(host='localhost', port=8080)
    for num in a:
        entities = tagger.get_entities(str(num))
        print "entities", entities
        print "call number: ", num
        time.sleep(.5)
