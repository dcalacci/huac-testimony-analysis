#!/usr/bin/env python
import re

def who_named_whom(filepath):
    import ner
    namedict = {}
    named_regex = re.compile("(^(\s)?[A-Z]\w+[,|\.]\s*[A-Z]\w+(?:\.)?([\s+]\w+)?)", 
                             re.MULTILINE)
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
        current_name = matches[0][0]

        print "named: ", current_name

        current_line = current_line.replace(current_name, "")
        # get all lines from current_line until the next named name.
        # could skip i to be where j is, but we can save that for later.
        named_lines = ""
        # go from current_line forward in the file
        for j in range(i+1, len(lines)):
            if named_regex.findall(lines[j]):
                break
            named_lines += lines[j]

        named_lines = current_line + named_lines# add the rest of the first line
        names = tagger.get_entities(named_lines)['PERSON']

        print "named lines for ", current_name, "are:\n", named_lines
        print "names extracted: ", names
        print "----------------------------"

        if namedict.has_key(current_name):
            namedict[current_name].append(names)
        else:
            namedict[current_name] = names
    return namedict
