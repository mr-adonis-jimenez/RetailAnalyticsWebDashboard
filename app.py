import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from metrics import (
    total_revenue,
    average_order_value,
    top_customers,
    revenue_by_category,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Retail Analytics Dashboard", layout="wide", page_icon="📊")
st.title("📊 Retail Analytics Dashboard")

@st.cache_data
def load_data(path: str = "sample_orders.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(path, parse_dates=["order_date"])
        required = {"order_total", "customer_id", "category"}
        missing = required - set(df.columns)
        if missing:
            st.error(f"CSV missing required columns: {missing}")
            st.stop()
        logger.info("Loaded %d rows from %s", len(df), path)
        return df
    except FileNotFoundError:
        st.error(f"Data file not found: {path}")
        st.stop()
    except Exception as e:
        logger.exception("Failed to load data")
        st.error(f"Error loading data: {e}")
        st.stop()

uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
df = load_data() if uploaded is None else load_data(uploaded)

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${total_revenue(df):,.2f}")
col2.metric("Avg Order Value", f"${average_order_value(df):,.2f}")
col3.metric("Total Orders", f"{len(df):,}")

st.divider()

col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Revenue by Category")
    rev_cat = revenue_by_category(df)
    fig = px.bar(rev_cat, x="category", y="order_total", color="category")
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Top Customers")
    top = top_customers(df, limit=10)
    fig2 = px.bar(top, x="customer_id", y="order_total")
    st.plotly_chart(fig2, use_container_width=True)
