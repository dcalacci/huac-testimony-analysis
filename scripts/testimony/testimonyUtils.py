#!/usr/bin/env python
import re, os
from preprocessing import cleanFile
from config import transcript_dir

class Transcripts:
    def __init__(self):
        self.names = [f.replace(".txt", "") for f in os.listdir(transcript_dir)]

    # some functions to guess likely names from mispellings. works OK
    def are_close(a, b):
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

    def get_all_speech_acts(self):
        for t in transcript_dir:
            speechacts = self.get_speech_acts(os.path.join(transcript_dir, t))

    def get_speech_acts(self, filepath):
        "returns a hash of name -> list of speech acts for a particular file."
        def name_distribution(matches):
            "computes a dict of name->% for all speech acts"
            import collections
            dist = collections.defaultdict(lambda: 0)

            for match in matches:
                dist[match[0]] += 1

                # prefer names in all caps
                if match[0].isupper():
                    dist[match[0]] += 10
            l = len(dist.keys())
            for key in dist.keys():
                dist[key] = dist[key]/float(l)

            return dist

        def find_likely_name(name, dist):
            "returns the most likely name given the a distribution of names"
            maybes = dict((k, v) for k, v in dist.items() if are_close(name.lower(), k.lower()))
            best = max(maybes.items(), key=lambda p: p[1])
            return best[0]

        cleanFile(filepath)
        str = ""
        with open(filepath, 'r+') as f:
            import mmap
            str = mmap.mmap(f.fileno(), 0)
        f.close()

        regex = re.compile("^(?:Mrs|Miss|Mr)(?:\.?)(?:\s?)(\w*?)[\.\s](.*?)\n",re.MULTILINE)
        matches = regex.findall(str)

        # name distribution to guess likely names from mispellings
        dist = name_distribution(matches)
        speechacts = {}
        for match in matches:
            likely_name = find_likely_name(match[0], dist).lower()
            # if the likely name has a low occurrence rate:
            if not dist[likely_name] < .03:
                if speechacts.has_key(likely_name):
                    speechacts[likely_name].append(match[1])
                else:
                    speechacts[likely_name] = [match[1]]
        return speechacts

    def is_actor(name):
        # get the end of the filename
        # compare to name given

#def is_actor():
#def get_speech_acts_by_speaker(speaker):
    
