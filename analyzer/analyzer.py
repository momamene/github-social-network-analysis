import settings
import networkx as nx
import matplotlib.pyplot as plt
import os


def read_graph():
    path = settings.GEXF_PATH
    graph = nx.read_gexf(path)
    return graph
    

def draw(G):

    user_list = [
        label
        for label
        in graph.node
        if graph.node[label]['_type'] == 'user'
    ]
    issue_list = [
        label
        for label
        in graph.node
        if graph.node[label]['_type'] == 'issue'
    ]

    pos = {}

    pos.update(
        (node, (1, index))
        for index, node
        in enumerate(user_list)
    )
    pos.update(
        (node, (2, index))
        for index, node
        in enumerate(issue_list)
    )


    nx.draw_networkx_nodes(
        G, pos,
        nodelist=user_list,
        node_color='r',
        node_size=500,
        alpha=0.8
    )

    nx.draw_networkx_nodes(
        G, pos,
        nodelist=issue_list,
        node_color='b',
        node_size=500,
        alpha=0.8
    )

    nx.draw_networkx_edges(
        G, pos,
        edgelist=G.edges(),
        node_size=500,
        width=2,
        alpha=1,
        edge_color='g'
    )

    # Labeling 
    labels = {
        node: r'%s' % (node,)
        for node
        in graph.nodes()
    }

    nx.draw_networkx_labels(
        G,
        pos,
        labels,
        font_size=10
    )
    
    if not os.path.exists(settings.DIST_PATH):
        os.makedirs(settings.DIST_PATH)

    plt.axis('off')
    plt.savefig(
        settings.DIST_PATH + '/' + settings.DRAWING_FILENAME
    )

if __name__ == "__main__":
    graph = read_graph()
    draw(graph)
