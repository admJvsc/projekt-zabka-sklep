import os

import pandas as pd

import globals as gl
import manager_baz_danych
import utils


def product_frame() -> pd.DataFrame:
    manager_baz_danych.init_databases()

    if not os.path.exists(gl.PROD_FILE):
        return pd.DataFrame(columns=utils.columns.product)

    frame: pd.DataFrame = pd.read_excel(gl.PROD_FILE, dtype=str, keep_default_na=False)

    return frame.reindex(columns=utils.columns.product, fill_value="").fillna("")

def save_product_frame(frame: pd.DataFrame):
    normalized_frame: pd.DataFrame = frame.reindex(columns=utils.columns.product, fill_value="")
    normalized_frame.to_excel(gl.PROD_FILE, index=False)

def next_product_id(frame: pd.DataFrame) -> str:
    product_ids: list[str] = frame["ID"].astype(str).tolist()
    return utils.next_numeric_id(product_ids, 0)

def get_all_products() -> list[tuple]:
    products_frame: pd.DataFrame = product_frame()
    records: list[tuple] = []

    for _, row in products_frame.iterrows():
        records.append((
            str(row["ID"]).strip(),
            str(row["NAME"]).strip(),
            str(row["PRICE"]).strip(),   # Dodana cena
            str(row["AMOUNT"]).strip(),  # Zmienione na AMOUNT
            str(row["UPDATED"]).strip(),
        ))

    return records

def purchase_product(product_name: str, quantity: int) -> int:
    products_frame: pd.DataFrame = product_frame()
    normalized_name: str = product_name.strip().upper()

    row_mask: pd.Series = products_frame["NAME"].astype(str).str.upper() == normalized_name

    if not row_mask.any():
        return 2

    available_packages: int = int(products_frame.loc[row_mask, "AMOUNT"].iloc[0] or 0)

    if quantity <= 0 or available_packages < quantity:
        return 3

    products_frame.loc[row_mask, "AMOUNT"] = str(available_packages - quantity)
    products_frame.loc[row_mask, "UPDATED"] = utils.today()

    save_product_frame(products_frame)
    return 0


def add_product_to_db(name: str, price: float, amount: int) -> tuple[str, str, str]:
    products_frame: pd.DataFrame = product_frame()

    new_id = next_product_id(products_frame)
    updated_date = utils.today()

    success = manager_baz_danych.dodaj_produkt_do_bazy(new_id, name, price, amount, updated_date)
    if success:
        return new_id, str(amount), updated_date
    return "", "", ""