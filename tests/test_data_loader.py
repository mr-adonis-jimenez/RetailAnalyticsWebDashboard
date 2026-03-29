import pytest
import pandas as pd
import tempfile
import os
from data_loader import load_csv


def test_load_csv_basic():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("order_total,customer_id,category\n100,C1,Electronics\n200,C2,Clothing\n")
        tmp_path = f.name
    try:
        df = load_csv(tmp_path)
        assert len(df) == 2
        assert "order_total" in df.columns
    finally:
        os.unlink(tmp_path)


def test_load_csv_file_not_found():
    with pytest.raises(Exception):
        load_csv("nonexistent_file.csv")


def test_load_csv_returns_dataframe():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("a,b\n1,2\n")
        tmp_path = f.name
    try:
        result = load_csv(tmp_path)
        assert isinstance(result, pd.DataFrame)
    finally:
        os.unlink(tmp_path)
