import streamlit as st
import json
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any
import pandas as pd

def load_knowledge_graph(file_path: str) -> Dict[str, Any]:
    """Load the knowledge graph from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON file: {e}")
        return {}
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return {}

def extract_graph_sections(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Extract all graph sections that have machine_readable data."""
    sections = {}
    
    # Skip metadata
    for key, value in data.items():
        if key == "metadata":
            continue
            
        if isinstance(value, dict):
            # Check if this is a direct graph section
            if "machine_readable" in value:
                sections[key] = value["machine_readable"]
            else:
                # Check nested sections
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict) and "machine_readable" in sub_value:
                        section_name = f"{key} - {sub_key}"
                        sections[section_name] = sub_value["machine_readable"]
    
    return sections

def create_network_graph(nodes: List[Dict], edges: List[Dict]) -> nx.Graph:
    """Create a NetworkX directed graph from nodes and edges."""
    G = nx.DiGraph()
    node_ids = set()
    # Add nodes
    for node in nodes:
        G.add_node(node['id'], 
                  label=node['label'], 
                  type=node.get('type', 'Unknown'))
        node_ids.add(node['id'])
    # Add edges, only if both source and target exist as nodes
    for edge in edges:
        if edge['source'] in node_ids and edge['target'] in node_ids:
            G.add_edge(edge['source'], 
                      edge['target'], 
                      relation=edge['relation'])
    return G

def create_plotly_network_graph(G: nx.Graph) -> go.Figure:
    """Create a Plotly network graph visualization with arrows for directed edges."""
    # Calculate layout
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    # Extract node positions
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_type = G.nodes[node].get('type', 'Unknown')
        node_text.append(f"{G.nodes[node]['label']}<br>Type: {node_type}")
        # Color nodes by type
        if 'Valuation' in node_type or 'Method' in node_type:
            node_colors.append('#1f77b4')  # Blue
        elif 'Risk' in node_type or 'Metric' in node_type:
            node_colors.append('#ff7f0e')  # Orange
        elif 'Financial' in node_type or 'Ratio' in node_type:
            node_colors.append('#2ca02c')  # Green
        elif 'Market' in node_type or 'Data' in node_type:
            node_colors.append('#d62728')  # Red
        else:
            node_colors.append('#9467bd')  # Purple
    
    # Create node trace
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[G.nodes[node]['label'] for node in G.nodes()],
        textposition="middle center",
        marker=dict(
            size=20,
            color=node_colors,
            line=dict(width=2, color='white')
        ),
        textfont=dict(size=10)
    )
    
    # Create edge trace
    edge_x = []
    edge_y = []
    edge_label_x = []
    edge_label_y = []
    edge_label_text = []
    arrow_annotations = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        # For edge label
        edge_label_x.append((x0 + x1) / 2)
        edge_label_y.append((y0 + y1) / 2)
        edge_label_text.append(G.edges[edge]['relation'])
        # Offset arrow endpoint slightly towards the source to avoid overlap with node marker
        dx = x1 - x0
        dy = y1 - y0
        length = (dx**2 + dy**2) ** 0.5
        if length != 0:
            offset = 0.08  # adjust this value for more/less offset
            x1_arrow = x1 - dx * offset / length
            y1_arrow = y1 - dy * offset / length
        else:
            x1_arrow, y1_arrow = x1, y1
        # Add arrow annotation with improved visibility
        arrow_annotations.append(dict(
            x=x1_arrow, y=y1_arrow, ax=x0, ay=y0,
            xref='x', yref='y', axref='x', ayref='y',
            showarrow=True, arrowhead=2, arrowsize=2, arrowwidth=2, arrowcolor='#888',
            standoff=5, opacity=0.9, text=' '
        ))

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Add edge label trace
    edge_label_trace = go.Scatter(
        x=edge_label_x,
        y=edge_label_y,
        mode='text',
        text=edge_label_text,
        textposition='top center',
        hoverinfo='text',
        showlegend=False,
        textfont=dict(size=10, color='#444')
    )

    # Create figure with arrow annotations
    fig = go.Figure(data=[edge_trace, node_trace, edge_label_trace],
                   layout=go.Layout(
                       title='Knowledge Graph Visualization',
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=600,
                       annotations=arrow_annotations
                   ))
    return fig

def display_graph_statistics(G: nx.Graph):
    """Display graph statistics."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Nodes", len(G.nodes()))
    
    with col2:
        st.metric("Edges", len(G.edges()))
    
    with col3:
        st.metric("Density", f"{nx.density(G):.3f}")
    
    with col4:
        if len(G.nodes()) > 1:
            st.metric("Avg Degree", f"{sum(dict(G.degree()).values()) / len(G.nodes()):.1f}")
        else:
            st.metric("Avg Degree", "0")

def display_node_types(G: nx.Graph):
    """Display node types distribution."""
    type_counts = {}
    for node in G.nodes():
        node_type = G.nodes[node].get('type', 'Unknown')
        type_counts[node_type] = type_counts.get(node_type, 0) + 1
    
    if type_counts:
        df = pd.DataFrame(list(type_counts.items()), columns=['Type', 'Count'])
        fig = px.bar(df, x='Type', y='Count', title='Node Types Distribution')
        st.plotly_chart(fig, use_container_width=True)

def main():
    st.set_page_config(
        page_title="Knowledge Graph Visualizer",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Knowledge Graph Visualizer")
    st.markdown("Explore the financial knowledge graph with interactive visualizations")
    
    # Load data
    data = load_knowledge_graph("data/knowledge_graph_v2_fixed.json")
    
    if not data:
        st.error("Failed to load knowledge graph data. Please check the JSON file.")
        return
    
    # Extract graph sections
    sections = extract_graph_sections(data)
    
    if not sections:
        st.error("No graph sections found in the data.")
        return
    
    # Sidebar for selection
    st.sidebar.header("Graph Selection")
    
    # Create dropdown options
    section_options = list(sections.keys())
    selected_section = st.sidebar.selectbox(
        "Select a graph section:",
        section_options,
        index=0
    )
    
    # Display selected section info
    st.sidebar.markdown(f"**Selected:** {selected_section}")
    
    # Get the selected graph data
    graph_data = sections[selected_section]
    
    # Create and display the graph
    if 'nodes' in graph_data and 'edges' in graph_data:
        # Create NetworkX graph
        G = create_network_graph(graph_data['nodes'], graph_data['edges'])
        
        # Display statistics
        st.subheader("📈 Graph Statistics")
        display_graph_statistics(G)
        
        # Display node types distribution
        st.subheader("🏷️ Node Types Distribution")
        display_node_types(G)
        
        # Display the network graph
        st.subheader("🕸️ Network Visualization")
        fig = create_plotly_network_graph(G)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display detailed information
        st.subheader("📋 Graph Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Nodes:**")
            nodes_df = pd.DataFrame(graph_data['nodes'])
            st.dataframe(nodes_df, use_container_width=True)
        
        with col2:
            st.markdown("**Edges:**")
            edges_df = pd.DataFrame(graph_data['edges'])
            st.dataframe(edges_df, use_container_width=True)
    
    else:
        st.error("Selected section does not contain valid graph data.")

if __name__ == "__main__":
    main() 