#!/usr/bin/env python
import networkx as nx
import testimony.graph as graph
from testimony.testimony_utils import Transcripts
import classifier

# this assumes that the unweighted named graph already exists.

def generate_graph_with_speechacts(G, transcripts):
    for n_id in G.node.keys():
        n_name = G.node[n_id]['label']
        for neighbor in G.neighbors(n_id):
            neighbor_id = neighbor['id']
            neighbor_name = neighbor['label']
            speechacts = transcripts.get_speech_acts_by_speaker_and_phrase(n_name, neighbor_name)
            G.edge[n_id][neighbor_id]['speechacts'] = speechacts
