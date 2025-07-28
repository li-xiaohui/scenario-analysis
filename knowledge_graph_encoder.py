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
# --- New: Find all traces between two nodes, showing up/down arrows for each node ---
def all_traces_between(kg, source_node, desti_node, max_depth=8, topk=3):
    """
    Return all possible traces (paths) from source_node to desti_node, with their net sign and per-node effect.
    Uses DFS up to max_depth to avoid infinite cycles.
    Returns: list of (path_with_arrows, net_sign), where path_with_arrows is a list of "NodeLabel (arrow)".
    If topk is provided, only print the topk paths.
    """
    results = []
    stack = [(source_node, [source_node], [])]  # (current, path, list of signs)
    node_labels = {n["id"]: n["label"] for n in kg["nodes"]}
    while stack:
        node, path, signs = stack.pop()
        if node == desti_node and node != source_node:
            # Attach arrows to each node label except the first (source)
            path_with_arrows = []
            for i, n in enumerate(path):
                if i == 0:
                    path_with_arrows.append(node_labels[n])
                else:
                    arrow = signs[i-1] if i-1 < len(signs) else ""
                    path_with_arrows.append(f"{node_labels[n]} ({arrow})")
            # Net sign is the last arrow in the path
            net_sign = signs[-1] if signs else ""
            results.append((path_with_arrows, net_sign))
            if topk is not None and len(results) >= topk:
                break
            continue
        if len(path) > max_depth:
            continue
        for edge in kg["edges"]:
            if edge["source"] == node:
                edge_sign = edge["sign"]
                # Determine next possible sign(s) and arrow(s)
                if not signs:
                    # First edge: use edge sign
                    if edge_sign == "+/-":
                        stack.append((edge["target"], path + [edge["target"]], signs + ['↑']))
                        stack.append((edge["target"], path + [edge["target"]], signs + ['↓']))
                    else:
                        arrow = '↑' if edge_sign == '+' else '↓'
                        stack.append((edge["target"], path + [edge["target"]], signs + [arrow]))
                else:
                    prev = signs[-1]
                    if edge_sign == "+/-":
                        stack.append((edge["target"], path + [edge["target"]], signs + ['↑']))
                        stack.append((edge["target"], path + [edge["target"]], signs + ['↓']))
                    else:
                        if prev == '↑':
                            arrow = '↑' if edge_sign == '+' else '↓'
                        elif prev == '↓':
                            arrow = '↓' if edge_sign == '+' else '↑'
                        else:
                            arrow = prev  # fallback
                        stack.append((edge["target"], path + [edge["target"]], signs + [arrow]))
    # Print topk paths if requested
    if topk is not None:
        for i, (path_with_arrows, net_sign) in enumerate(results[:topk]):
            label_path = " → ".join(path_with_arrows)
            print(f"Path {i+1}: {label_path} (net effect: {net_sign})")
    return results

# --- New: Pyvis visualization with legend ---
def plot_pyvis_transmission(kg, paths, output_html="transmission_pyvis.html"):
    """
    Plot the knowledge graph using pyvis, highlighting the given paths.
    Displays a legend for node types and edge signs.
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
    type_color = {
        "ORG": "#a259f7", "RATE": "#4f8cff", "ASSET": "#ffb347", "METRIC": "#7be495",
        "POLICY": "#f7b7a3", "MEASURE": "#f7e3af", "SHOCK": "#f76e6e", "EVENT": "#b2a4ff", "ACTION": "#f9f871"
    }
    edge_color = {
        "+": "#7be495",    # green
        "-": "#f76e6e",    # red
        "+/-": "#4f8cff",  # blue
        "highlight": "#ffa500"  # orange (not used for color now)
    }
    net = Network(height="800px", width="100%", directed=True, notebook=False)
    # Determine which nodes are in highlighted paths
    highlight_nodes = set()
    highlight_edges = set()
    for path, sign in paths:
        for i in range(len(path)):
            highlight_nodes.add(path[i])
        for i in range(len(path)-1):
            highlight_edges.add((path[i], path[i+1]))
    # Add nodes
    for node in kg["nodes"]:
        color = type_color.get(node.get("type", "METRIC"), "#cccccc")
        if node["id"] in highlight_nodes:
            label = f"{node['label']}"
            font = {"size": 14, "bold": True}
        else:
            label = node["label"]
            font = {"size": 14}
        net.add_node(node["id"], label=label, color=color, font=font)
    # Add edges
    for edge in kg["edges"]:
        color = edge_color.get(edge["sign"], "#cccccc")
        width = 8 if (edge["source"], edge["target"]) in highlight_edges else 2
        net.add_edge(edge["source"], edge["target"], color=color, arrows="to", width=width)
    # Add legend as a fixed HTML box
    legend_html = """
    <div style="position: fixed; top: 20px; right: 20px; z-index: 9999; background: white; border: 1px solid #ccc; border-radius: 8px; padding: 12px; font-size: 14px; box-shadow: 2px 2px 8px #aaa;">
        <b>Legend</b><br>
        <u>Node Types</u><br>
        <span style="display:inline-block;width:12px;height:12px;background:#a259f7;border-radius:3px;margin-right:4px;"></span>ORG<br>
        <span style="display:inline-block;width:12px;height:12px;background:#4f8cff;border-radius:3px;margin-right:4px;"></span>RATE<br>
        <span style="display:inline-block;width:12px;height:12px;background:#ffb347;border-radius:3px;margin-right:4px;"></span>ASSET<br>
        <span style="display:inline-block;width:12px;height:12px;background:#7be495;border-radius:3px;margin-right:4px;"></span>METRIC<br>
        <span style="display:inline-block;width:12px;height:12px;background:#f7b7a3;border-radius:3px;margin-right:4px;"></span>POLICY<br>
        <span style="display:inline-block;width:12px;height:12px;background:#f7e3af;border-radius:3px;margin-right:4px;"></span>MEASURE<br>
        <span style="display:inline-block;width:12px;height:12px;background:#f76e6e;border-radius:3px;margin-right:4px;"></span>SHOCK<br>
        <span style="display:inline-block;width:12px;height:12px;background:#b2a4ff;border-radius:3px;margin-right:4px;"></span>EVENT<br>
        <span style="display:inline-block;width:12px;height:12px;background:#f9f871;border-radius:3px;margin-right:4px;"></span>ACTION<br>
        <u>Edge Signs</u><br>
        <span style="display:inline-block;width:18px;height:4px;background:#7be495;margin-right:4px;"></span>Positive (+)<br>
        <span style="display:inline-block;width:18px;height:4px;background:#f76e6e;margin-right:4px;"></span>Negative (-)<br>
        <span style="display:inline-block;width:18px;height:4px;background:#4f8cff;margin-right:4px;"></span>Positve/Negative (+/-)<br>
        <span style="display:inline-block;width:18px;height:4px;background:#000;margin-right:4px;border:2px solid #ffa500;"></span>Highlighted Path (bold)<br>
        <span style="font-weight:bold;">Bold label</span>: Node in highlighted path
    </div>
    """
    net.show_buttons(filter_=['physics'])
    net.save_graph(output_html)
    # Inject legend into the saved HTML
    try:
        with open(output_html, "r", encoding="utf-8") as f:
            html = f.read()
        if "</body>" in html:
            html = html.replace("</body>", legend_html + "\n</body>")
        else:
            html += legend_html
        with open(output_html, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        print(f"Could not inject legend: {e}")
    print(f"Pyvis interactive graph saved to {output_html}")

if __name__ == "__main__":
    print("\n--- Structured KG ---")
    from pprint import pprint
    # pprint(sample_kg)
    # print("\n--- Textual KG ---")
    # print(kg_to_text(sample_kg))
    
    
    print("\n--- All Traces: Policy to Inflation (Pyvis) ---")
    # paths = all_traces_between(sample_kg, "inflation_expectations", "inflation")    
    paths = all_traces_between(sample_kg, "supply_shock", "inflation", topk=5)

    # Print first 3 paths with labels and net sign
    # node_labels = {n["id"]: n["label"] for n in sample_kg["nodes"]}
    # for i, (path, sign) in enumerate(paths[:3]):
    #     label_path = " → ".join(node_labels[n] for n in path)
    #     print(f"Path {i+1}: {label_path} (net effect: {'↑' if sign == '+' else '↓' if sign == '-' else sign})")
    
    plot_pyvis_transmission(sample_kg, paths, output_html="inflation_expectation_to_inflation.html")
