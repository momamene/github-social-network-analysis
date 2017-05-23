import networkx as nx
import sys
import json
import matplotlib.pyplot as plt
import math

from networkx.algorithms import bipartite


if __name__ == "__main__":
    json_path = sys.argv[1]
    png_path = sys.argv[2]
    B = nx.Graph()
    with open(json_path) as f:
        for raw_data in f:
            data = json.loads(raw_data)
            filename, commits = data.popitem()
            B.add_node(filename, bipartite=0)
            for commit in commits:
                B.add_node(commit, bipartite=1)
                B.add_edge(filename, commit)

    print("Bipartite Graph created")

    filenames = [
        node
        for node, attributes
        in B.node.items()
        if attributes['bipartite'] == 0
    ]

    G = bipartite.weighted_projected_graph(B, filenames, ratio=True)
    print("Projected Graph created")

    # pos = nx.spring_layout(G, scale=100, iterations=50)
    pos = nx.random_layout(G)
    print("Nodes are positioned.")

    node_labels = { filename: filename for filename in filenames }
    nx.draw_networkx_labels(G, pos, node_labels, font_size=2)

    node_size = [
        math.log10(degree + 2) * 100 for filename, degree in G.degree().items()
    ]
    nx.draw_networkx_nodes(G, pos, node_size=node_size)
    print("Nodes are drawn.")

    weights = [d['weight'] * 100 for (u,v,d) in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, edge_color=weights, width=weights)
    print("Edges are drawn.")

    plt.savefig(png_path)
    print("Graph picture are saved.")
