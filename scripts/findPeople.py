#!/usr/bin/env python
import re, sys, os, fileinput, tempfile

def cleanFile(filepath):
    "removes unwanted lines from the given file"

    badlines = []
    badlines.append('^\d+')
    badlines.append('^COMMUNISM')
    badlines.append('^INDUSTRY')

    def isBadLine(line):
        "returns true if the line is a 'bad line'"
        for regex in badlines:
            if bool(re.findall(regex, line)):
                return True
        return False

    # remove lines that are "bad"
    for line in fileinput.input(filepath, inplace=1):
        if not isBadLine(line): print line,

    # remove blank lines
    for line in fileinput.input(filepath, inplace=1):
        if line.rstrip(): print line




def splitFileByTestimony(filepath):
    """
    Splits the file into parts based on who is giving the testimony.
    Produces a directory that mirrors the given file's name that contains
    files whose names correspond to individual's names
    """

    def findPersonDelimiters(filepath):
        """
        Finds the line number where an individual's testimony begins. 
        Returns a hash of the form 'name' => 'line number'
        """
        regex = re.compile("TESTIMONY OF (.+?)[,\n]")
        f=open(os.path.abspath(filepath))
        persons = {}
        for i, line in enumerate(f.readlines()):
            r = regex.findall(line)
            if r: # if we found anything
                # if the name is already there and this line number is after
                # the one we found previously, we shouldn't change the hash.
                if not (persons.has_key(r[0]) and i+1 > persons[r[0]]):
                    name = r[0].replace(' ', '-').lower()
                    persons[name] = i+1# make the hash: name -> line number
                    
        f.close()
        return persons

    def findPageRanges(filepath):
        """
        returns a list of tuples of the form (name, start, end) where name is the
        name of the person being interviewed, start is the line number at the
        start of that persons' transcript, and end is the end of the interview.
        """
        persons = sorted(findPersonDelimiters(filepath).items(), key=lambda x: x[1])
        # list of tuples of the form (name, start, end). if it ends at EOF, 
        # end is -1. Sorted by beginning line number.
        sections = []
        for index, person in enumerate(persons): 
            t = (person[0], person[1])
            if index+1 == len(persons):
                t = t + ("-1",)
            else:
                t = t + (persons[index+1][1],)
                sections.append(t)
        return sections

    def makeSubFile(origFile, start, end, name):
        """
        Copies the lines between 'start' and 'end' in origFile to a new file
        with the suffix 'name' into a new file in a subdirectory with the same
        name as origFile. The name of the new file is 'name', with the same
        extension as the original file.
        """
        path, filename = os.path.split(origFile)
        basename, ext = os.path.splitext(filename)
        # file is stored in directory {original-path}/{basename}
        newPath = os.path.join(path, basename)
        if not os.path.exists(newPath):
            os.makedirs(newPath)
        outfile = open(os.path.join(newPath, 
                                    '{}{}'.format(name, ext)), 'w')
        with open(origFile, 'r') as f:
            for i, line in enumerate(f):
                if i == end:
                    outfile.close()
                    break;
                if i > start:
                    outfile.write(line)

    def separateTranscriptBySpeaker(filepath, persons):
        """
        Splits the transcript into separate files based on the tuple given - 
        the tuple is of the same form that findPageRanges returns. Each sub-file
        has a suffix that corresponds to the speaker ('person') in the tuple.
        """
        for person in persons:
            makeSubFile(filepath, person[1], person[2], person[0].lower())
    persons = findPageRanges(filepath)
    print persons
    separateTranscriptBySpeaker(filepath, persons)
