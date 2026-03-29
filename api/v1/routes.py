"""REST API v1 blueprint for Retail Analytics Dashboard.

Endpoints:
    GET  /api/v1/health           - Health check
    GET  /api/v1/metrics          - Dashboard KPI metrics
    GET  /api/v1/orders           - List orders (paginated)
    GET  /api/v1/orders/<id>      - Single order
    GET  /api/v1/analytics/revenue  - Revenue breakdown by category
    GET  /api/v1/analytics/trends   - Monthly sales trends
"""

import logging
import pandas as pd
from flask import Blueprint, jsonify, request, current_app

logger = logging.getLogger(__name__)

api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")

_df_cache = None


def _get_data() -> pd.DataFrame:
    """Load and cache the orders dataframe."""
    global _df_cache
    if _df_cache is None:
        try:
            _df_cache = pd.read_csv("sample_orders.csv")
        except FileNotFoundError:
            _df_cache = pd.DataFrame(columns=["order_id", "customer_id", "category", "order_total", "order_date"])
    return _df_cache


def _error(message: str, status: int = 400):
    return jsonify({"error": message, "status": status}), status


# ── Health ────────────────────────────────────────────────────────────────────

@api_v1.get("/health")
def health():
    return jsonify({"status": "healthy", "version": "1.0.0"})


# ── Metrics ───────────────────────────────────────────────────────────────────

@api_v1.get("/metrics")
def get_metrics():
    df = _get_data()
    if df.empty:
        return _error("No data available", 503)
    return jsonify({
        "total_revenue": round(float(df["order_total"].sum()), 2),
        "average_order_value": round(float(df["order_total"].mean()), 2),
        "total_orders": int(len(df)),
        "unique_customers": int(df["customer_id"].nunique()) if "customer_id" in df.columns else None,
    })


# ── Orders ────────────────────────────────────────────────────────────────────

@api_v1.get("/orders")
def list_orders():
    df = _get_data()
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(100, request.args.get("per_page", 20, type=int))
    total = len(df)
    start = (page - 1) * per_page
    end = start + per_page
    records = df.iloc[start:end].to_dict(orient="records")
    return jsonify({
        "data": records,
        "pagination": {"page": page, "per_page": per_page, "total": total, "pages": -(-total // per_page)},
    })


@api_v1.get("/orders/<order_id>")
def get_order(order_id):
    df = _get_data()
    if "order_id" not in df.columns:
        return _error("order_id column not present in dataset", 404)
    match = df[df["order_id"].astype(str) == str(order_id)]
    if match.empty:
        return _error(f"Order {order_id} not found", 404)
    return jsonify({"data": match.iloc[0].to_dict()})


# ── Analytics ─────────────────────────────────────────────────────────────────

@api_v1.get("/analytics/revenue")
def revenue_analytics():
    df = _get_data()
    if "category" not in df.columns:
        return _error("category column not found", 422)
    rev = df.groupby("category")["order_total"].agg(["sum", "mean", "count"]).reset_index()
    rev.columns = ["category", "total_revenue", "avg_order", "order_count"]
    rev = rev.sort_values("total_revenue", ascending=False)
    return jsonify({"data": rev.round(2).to_dict(orient="records")})


@api_v1.get("/analytics/trends")
def sales_trends():
    df = _get_data()
    if "order_date" not in df.columns:
        return _error("order_date column not found", 422)
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month")["order_total"].agg(["sum", "count"]).reset_index()
    monthly.columns = ["month", "total_revenue", "order_count"]
    return jsonify({"data": monthly.sort_values("month").round(2).to_dict(orient="records")})
