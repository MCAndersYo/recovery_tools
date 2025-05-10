import os
import ast
from radon.complexity import cc_visit
import networkx as nx
from import_graph import find_python_modules

def compute_module_loc(root_pkg_dir: str, package_name: str) -> dict[str, int]:
    """
    Compute Lines of Code (LOC) for each module in the given package.
    Returns a dict mapping module_name -> non-blank line count.
    """
    module_loc = {}
    modules = find_python_modules(root_pkg_dir, package_name)
    for module_name, path in modules:
        with open(path, "r", encoding="utf-8") as f:
            non_blank = sum(1 for line in f if line.strip())
        module_loc[module_name] = non_blank
    return module_loc

def compute_module_cc(root_pkg_dir: str, package_name: str) -> dict[str, int]:
    """
    Compute Cyclomatic Complexity (CC) for each module in the given package.
    Returns a dict mapping module_name -> total cyclomatic complexity.
    """
    module_cc = {}
    modules = find_python_modules(root_pkg_dir, package_name)
    for module_name, path in modules:
        src = open(path, "r", encoding="utf-8").read()
        blocks = cc_visit(src)
        total_cc = sum(block.complexity for block in blocks)
        module_cc[module_name] = total_cc
    return module_cc

def compute_degree(G: nx.DiGraph) -> dict[str, int]:
    """
    Compute the total degree (in + out) for each node.
    """
    return dict(G.degree())

def compute_pagerank(G: nx.DiGraph, **kwargs) -> dict[str, float]:
    """
    Compute PageRank scores on the undirected version of G.
    Additional kwargs are passed to networkx.pagerank.
    """
    undirected = G.to_undirected()
    return nx.pagerank(undirected, **kwargs)
    

def annotate_metrics(G, loc_map, cc_map, deg_map, pr_map):
    for n in G.nodes():
        G.nodes[n].update({
            "loc": loc_map.get(n, 0),
            "cc":  cc_map.get(n,  0),
            "degree":   deg_map.get(n, 0),
            "pagerank": pr_map.get(n, 0.0)
    })
    return G