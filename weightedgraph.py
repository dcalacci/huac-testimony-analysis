#!/usr/bin/env python
import networkx as nx
import testimony.graph as graph
from testimony.testimony_utils import Transcripts
import classifier

def get_weighted_graph(year):
    graph = graph.get_named_graph(year)
    for k in graph
