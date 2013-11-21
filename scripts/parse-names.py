#!/usr/bin/env python
import re

def remove_lines_with_leading_spaces(filepath):
    # lines that either start with a capital or leading spaces.
    regex = re.compile("(^\s.*)|(^[a-z].*)")
    # read lines in
    f = open(filepath, "r")
    lines = f.readlines()
    f.close()
    f = open(filepath, "w")
    for line in lines:
        if not regex.findall(line):
            f.write(line)
    f.close()

def clean_names(filepath):
    regex = re.compile("(^[A-Z][a-z]+,\s*[A-Z][a-z]+)" +   # First, Last
                       "\s*" +                             # some whitespace
                       "([A-Z][a-z]+.*?,)?" +              # Another name, maybe.
                       "(Testimony|Investigation .*\n)?")  # Some have this weird thing
