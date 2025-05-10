# main.py (excerpt)
import os, warnings
import networkx as nx
from networkx.drawing.nx_pydot import write_dot
from visualize import render_subsystem_graph
import pickle
import numpy as np

from import_graph    import build_import_graph
from prune_graph     import prune_graph
from collapse_graph  import collapse_to_packages
from metrics_overlay  import *

warnings.filterwarnings("ignore", category=SyntaxWarning)

def main():
    # ── resolve paths ──
    #script_dir = os.path.dirname(__file__)
    #root_dir   = os.path.abspath(os.path.join(script_dir, "..", "api", "zeeguu"))
    #pkg_name   = "zeeguu"

    script_dir    = os.path.dirname(__file__)        # …/recovery_tools
    root_dir      = os.path.abspath(
        os.path.join(script_dir, "..", "api", "zeeguu", "core", "model")
    )
    pkg_name = "zeeguu.core.model"


    # ── 1) raw graph ──
    G = build_import_graph(root_dir, pkg_name)
    print(f"Extracted {G.number_of_nodes()} modules and {G.number_of_edges()} edges.")

    loc_map      = compute_module_loc(root_dir, pkg_name)
    cc_map       = compute_module_cc(root_dir, pkg_name)
    deg_map = compute_degree(G)
    pr_map = compute_pagerank(G)

    degree_values = np.array(list(deg_map.values()))
    degree_p25 = int(np.percentile(degree_values, 25))
    degree_p50 = int(np.percentile(degree_values, 50))
    degree_p75 = int(np.percentile(degree_values, 75))
    degree_p85 = int(np.percentile(degree_values, 85))


    loc_values = np.array(list(loc_map.values()))
    loc_p25 = np.percentile(loc_values, 25)
    loc_p50 = np.percentile(loc_values, 50)
    loc_p75 = np.percentile(loc_values, 75)
    loc_p85 = np.percentile(loc_values, 85)


    pr_values = list(pr_map.values())
    pr_p25 = np.percentile(pr_values, 50)
    pr_p50 = np.percentile(pr_values, 50)
    pr_p75       = np.percentile(pr_values, 75)
    pr_p90       = np.percentile(pr_values, 90)

    annotate_metrics(G, loc_map, cc_map, deg_map, pr_map)


    # ── 2) prune noise ── p25 for zeeguu and zeeguu.core, p75 for zeeguu.model
    G_pruned = prune_graph(
        G,
        pkg_name,
        min_loc=loc_p75,
        min_cc=2,
        min_degree=degree_p75,
        min_pr=0
    )
    print(f"Pruned to {G_pruned.number_of_nodes()} nodes and {G_pruned.number_of_edges()} edges.")

    # 4) collapse to packages **and** aggregate LOC
    G_pkg = collapse_to_packages(
        G_pruned,
        depth=2
    )
    print(f"Collapsed to {G_pkg.number_of_nodes()} packages.")

    # 5) detect & annotate communities
    #mapping = detect_communities(G_pkg)
    #annotate_communities(G_pkg, mapping)
    #print(f"Found {len(set(mapping.values()))} communities.")


    # 6) render final diagram (colors, sizes by loc)
    #render_styled_graph2(
        #G_pkg,
        #out_png="zeeguu_architecture.png",
        #palette="paired12",
        #depth=2
    #)

    render_subsystem_graph(
        G_pruned,
        out_png="core_subsystem.png",
        engine="neato",      # color by "zeeguu.core"
    )

if __name__ == "__main__":
    main()
