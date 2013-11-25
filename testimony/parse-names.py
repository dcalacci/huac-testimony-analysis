#!/usr/bin/env python
import re
import os
import time
import ner
import subprocess


def who_named_whom(filepath):
#    os.chdir('../external/')
#    print os.getcwd()
#    ner_server_process = subprocess.Popen('./ner.sh')
 #   os.chdir('../testimony/')
#    ner_server_process = subprocess.Popen('../external/ner.sh')
    counter = 0
    namedict = {}
    named_regex = re.compile("(^(\s)?[A-Z]\w+[,|\.]\s*[A-Z]\w+(?:\.)?([\s+]\w+)?)", 
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
        current_name = matches[0][0]

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

        current_line = current_line.replace(current_name, "")
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

        named_lines = current_line + named_lines# add the rest of the first line
        got_result = None
        while got_result == None:
            try:
                entities = tagger.get_entities(named_lines)
                got_result = True
            except:
 #                os.kill(ner_server_process.pid, 0)
#                ner_server_process.kill()
 #               time.sleep(0.5)
#                os.chdir('../external/')
#                print os.getcwd()
#                ner_server_process = subprocess.Popen('./ner.sh')
#                os.chdir('../testimony/')
#                time.sleep(3)
                pass
            
        counter += 1
        print "Server calls: ", counter
        if not entities.has_key('PERSON'):
            continue
        names = entities['PERSON']
#        names = tagger.get_entities(named_lines)['PERSON']

        print "named lines for ", current_name, "are:\n", named_lines
        print "names extracted: ", names
        print "----------------------------"

        if namedict.has_key(current_name):
            namedict[current_name].append(names)
        else:
            namedict[current_name] = names
    return namedict

def test_ner():
    a = range(1, 30)
    tagger = ner.HttpNER(host='localhost', port=8080)
    for num in a:
        entities = tagger.get_entities(str(num))
        print "entities", entities
        print "call number: ", num
        time.sleep(.5)
