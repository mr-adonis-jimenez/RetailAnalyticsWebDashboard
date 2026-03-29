import pytest
import pandas as pd
from metrics import total_revenue, average_order_value, top_customers, revenue_by_category


def test_total_revenue(sample_df):
    assert total_revenue(sample_df) == pytest.approx(600.0)


def test_total_revenue_empty():
    df = pd.DataFrame({"order_total": []})
    assert total_revenue(df) == 0.0


def test_average_order_value(sample_df):
    assert average_order_value(sample_df) == pytest.approx(120.0)


def test_top_customers_returns_correct_count(sample_df):
    result = top_customers(sample_df, limit=2)
    assert len(result) == 2


def test_top_customers_sorted_descending(sample_df):
    result = top_customers(sample_df, limit=3)
    totals = result["order_total"].tolist()
    assert totals == sorted(totals, reverse=True)


def test_top_customers_columns(sample_df):
    result = top_customers(sample_df)
    assert "customer_id" in result.columns
    assert "order_total" in result.columns


def test_revenue_by_category(sample_df):
    result = revenue_by_category(sample_df)
    assert set(result["category"]) == {"Electronics", "Clothing", "Food"}


def test_revenue_by_category_totals(sample_df):
    result = revenue_by_category(sample_df)
    electronics = result[result["category"] == "Electronics"]["order_total"].values[0]
    assert electronics == pytest.approx(350.0)
