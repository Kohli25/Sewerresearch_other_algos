import pandas as pd 
import math
import networkx as nx
import matplotlib.pyplot as plt
import os

def build_weighted_graph(nodes_df, edges_df):
    """
    Build an undirected graph with Euclidean distance weights between node coords.
    Returns networkx.Graph() and a pos dict {node: (x,y)} for plotting.
    nodes_df: index = node id, columns include ['x','y','flow','elevation'] (flow/elevation optional)
    edges_df: two columns (u,v) or index can be ignored; each row is (u,v)
    """
    G = nx.Graph()
    outlet_id=None
    
    # Add nodes with attributes and build pos dict
    for nid, row in nodes_df.iterrows():

        x = float(row["x"])
        y = float(row["y"])
        # safe-get flow and elevation (set to 0 if missing)
        flow = float(row["flow"]) if "flow" in row and not pd.isna(row["flow"]) else 0.0
        #print(flow)
        
        #outlet node
        if(flow<0):
            outlet_id=nid
            
        elev = float(row["elevation"]) if "elevation" in row and not pd.isna(row["elevation"]) else None
        G.add_node(nid, x=x, y=y, ground_level=elev,flow=flow)

    # Add edges with length weight
    for _, (u, v) in edges_df.iterrows():
        if u not in nodes_df.index or v not in nodes_df.index:
            continue
        xu, yu = nodes_df.loc[u, ["x", "y"]]
        xv, yv = nodes_df.loc[v, ["x", "y"]]
        length = math.hypot(float(xu) - float(xv), float(yu) - float(yv))
        G.add_edge(u, v, length=length)
        
            
    print(f"\nTree Network Summary:")
    print(f"="*20)
    print(f"Total Manholes: {G.number_of_nodes()}")
    print(f"Total Sections: {G.number_of_edges()}")
    print(f"Outlet Node: {outlet_id}")

        

    return G,outlet_id



def plot_graph_with_coords(G, title="Tree Plot", show_elevation=False, show_lengths=True, 
                          show_edge_flows=False, figsize=(10, 8), save_path=None):

    plt.figure(figsize=figsize)
    ax = plt.gca()
    
    # extract positions of manholes
    pos = {}
    for n, data in G.nodes(data=True):
        if "x" in data and "y" in data:
            pos[n] = (float(data["x"]), float(data["y"]))
    
    # Node sizes: scale flow (add small base so zero-flow nodes are visible)
    flows = nx.get_node_attributes(G, "flow")
    
    # Edge widths: normalize lengths to a reasonable thickness
    lengths = nx.get_edge_attributes(G, "length")
    edge_flows = nx.get_edge_attributes(G, "flow_m3s")
    
    # Draw edges and nodes at their coordinates
    nx.draw_networkx_edges(G, pos, ax=ax, width=2)
    node_collection = nx.draw_networkx_nodes(G, pos, node_size=500, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=9, ax=ax)
    
    edge_labels = {}
    for e, d in G.edges.items():
        text = []
        if show_lengths and "length" in d:
            text.append(f"L={d['length']:.2f} m")
        if show_edge_flows and "flow_m3s" in d:
            text.append(f"Q={d['flow_m3s']:.3f} m3/s")
        if text:
            edge_labels[e] = "\n".join(text)  # stacked
            
    if edge_labels:
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, label_pos=0.5)
    
    # Optional: annotate elevation next to nodes
    if show_elevation:
        elevs = nx.get_node_attributes(G, "elevation")
        for n, (x, y) in pos.items():
            ev = elevs.get(n, None)
            if ev is not None:
                ax.text(x + 0.2, y + 0.2, f"{ev:.2f}m", fontsize=7, alpha=0.8)
    
    ax.set_aspect('equal', adjustable='datalim')   # preserve scale
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    plt.title(title)
    plt.tight_layout()
    
    # Save figure if path is provided
    if save_path:
        # Ensure directory exists
        save_dir = os.path.dirname(save_path)
        if save_dir:  # Only create directory if path contains a directory
            os.makedirs(save_dir, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to: {save_path}")
    
    plt.show()
