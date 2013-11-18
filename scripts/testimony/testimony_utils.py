#!/usr/bin/env python
import re
import os
import namedist
from collections import defaultdict
from preprocessing import cleanFile
from config import transcript_dir



class Transcripts:
    def __init__(self):
        self.names = [f.replace(".txt", "") for f in os.listdir(transcript_dir)]
        self.speechacts = self.get_all_speech_acts()

    def get_all_speech_acts(self):
        """
        produces a dict of name -> list of speech acts for every speaker
        in all testimonies
        """
        def merge(dicts):
            "merges every dict in dicts. assumes that vals are lists"
            print "Merging..."
            result = defaultdict(lambda: [])
            for d in dicts:
                for (k,v) in d.items():
                    result[k] += v
            return result
                            
        dicts = []
        print "Getting speech acts..."
        for name in self.names:
            dicts.append(self.get_speech_acts_from_testimony(name))

        # remove bum keys
        speechacts =  merge(dicts)
        for key in speechacts.keys():
            if len(key) < 3:
                del speechacts[key]

        dist = namedist.name_distribution_from_dict(speechacts)

        for (k, v) in speechacts.items():
            likely_name = namedist.find_likely_name(k, dist)
            if not dist[likely_name] < .00001:
                speechacts[likely_name] += v
            if not likely_name == k:
                del speechacts[k]

        return speechacts

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

        regex = re.compile("^(?:Mrs|Miss|Mr)(?:\.?)(?:\s?)(\w*?)[\.\s](.*?)\n",
                           re.MULTILINE)
        matches = regex.findall(str)

        # name distribution to guess likely names from mispellings
        dist = namedist.name_distribution_from_matches(matches)
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
    
