# collapse_graph.py

import networkx as nx
from collections import Counter
from typing import List

def collapse_to_packages(
    G: nx.DiGraph,
    depth: int = 2
) -> nx.DiGraph:
    """
    Collapse a module‐graph G into a package‐graph at the given depth,
    aggregating any node‐attributes named 'loc', 'cc', 'degree', 'pagerank'.
    """
    def pkg(name: str) -> str:
        parts = name.split(".")
        return ".".join(parts[:depth])

    # 1) count import‐edges between packages
    weights = Counter()
    for u, v in G.edges():
        pu, pv = pkg(u), pkg(v)
        if pu != pv:
            weights[(pu, pv)] += 1

    # 2) build collapsed graph (with edge weights)
    H = nx.DiGraph()
    for (pu, pv), w in weights.items():
        H.add_edge(pu, pv, weight=w)

    # 3) aggregate metrics on G into package nodes on H
    METRICS = ["loc", "cc", "degree", "pagerank"]
    # prepare counters for each metric
    pkg_counters = { m: Counter() for m in METRICS }

    # walk every module‐node in G
    for module, attrs in G.nodes(data=True):
        p = pkg(module)
        if p not in H:
            # skip any package that ended up with no edges
            continue
        for m in METRICS:
            if m in attrs:
                pkg_counters[m][p] += attrs[m]

    # attach as node attributes in H
    for m, counter in pkg_counters.items():
        for p, total in counter.items():
            H.nodes[p][m] = total

    return H
