#!/usr/bin/env python
import networkx as nx
import testimony.graph as graph
import testimony.nameutils as nameutils
cimport classifier

# this assumes that the unweighted named graph already exists.


def generate_graph_with_sentiment_weights(G):
    "this assumes that the graph's edges from a to b have speechacts by a that mention b"
    for edge in G.edges_iter():
        print "edge: ", edge
        a = edge[0]
        a_name = G.node[a]['label']
        b = edge[1]
        b_name = G.node[b]['label']
        speechacts_scores = []
        for speechact in G.edge[a][b]['speechacts']:
            scores = classifier.score_all_entities_in_speechact(speechact)
            for entity in scores.keys():
                # if nameutils.are_close_tokens(b_name, entity):
                if nameutils.are_close(b_name, entity):
                    speechacts_scores += scores[entity]

        average_score = 0
        if speechacts_scores:
            average_score = sum(speechacts_scores) / len(speechacts_scores)
        G.edge[a][b]['score'] = average_score

def generate_graph_with_sentiment_weights_2(G, transcripts):
    "assumes a simple unweighted naming graph"
    for edge in G.edges_iter():
        a = edge[0]
        a_name = G.node[a]['label']
        b = edge[1]
        b_name = G.node[b]['label']
        speechacts = transcripts.get_speech_acts_by_speaker_and_mention(a_name, b_name)

        speechacts_scores = []
        for speechact in speechacts:
            scores = classifier.score_all_entities_in_speechact(speechact)
            for entity in scores.keys():
                if nameutils.are_close(b_name, entity):
                    speechacts_scores.append(scores[entity])

        average_score = 0
        if speechacts_scores:
            average_score = sum(speechacts_scores) / len(speechacts_scores)
        G.edge[a][b]['score'] = average_scoreq

def generate_graph_with_speechacts_2(G, transcripts):
    for edge in G.edges_iter():
        a = edge[0]
        a_name = G.node[a]['label']
        b = edge[1]
        b_name = G.node[b]['label']
        speechacts = transcripts.get_speech_acts_by_speaker_and_mention(a_name, b_name)
        G.edge[a][b]['speechacts'] = speechacts

def generate_graph_with_speechacts(G, transcripts):
    for n_id in G.node.keys():
        n_name = G.node[n_id]['label']
        for neighbor in G.neighbors(n_id):
            neighbor_id = neighbor['id']
            neighbor_name = neighbor['label']
            speechacts = transcripts.get_speech_acts_by_speaker_and_phrase(n_name, neighbor_name)
            G.edge[n_id][neighbor_id]['speechacts'] = speechacts
