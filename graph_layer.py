import networkx as nx

graph = nx.Graph()


def build_graph():
    graph.add_edge("P123", "Mobiles", relation="belongs_to")
    graph.add_edge("P123", "ReturnPolicy", relation="has_policy")
    graph.add_edge("Mobiles", "Electronics", relation="parent_category")


def expand_graph(product_id):
    if product_id in graph:
        return list(graph.neighbors(product_id))
    return []
