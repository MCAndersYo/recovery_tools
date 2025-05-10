import re
import networkx as nx

# ------- Name-based noise patterns -------
EXCLUDE_PATTERNS = [
    r"(^|\.)tests?($|\.)",    # .test. or .tests or ends with .test/.tests
    r"(^|\.)scripts?($|\.)",
    r"(^|\.)notebooks?($|\.)",
    r"(^|\.)examples?($|\.)",
    r"(^|\.)demos?($|\.)",
    r"(^|\.)utils?($|\.)",
    r"(^|\.)helpers?($|\.)",
    r"(^|\.)migrations?($|\.)",
    r"(^|\.)configs?($|\.)",
    r"(^|\.)docs?($|\.)",
    r"(^|\.)fixtures?($|\.)",
    r"(^|\.)seed($|\.)",
    r"(^|\.)__init__$"
]

def is_noise_module(name: str) -> bool:
    """
    Return True if the module name matches any noise pattern
    (e.g., test modules, scripts, notebooks, etc.).
    """
    return any(re.search(p, name) for p in EXCLUDE_PATTERNS)

def is_noise(name: str) -> bool:
    return any(re.search(p, name) for p in EXCLUDE_PATTERNS)

def prune_graph(
    G: nx.DiGraph,
    base_pkg: str,
    min_loc: int = 20,
    min_cc: int = 2,
    min_degree: int = 2,
    min_pr: float = 0.01
) -> nx.DiGraph:
    """
    Prune by:
      1) keeping only nodes under base_pkg,
      2) removing noise by name,
      3) enforcing LOC ≥ min_loc,
      4) enforcing CC  ≥ min_cc,
      5) enforcing degree ≥ min_degree,
      6) enforcing pagerank ≥ min_pr.
    """
    keep = []
    for n, data in G.nodes(data=True):
        # 1) only our package
        if not (n == base_pkg or n.startswith(base_pkg + ".")):
            continue
        # 2) noise names
        if is_noise(n):
            continue
        # 3) metric thresholds from node attributes
        if data.get("loc", 0)       < min_loc:     continue
        if data.get("cc", 0)        < min_cc:      continue
        if data.get("degree", 0)    < min_degree:  continue
        if data.get("pagerank", 0.0)< min_pr:      continue
        keep.append(n)

    return G.subgraph(keep).copy()
