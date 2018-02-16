from collections import deque

import networkx as nx
import numpy as np


def random_subtree(T, alpha, beta, subtree_mark):
    """ Random subtree of T according to Algorithm X in [1].

    Args:
        alpha (float): probability of continuing to a neighbor
        beta (float): probability of non empty subtree
        T (NetworkX graph): the tree of which the subtree is taken

    Returns:
        A subtree of T

    References:
        [1] F. Rios J., Ohlsson, T. Pavlenko Bayesian structure learning in graphical models using sequential Monte Carlo.

    """
    # Take empty subtree with prob beta
    empty = np.random.multinomial(1, [beta, 1-beta]).argmax()
    subtree_edges = []
    subtree_nodes = []

    if empty == 1:
        separators = {}
        subtree = nx.Graph()
        return (subtree, [], [], {}, separators, 1-beta)

    # Take non-empty subtree
    n = T.order()
    w = 0.0
    visited = set()  # cliques
    q = deque([])
    start = np.random.randint(n)  # then n means new component
    separators = {}
    start_node = T.nodes()[start]
    q.append(start_node)
    subtree_adjlist = {start_node: []}
    while len(q) > 0:
        node = q.popleft()
        visited.add(node)
        subtree_nodes.append(node)
        T.node[node]["subnode"] = subtree_mark
        for neig in T.neighbors(node):
            b = np.random.multinomial(1, [1-alpha, alpha]).argmax()
            if neig not in visited:
                if b == 1:
                    subtree_edges.append((node, neig))
                    subtree_adjlist[node].append(neig)
                    subtree_adjlist[neig] = [node]
                    q.append(neig)
                    # Add separator
                    sep = neig & node
                    if not sep in separators:
                        separators[sep] = []
                    separators[sep].append((neig, node))
                else:
                    w += 1

    subtree = T.subgraph(subtree_nodes)
    v = len(subtree_nodes)
    probtree = beta * v * np.power(alpha, v-1) / np.float(n)
    probtree *= np.power(1-alpha, w)
    return (subtree, subtree_nodes, subtree_edges, subtree_adjlist, separators, probtree)


def prob_subtree(subtree, T, alpha, beta):
    """ Returns the probability of the subtree subtree generated by
    random_subtree(T, alpha, beta).

    Args:
        T (NetworkX graph): A tree
        subtree (NetworkX graph): a subtree of T drawn by the subtree kernel
        alpha (float): Subtree kernel parameter
        beta (float): Subtree kernel parameter

    Returns:
        float
    """
    p = subtree.order()
    if p == 0:
        return 1.0 - beta
    forest = T.subgraph(set(T.nodes()) - set(subtree.nodes()))
    components = nx.connected_components(forest)
    w = float(len(list(components)))
    v = float(subtree.order())
    alpha = float(alpha)
    beta = float(beta)
    n = float(T.order())
    prob = beta * v * np.power(alpha, v-1) * np.power(1-alpha, w) / n
    return prob