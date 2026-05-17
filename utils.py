from datetime import date

import pandas as pd

import globals as gl

class columns:
    customer: list[str] = ["ID", "NAME", "E-MAIL", "PHONE", "CREATED", "UPDATED"]
    address: list[str] = ["ID", "STREET", "CITY", "COUNTRY"]
    product: list[str] = ["ID", "NAME", "PRICE", "NO_PACKAGES_AVAILABLE", "UPDATED"]

class legacy_columns:
    product_amount: str = "AMOUNT"

def today() -> str:
    return date.today().isoformat()

def next_numeric_id(values: list[str], default_start: int) -> str:
    ids: list[int] = [int(value) for value in values if value.strip().isdigit()]
    next_id: int = max(ids, default=default_start) + 1
    return str(next_id)

def customer_frame() -> pd.DataFrame:
    frame: pd.DataFrame = pd.read_csv(gl.CUST_FILE, dtype=str, keep_default_na=False)
    return frame.reindex(columns=columns.customer, fill_value="")

def address_frame() -> pd.DataFrame:
    frame: pd.DataFrame = pd.read_csv(gl.ADDR_FILE, dtype=str, keep_default_na=False)
    return frame.reindex(columns=columns.address, fill_value="")

def save_customer_frame(frame: pd.DataFrame):
    normalized_frame: pd.DataFrame = frame.reindex(columns=columns.customer, fill_value="")
    normalized_frame.to_csv(gl.CUST_FILE, index=False)

def save_address_frame(frame: pd.DataFrame):
    normalized_frame: pd.DataFrame = frame.reindex(columns=columns.address, fill_value="")
    normalized_frame.to_csv(gl.ADDR_FILE, index=False)

def next_customer_id(frame: pd.DataFrame) -> str:
    customer_ids: list[str] = frame["ID"].astype(str).tolist()
    return next_numeric_id(customer_ids, 2000)

def has_customer(frame: pd.DataFrame, customer_id: str) -> bool:
    normalized_id: str = customer_id.strip()
    return normalized_id in frame["ID"].astype(str).tolist()
