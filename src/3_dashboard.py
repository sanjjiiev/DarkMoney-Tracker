import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "..", "data", "clean_transactions.csv")

st.set_page_config(page_title="Financial Intelligence Dashboard", layout="wide")

st.title("Financial Intelligence Dashboard")
st.markdown("### DOJ Archive Transaction Analysis")

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

try:
    df = load_data()
    
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Search & Filters")
    search_term = st.sidebar.text_input("Search Entity (e.g., 'Harvard', 'Bank')")
    
    if search_term:
        filtered_df = df[df['entities'].str.contains(search_term, case=False, na=False)]
    else:
        filtered_df = df
        
    # --- METRICS ---
    col1, col2 = st.columns(2)
    col1.metric("Transactions Found", len(filtered_df))
    # Simple logic to count unique entities mentioned
    unique_entities = len(pd.unique(filtered_df['entities'].str.split(', ', expand=True).stack()))
    col2.metric("Unique Entities Involved", unique_entities)

    # --- VISUALIZATION SELECTION ---
    st.divider()
    
    col_ctrl1, col_ctrl2 = st.columns([1, 3])
    
    with col_ctrl1:
        st.subheader("Graph Settings")
        top_n = st.slider("Max Entities Displayed", 5, 100, 30)
        graph_type = st.radio("Visualization Type", ["Network Graph (OSINT)", "Sankey Flow", "Bar Chart"])

    # Data Preparation
    # Extract the primary entity (first one listed)
    primary_entities = filtered_df['entities'].apply(
        lambda x: x.split(',')[0] if isinstance(x, str) and x.strip() else "Unknown"
    )
    
    entity_counts = primary_entities.value_counts().head(top_n)
    
    with col_ctrl2:
        if graph_type == "Network Graph (OSINT)":
            st.subheader("Entity Relationship Network")
            
            # Create NetworkX Graph
            G = nx.Graph()
            central_node = "Source Funds"
            G.add_node(central_node, size=20)
            
            for entity, count in entity_counts.items():
                G.add_node(entity, size=count)
                G.add_edge(central_node, entity, weight=count)
            
            # Layout
            pos = nx.spring_layout(G, k=0.5, iterations=50)
            
            # Edges Trace
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines')
            
            # Nodes Trace
            node_x = []
            node_y = []
            node_text = []
            node_size = []
            
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(f"{node}")
                if node == central_node:
                    node_size.append(25)
                else:
                    # Scale size slightly
                    node_size.append(10 + (entity_counts.get(node, 1) * 0.5))

            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                textposition="top center",
                marker=dict(
                    showscale=True,
                    colorscale='YlGnBu',
                    size=node_size,
                    color=node_size,
                    line_width=2))
            
            fig = go.Figure(data=[edge_trace, node_trace],
                            layout=go.Layout(
                                showlegend=False,
                                hovermode='closest',
                                margin=dict(b=0,l=0,r=0,t=0),
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                            )
            st.plotly_chart(fig, use_container_width=True)

        elif graph_type == "Sankey Flow":
            st.subheader("Fund Flow Diagram")
            sources = ["Source Funds"] * len(entity_counts)
            targets = entity_counts.index.tolist()
            values = entity_counts.values.tolist()

            all_nodes = list(set(sources + targets))
            node_map = {node: i for i, node in enumerate(all_nodes)}
            
            link = dict(
                source=[node_map[s] for s in sources],
                target=[node_map[t] for t in targets],
                value=values
            )
            
            node = dict(
                label=all_nodes,
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5)
            )
            
            fig = go.Figure(data=[go.Sankey(node=node, link=link)])
            st.plotly_chart(fig, use_container_width=True)
            
        elif graph_type == "Bar Chart":
            st.subheader("Top Entities by Frequency")
            fig = px.bar(
                x=entity_counts.values,
                y=entity_counts.index,
                orientation='h',
                labels={'x': 'Transaction Count', 'y': 'Entity'},
                color=entity_counts.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

    # --- EVIDENCE TABLE ---
    st.divider()
    st.subheader("Transaction Ledger")
    st.dataframe(
        filtered_df[['amount', 'entities', 'context']], 
        use_container_width=True,
        hide_index=True
    )

except FileNotFoundError:
    st.error("Data file not found. Please run '2_analyze.py' first.")