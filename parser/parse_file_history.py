import networkx as nx
import sys
import json
import matplotlib.pyplot as plt
import math
from collections import defaultdict
from networkx.algorithms import bipartite
import random
import numpy as np
from networkx.algorithms.community.asyn_lpa import asyn_lpa_communities
from collections import Counter


def jaccard(G, u, v):
    unbrs = set(G[u])
    vnbrs = set(G[v])
    return float(len(unbrs & vnbrs)) / len(unbrs | vnbrs)

def common_neighbor(G, u, v):
    unbrs = set(G[u])
    vnbrs = set(G[v])
    return len(unbrs & vnbrs)

if __name__ == "__main__":

    # Parse dataset from path

    json_path = sys.argv[1]
    B = nx.Graph()
    with open(json_path) as f:
        for raw_data in f:
            data = json.loads(raw_data)
            filename, commits = data.popitem()
            B.add_node(filename, bipartite=0)
            for commit in commits:
                B.add_node(commit, bipartite=1)
                B.add_edge(filename, commit)

    # Split dataset into training data and test data

    validation_ratio = 0.2
    filenames = {
        n
        for n, d
        in B.nodes(data=True)
        if d['bipartite']==0
    }
    commits = set(B) - filenames

    # train data
    train_nodes_count = int(len(commits) * (1 - validation_ratio))
    train_commits = random.sample(commits, train_nodes_count)

    train_filenames = list(
        n1
        for n1, n2
        in B.edges()
        if n2 in train_commits
    )

    B_train = B.subgraph(train_filenames + train_commits)

    G_train = bipartite.generic_weighted_projected_graph(
        B_train, train_commits, weight_function=common_neighbor
    )

    communities = list(asyn_lpa_communities(G_train, 'weight'))

    print(communities)

    '''
    filename_labels = {
        filename: index
        for index, community
        in enumerate(communities)
        for filename
        in community
    }

    # test data
    test_commits = commits - set(train_commits)

    for commit in test_commits:
        freq = Counter()
        for filename in B[commit]:
            if filename not in train_filenames:
                continue
            freq.update({filename_labels[filename]: 1})
        if len(freq) > 1:
            print(commit, freq)
    '''
