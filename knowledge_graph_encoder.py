# knowledge_graph_encoder.py

class MonetaryPolicy:
    def __init__(self, instruments, targets, channels):
        self.instruments = instruments  # e.g., {'interest_rate': 0.05}
        self.targets = targets          # e.g., {'inflation': 0.02, 'unemployment': 0.05}
        self.channels = channels        # e.g., ['interest_rate', 'exchange_rate', 'credit', 'asset_price', 'expectations']

    def describe(self):
        return {
            "instruments": self.instruments,
            "targets": self.targets,
            "channels": self.channels
        }

class Scenario:
    def __init__(self, name, shocks):
        self.name = name
        self.shocks = shocks  # e.g., {'oil_price_shock': +0.1}

    def describe(self):
        return {
            "name": self.name,
            "shocks": self.shocks
        }

# Import sample_kg from a separate file
from knowledge_graph_sample import sample_kg

# Step 2: Represent the KG for the LLM

def kg_to_text(kg):
    node_labels = {n["id"]: n["label"] for n in kg["nodes"]}
    lines = ["The monetary policy transmission knowledge graph:"]
    for edge in kg["edges"]:
        src = node_labels[edge["source"]]
        tgt = node_labels[edge["target"]]
        sign = edge["sign"]
        if sign == "+/-":
            arrow = "↑/↓"
        else:
            arrow = "↑" if sign == "+" else "↓"
        lines.append(f"- {src} {arrow} → {tgt}")
    return "\n".join(lines)

# Step 3: Integrate with an LLM Agent (simulated)
def trace_transmission(kg, start_node, shock_direction):
    """
    Trace and print the transmission steps from a starting node (e.g., 'policy_rate')
    with a given shock direction ('+' for increase, '-' for decrease).
    Now supports bidirectional edges with sign '+/-'.
    """
    node_labels = {n["id"]: n["label"] for n in kg["nodes"]}
    from collections import deque
    # Expanded targets to include more macroeconomic endpoints for richer transmission tracing
    targets = {"output", "prices", "SPX", "UST", "inflation", "inflation_expectations", "behavior_change", "supply_demand_imbalance", "global_costs", "production", "deflation"}
    results = []
    queue = deque()
    queue.append((start_node, [start_node], shock_direction))
    while queue:
        node, path, sign = queue.popleft()
        if node in targets and node != start_node:
            results.append((path, sign))
            continue
        for edge in kg["edges"]:
            if edge["source"] == node:
                edge_sign = edge["sign"]
                if edge_sign == "+/-":
                    # For bidirectional, propagate both + and -
                    queue.append((edge["target"], path + [edge["target"]], '+'))
                    queue.append((edge["target"], path + [edge["target"]], '-'))
                else:
                    next_sign = sign if edge_sign == "+" else ('-' if sign == '+' else '+')
                    queue.append((edge["target"], path + [edge["target"]], next_sign))
    # Print steps
    for path, final_sign in results:
        step_str = ""
        for i in range(len(path)-1):
            src = node_labels[path[i]]
            tgt = node_labels[path[i+1]]
            edge = next(e for e in kg["edges"] if e["source"] == path[i] and e["target"] == path[i+1])
            edge_sign = edge["sign"]
            if edge_sign == "+/-":
                arrow = "↑/↓"
            else:
                arrow = "↑" if edge_sign == "+" else "↓"
            step_str += f"{src} {arrow} → "
        step_str += f"{node_labels[path[-1]]} (net effect: {'↑' if final_sign == '+' else '↓'})"
        print(step_str)

# Step 4: Example usage
import sys

# Add plotting imports
try:
    import networkx as nx
    import matplotlib.pyplot as plt
except ImportError:
    nx = None
    plt = None

# Remove pyvis import and HTML export function

def plot_transmission_graph(kg, start_node=None, highlight_paths=None, save_path=None):
    """
    Plot the knowledge graph using networkx and matplotlib.
    Optionally highlight paths starting from start_node (list of paths).
    If save_path is provided, save the plot to that file (e.g., 'transmission_graph.png').
    Nodes are colored by their 'type' field.
    Now supports bidirectional edges with sign '+/-'.
    """
    if nx is None or plt is None:
        print("networkx and matplotlib are required for plotting. Please install them with 'pip install networkx matplotlib'.")
        return
    G = nx.DiGraph()
    node_labels = {n["id"]: n["label"] for n in kg["nodes"]}
    node_types = {n["id"]: n.get("type", "METRIC") for n in kg["nodes"]}
    type_color = {"ORG": "purple", "RATE": "blue", "ASSET": "orange", "METRIC": "green"}
    for node in kg["nodes"]:
        G.add_node(node["id"], label=node["label"], type=node.get("type", "METRIC"))
    for edge in kg["edges"]:
        G.add_edge(edge["source"], edge["target"], sign=edge["sign"])
    pos = nx.spring_layout(G, seed=42)
    # Draw nodes by type
    for t, color in type_color.items():
        nodelist = [n for n in G.nodes if node_types[n] == t]
        nx.draw_networkx_nodes(G, pos, nodelist=nodelist, node_color=color, node_size=1200, label=t)
    # Draw all edges
    edge_colors = []
    for u, v, d in G.edges(data=True):
        if d['sign'] == '+':
            edge_colors.append('green')
        elif d['sign'] == '-':
            edge_colors.append('red')
        elif d['sign'] == '+/-':
            edge_colors.append('blue')  # Use blue for bidirectional
        else:
            edge_colors.append('gray')
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True, arrowstyle='-|>', arrowsize=20)
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)
    if highlight_paths:
        for path, sign in highlight_paths:
            edges_in_path = list(zip(path[:-1], path[1:]))
            nx.draw_networkx_edges(
                G, pos,
                edgelist=edges_in_path,
                edge_color='orange',
                width=3,
                arrows=True,
                arrowstyle='-|>',
                arrowsize=25
            )
    import matplotlib.patches as mpatches
    legend_handles = [mpatches.Patch(color=color, label=label) for label, color in type_color.items()]
    legend_handles.append(mpatches.Patch(color='green', label='Positive'))
    legend_handles.append(mpatches.Patch(color='red', label='Negative'))
    legend_handles.append(mpatches.Patch(color='blue', label='Bidirectional'))
    plt.legend(handles=legend_handles, title="Node Type", loc="best")
    plt.title("Monetary Policy Transmission Knowledge Graph")
    plt.axis('off')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        print(f"Graph saved to {save_path}")
    plt.show()

def get_transmission_paths(kg, start_node, shock_direction):
    """
    Return all transmission paths and their net sign from start_node to targets.
    Now supports bidirectional edges with sign '+/-'.
    """
    from collections import deque
    # Expanded targets to include more macroeconomic endpoints for richer transmission tracing
    targets = {"output", "prices", "SPX", "UST", "inflation", "inflation_expectations", "behavior_change", "supply_demand_imbalance", "global_costs", "production", "deflation"}
    results = []
    queue = deque()
    queue.append((start_node, [start_node], shock_direction))
    while queue:
        node, path, sign = queue.popleft()
        if node in targets and node != start_node:
            results.append((path, sign))
            continue
        for edge in kg["edges"]:
            if edge["source"] == node:
                edge_sign = edge["sign"]
                if edge_sign == "+/-":
                    queue.append((edge["target"], path + [edge["target"]], '+'))
                    queue.append((edge["target"], path + [edge["target"]], '-'))
                else:
                    next_sign = sign if edge_sign == "+" else ('-' if sign == '+' else '+')
                    queue.append((edge["target"], path + [edge["target"]], next_sign))
    return results

# --- New: Find all traces between two nodes ---
def all_traces_between(kg, source_node, desti_node, max_depth=8):
    """
    Return all possible traces (paths) from source_node to desti_node, with their net sign.
    Uses DFS up to max_depth to avoid infinite cycles.
    Returns: list of (path, net_sign)
    """
    results = []
    stack = [(source_node, [source_node], None)]  # (current, path, current_sign)
    while stack:
        node, path, sign = stack.pop()
        if node == desti_node and node != source_node:
            results.append((path, sign))
            continue
        if len(path) > max_depth:
            continue
        for edge in kg["edges"]:
            if edge["source"] == node:
                edge_sign = edge["sign"]
                if edge_sign == "+/-":
                    stack.append((edge["target"], path + [edge["target"]], '+'))
                    stack.append((edge["target"], path + [edge["target"]], '-'))
                else:
                    next_sign = sign if sign is not None and edge_sign == "+" else ('-' if sign == '+' and edge_sign == '-' else ('+' if sign == '-' and edge_sign == '-' else edge_sign))
                    stack.append((edge["target"], path + [edge["target"]], next_sign))
    return results

# --- New: Pyvis visualization ---
def plot_pyvis_transmission(kg, paths, output_html="transmission_pyvis.html"):
    """
    Plot the knowledge graph using pyvis, highlighting the given paths.
    paths: list of (path, sign)
    output_html: file to save the interactive visualization
    """
    try:
        from pyvis.network import Network
    except ImportError:
        print("pyvis is required for this function. Install with 'pip install pyvis'.")
        return
    node_labels = {n["id"]: n["label"] for n in kg["nodes"]}
    node_types = {n["id"]: n.get("type", "METRIC") for n in kg["nodes"]}
    type_color = {"ORG": "#a259f7", "RATE": "#4f8cff", "ASSET": "#ffb347", "METRIC": "#7be495", "POLICY": "#f7b7a3", "MEASURE": "#f7e3af", "SHOCK": "#f76e6e", "EVENT": "#b2a4ff", "ACTION": "#f9f871"}
    net = Network(height="800px", width="100%", directed=True, notebook=False)
    # Add nodes
    for node in kg["nodes"]:
        color = type_color.get(node.get("type", "METRIC"), "#cccccc")
        net.add_node(node["id"], label=node["label"], color=color)
    # Add edges
    for edge in kg["edges"]:
        color = "#7be495" if edge["sign"] == "+" else ("#f76e6e" if edge["sign"] == "-" else ("#4f8cff" if edge["sign"] == "+/-" else "#cccccc"))
        net.add_edge(edge["source"], edge["target"], color=color, arrows="to")
    # Highlight paths
    highlight_edges = set()
    for path, sign in paths:
        for i in range(len(path)-1):
            highlight_edges.add((path[i], path[i+1]))
    for edge in net.edges:
        if (edge["from"], edge["to"]) in highlight_edges:
            edge["color"] = "#ffa500"
            edge["width"] = 4
    net.show_buttons(filter_=['physics'])
    net.show(output_html, notebook=False)
    print(f"Pyvis interactive graph saved to {output_html}")

if __name__ == "__main__":
    print("\n--- Structured KG ---")
    from pprint import pprint
    pprint(sample_kg)
    print("\n--- Textual KG ---")
    print(kg_to_text(sample_kg))
    print("\n--- Transmission Steps: Expansionary Fiscal/Monetary Policy Increase ---")
    trace_transmission(sample_kg, start_node="accommodative_policy", shock_direction='+')
    print("\n--- Transmission Steps: Expansionary Fiscal/Monetary Policy Decrease ---")
    trace_transmission(sample_kg, start_node="accommodative_policy", shock_direction='-')

    # Plot the graph and highlight transmission paths for expansionary policy increase
    print("\n--- Plotting Transmission Graph (Expansionary Policy Increase) ---")
    paths_plus = get_transmission_paths(sample_kg, start_node="accommodative_policy", shock_direction='+')
    plot_transmission_graph(sample_kg, start_node="accommodative_policy", highlight_paths=paths_plus, save_path="transmission_graph.png")

    # Example: Find and plot all traces from accommodative_policy to inflation
    print("\n--- All Traces: Accommodative Policy to Inflation (Pyvis) ---")
    paths = all_traces_between(sample_kg, "accommodative_policy", "inflation")
    print(f"Found {len(paths)} paths from accommodative_policy to inflation.")
    # Print first 3 paths with labels and net sign
    node_labels = {n["id"]: n["label"] for n in sample_kg["nodes"]}
    for i, (path, sign) in enumerate(paths[:3]):
        label_path = " → ".join(node_labels[n] for n in path)
        print(f"Path {i+1}: {label_path} (net effect: {'↑' if sign == '+' else '↓' if sign == '-' else sign})")
    plot_pyvis_transmission(sample_kg, paths, output_html="accommodative_to_inflation.html")
