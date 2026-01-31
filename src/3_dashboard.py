import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "..", "data", "clean_transactions.csv")

st.set_page_config(page_title="Epstein Money Tracker", layout="wide")

st.title("💸 The Epstein Financial Graph")
st.markdown("**Tracking the flow of funds from the DOJ Archives**")

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

try:
    df = load_data()
    
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filters")
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

    # --- VISUALIZATION: SANKEY DIAGRAM ---
    st.subheader("Money Flow Visualization")
    
    # Add a slider to control graph density
    top_n = st.slider("Show Top N Entities", 5, 100, 20)
    
    # Aggregate data to prevent congestion
    # Extract the primary entity (first one listed)
    primary_entities = filtered_df['entities'].apply(
        lambda x: x.split(',')[0] if isinstance(x, str) and x.strip() else "Unknown"
    )
    
    # Count occurrences and take top N
    entity_counts = primary_entities.value_counts().head(top_n)
    
    sources = ["Epstein/Shell Co"] * len(entity_counts)
    targets = entity_counts.index.tolist()
    values = entity_counts.values.tolist()

    # Map labels to integers for Plotly
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
    st.plotly_chart(fig, width="stretch")

    # --- EVIDENCE TABLE ---
    st.subheader("Raw Evidence from Files")
    st.dataframe(filtered_df[['amount', 'entities', 'context']])

except FileNotFoundError:
    st.error("Data file not found. Please run '2_analyze.py' first.")