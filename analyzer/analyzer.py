import settings
import networkx as nx
import matplotlib.pyplot as plt
import os
import operator

def read_graph():
    path = settings.GEXF_PATH
    G = nx.read_gexf(path)
    return G


def get_user_list(G):
    return [
        label
        for label
        in G.node
        if G.node[label]['_type'] == 'user'
    ]

def get_issue_list(G, include_PR=True):
    if include_PR:
        return [
            label
            for label
            in G.node
            if G.node[label]['_type'] == 'issue'
        ]
    else:
        return [
            label
            for label
            in G.node
            if (
                    G.node[label]['_type'] == 'issue' and
                    not G.node[label].get('is_pull_request')
            )
        ]

def get_pr_list(G):
    return [
        label
        for label
        in G.node
        if (
                G.node[label]['_type'] == 'issue' and
                G.node[label].get('is_pull_request')
        )
    ]

def draw(G):

    user_list = get_user_list(G)
    issue_list = get_issue_list(G,True)
    pr_list = get_pr_list(G)

    pos = nx.drawing.spring_layout(G)

    nx.draw_networkx_nodes(
        G, pos,
        nodelist=user_list,
        node_color='r',
        node_size=5,
        alpha=0.5
    )

    nx.draw_networkx_nodes(
        G, pos,
        nodelist=issue_list,
        node_color='g',
        node_size=5,
        alpha=0.5
    )

    nx.draw_networkx_nodes(
        G, pos,
        nodelist=pr_list,
        node_color='b',
        node_size=5,
        alpha=0.5
    )

    nx.draw_networkx_edges(
        G, pos,
        edgelist=G.edges(),
        node_size=5,
        width=0.1,
        alpha=0.1,
        edge_color='#000000'
    )

    # Labeling
    labels = {
        node: (
            node + '(RR)' if G.node[node].get('is_pull_request')
            else node
        )
        for node
        in G.nodes()
    }

    if not os.path.exists(settings.DIST_PATH):
        os.makedirs(settings.DIST_PATH)

    plt.axis('off')

    filename = os.path.basename(settings.GEXF_PATH).replace('gexf', 'png')
    plt.savefig(
        settings.DIST_PATH + '/' + filename
    )
    
if __name__ == "__main__":
    G = read_graph()
    issue_list = get_issue_list(G)
    user_list = get_user_list(G)

    issue_issue_G = G.subgraph(issue_list)
    user_user_G = G.subgraph(user_list)

    user_issue_G = G.copy()
    for from_node, to_node in G.edges_iter():
        edge = user_issue_G.edge[from_node][to_node]
        if not edge.get('commenter') and not edge.get('issuer'):
            user_issue_G.remove_edge(from_node, to_node)
    user_degree_list = [
        degree
        for user, degree
        in user_issue_G.out_degree().items()
        if degree > 0
    ]

    draw(G)
