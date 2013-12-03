#!/usr/bin/env python
import os
import pickle
import itertools
import networkx as nx
from config import graphs_dir


# class NamedGraph:
#     def __init__(self):
        
#         # list of graphs. temporary until you merge them
#         self.graphs = []
#         for p in os.listdir(graphs_dir):
#             self.graphs.append(pickle.load(open(p, "rb")))

def find_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if not graph.has_key(start):
        return None
    for node in graph[start]:
        if node not in path:
            newpath = find_path(graph, node, end, path)
            if newpath: return newpath
    return None

def find_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if not graph.has_key(start):
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths


# simple named graph 
p1953= pickle.load(open(os.path.join(graphs_dir, "1953.p"), "rb"))
for k,v in p1953.items():
    newv = [([x] if isinstance(x,basestring) else x) for x in v]
    v = list(itertools.chain(*newv))
    p1953[k] = v


named_graph = nx.DiGraph()
for start, ends in p1953.items():
    for end in ends:
        named_graph.add_edge(start, end)

pos = nx.spring_layout(named_graph)
nx.draw_networkx(named_graph, pos)
