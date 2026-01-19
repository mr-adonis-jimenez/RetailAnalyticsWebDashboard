import streamlit as st
import pandas as pd
from utils.metrics import (
    total_revenue,
    average_order_value,
    top_customers,
    revenue_by_category
)

st.set_page_config(
    page_title="Retail Analytics Dashboard",
    layout="wide"
)

st.title("📊 Retail Analytics Dashboard")

# Load data
df = pd.read_csv("data/sample_orders.csv")

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${total_revenue(df):,.2f}")
col2.metric("Avg Order Value", f"${average_order_value(df):,.2f}")
col3.metric("Total Orders", len(df))

st.divider()

# Charts
st.subheader("Revenue by Product Category")
category_df = revenue_by_category(df)
st.bar_chart(category_df.set_index("category"))

st.subheader("Top Customers by Revenue")
top_df = top_customers(df)
st.dataframe(top_df)

st.divider()

# Insights
with open("insights/business_insights.md") as f:
    st.subheader("📌 Business Insights")
    st.markdown(f.read())
