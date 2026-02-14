def total_revenue(df):
    return df["order_total"].sum()


def average_order_value(df):
    return df["order_total"].mean()


def top_customers(df, limit=10):
    return (
        df.groupby("customer_id")["order_total"]
        .sum()
        .sort_values(ascending=False)
        .head(limit)
        .reset_index()
    )


def revenue_by_category(df):
    return (
        df.groupby("category")["order_total"]
        .sum()
        .reset_index()
    )
