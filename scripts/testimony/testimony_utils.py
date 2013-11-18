#!/usr/bin/env python
import re
import os
import namedist
from preprocessing import cleanFile
from config import transcript_dir

class Transcripts:
    def __init__(self):
        self.names = [f.replace(".txt", "") for f in os.listdir(transcript_dir)]

    def get_all_speech_acts(self):
        for t in transcript_dir:
            speechacts = self.get_speech_acts_from_file(os.path.join(transcript_dir, t))

    def get_speech_acts_from_testimony(self, name):
        "gets all the speech acts from the given actor's testimony."
        return self._get_speech_acts_from_file(os.path.join(transcript_dir, 
                                                            name+".txt"))

    def _get_speech_acts_from_file(self, filepath):
        "returns a hash of name -> list of speech acts for a particular file."
        cleanFile(filepath)
        str = ""
        with open(filepath, 'r+') as f:
            import mmap
            str = mmap.mmap(f.fileno(), 0)
        f.close()

        regex = re.compile("^(?:Mrs|Miss|Mr)(?:\.?)(?:\s?)(\w*?)[\.\s](.*?)\n",re.MULTILINE)
        matches = regex.findall(str)

        # name distribution to guess likely names from mispellings
        dist = namedist.name_distribution(matches)
        print dist
        speechacts = {}
        for match in matches:
            likely_name = namedist.find_likely_name(match[0], dist).lower()
            # if the likely name doesn't have a low occurrence rate:
            if not dist[likely_name] < .01:
                if speechacts.has_key(likely_name):
                    speechacts[likely_name].append(match[1])
                else:
                    speechacts[likely_name] = [match[1]]
        return speechacts

#    def is_actor(name):
        # get the end of the filename
        # compare to name given

#def is_actor():
#def get_speech_acts_by_speaker(speaker):
    
