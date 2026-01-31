import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
    
    # --- FILTERS (MAIN PAGE) ---
    col_search, col_top = st.columns([3, 1])
    search_term = col_search.text_input("Search Entity", placeholder="Type to filter (e.g., 'Harvard')...")
    top_n = col_top.slider("Max Entities", 5, 100, 15)
    
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

    st.divider()
    
    # --- DATA PREPARATION ---
    # Extract the primary entity (first one listed)
    primary_entities = filtered_df['entities'].apply(
        lambda x: x.split(',')[0] if isinstance(x, str) and x.strip() else "Unknown"
    )
    
    entity_counts = primary_entities.value_counts().head(top_n)
    
    # --- VISUALIZATIONS ---
    
    # 1. Sankey Diagram (Full Width)
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
    
    fig_sankey = go.Figure(data=[go.Sankey(node=node, link=link)])
    st.plotly_chart(fig_sankey, use_container_width=True)

    # 2. Bar Chart & Treemap (Side by Side)
    col_viz1, col_viz2 = st.columns(2)
    
    with col_viz1:
        st.subheader("Top Entities (Bar)")
        fig_bar = px.bar(
            x=entity_counts.values,
            y=entity_counts.index,
            orientation='h',
            labels={'x': 'Transaction Count', 'y': 'Entity'},
            color=entity_counts.values,
            color_continuous_scale='Viridis'
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_viz2:
        st.subheader("Entity Distribution (Treemap)")
        # Prepare data for Treemap
        treemap_data = pd.DataFrame({
            'Entity': entity_counts.index,
            'Count': entity_counts.values,
            'Parent': ['All Transactions'] * len(entity_counts)
        })
        fig_tree = px.treemap(
            treemap_data,
            path=['Parent', 'Entity'],
            values='Count',
            color='Count',
            color_continuous_scale='RdBu'
        )
        st.plotly_chart(fig_tree, use_container_width=True)

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