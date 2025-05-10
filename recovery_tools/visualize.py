# visualize3_no_clusters.py

import os
from graphviz import Digraph

def render_subsystem_graph(
    G,
    out_png="subsystem.png",
    engine="neato",      # spring‐layout engine
):
    """
    • node size ∝ LOC (attrs['loc'])
    • node fill‐color ∝ PageRank (attrs['pagerank']), white→red
    • node border thickness ∝ Cyclomatic Complexity (attrs['cc'])
    • edge thickness ∝ import‐weight, labels = import‐weight
    • bidirectional dependencies → single line with arrows at both ends
    • nodes drawn after edges so edges never cover them
    """
    # 1) Collect node metrics
    nodes = list(G.nodes(data=True))
    locs = [attrs.get("loc", 0)         for _, attrs in nodes]
    prs  = [attrs.get("pagerank", 0.0)  for _, attrs in nodes]
    ccs  = [attrs.get("cc", 0)          for _, attrs in nodes]

    min_loc, max_loc = (min(locs), max(locs)) if locs else (0, 1)
    min_pr,  max_pr  = (min(prs),  max(prs))  if prs  else (0.0, 1.0)
    min_cc,  max_cc  = (min(ccs),  max(ccs))  if ccs  else (0, 1)

    # 2) Build the Digraph with tighter spacing
    dot = Digraph(format="png", engine=engine)
    dot.graph_attr.update(
        dpi="300",
        overlap="false",
        splines="ortho",
        K="0.3",
        nodesep="0.2",   # closer nodes
        ranksep="0.3",   # tighter ranks
        pad="0.2"        # less padding
    )
    # edge defaults
    dot.edge_attr.update(color="gray50", fontsize="10", fontcolor="gray20")

    # 3) Emit edges first
    seen = set()
    for u, v, edata in G.edges(data=True):
        if (v, u) in G.edges and frozenset((u, v)) not in seen:
            w1 = G[u][v].get("weight", 1)
            w2 = G[v][u].get("weight", 1)
            label = f"{w1}/{w2}"
            pen = min(4, 0.3 + max(w1, w2))
            dot.edge(u, v, penwidth=str(pen), label=label, dir="both")
            seen.add(frozenset((u, v)))
        elif (v, u) not in G.edges:
            w = edata.get("weight", 1)
            pen = min(4, 0.3 + w)
            dot.edge(u, v, penwidth=str(pen), label=str(w), dir="forward")

    # 4) Now emit nodes afterwards, with larger font and name-only labels
    dot.node_attr.update(
        style="filled,rounded",
        shape="box",
        fontsize="12",   # larger label text
        fontcolor="black"
    )

    for node, attrs in nodes:
        # size by LOC
        loc = attrs.get("loc", 0)
        norm_loc = (loc - min_loc) / (max_loc - min_loc) if max_loc > min_loc else 1.0
        size = 0.5 + norm_loc * (3.0 - 0.5)

        # fill-color by PR
        pr = attrs.get("pagerank", 0.0)
        norm_pr = (pr - min_pr) / (max_pr - min_pr) if max_pr > min_pr else 1.0
        r = 255
        gb = int(255 * (1 - norm_pr))
        fillcol = f"#{r:02x}{gb:02x}{gb:02x}"

        # border thickness by CC
        cc = attrs.get("cc", 0)
        norm_cc = (cc - min_cc) / (max_cc - min_cc) if max_cc > min_cc else 1.0
        pen = 1 + norm_cc * 4

        # label = node name only
        short = node.split(".")[-1]

        dot.node(
            node,
            label=short,
            width=f"{size:.2f}",
            height=f"{size:.2f}",
            fillcolor=fillcol,
            penwidth=str(pen)
        )

    # 5) Add legend
    legend_label = '''<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4" BGCOLOR="white">
  <TR><TD ALIGN="LEFT">Node area</TD><TD>LOC</TD></TR>
  <TR><TD ALIGN="LEFT">Fill color</TD><TD>PageRank</TD></TR>
  <TR><TD ALIGN="LEFT">Border thickness</TD><TD>Cyclomatic Complexity</TD></TR>
  <TR><TD ALIGN="LEFT">Edge thickness</TD><TD>Import count</TD></TR>
  <TR><TD ALIGN="LEFT">Edge label</TD><TD>Import count</TD></TR>
</TABLE>
>'''
    with dot.subgraph(name="cluster_legend") as leg:
        leg.attr(label="Legend", labelloc="b", fontsize="10")
        leg.node(
            "legend",
            shape="box",
            style="filled",
            fillcolor="white",
            margin="0.1",
            label=legend_label
        )

    # 6) Render (overwrite existing .png)
    base = out_png.replace(".png", "")
    png  = f"{base}.png"
    if os.path.exists(png):
        os.remove(png)
    dot.render(filename=base, cleanup=True)
    print(f"Wrote {png}")

