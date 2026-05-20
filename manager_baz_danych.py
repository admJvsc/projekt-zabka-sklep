"""
manager_baz_danych.py Module

Function: Handles the provided Żabka store database files.
Compatible columns:
- customer.csv (ID, NAME, E-MAIL, PHONE, CREATED, UPDATED)
- address.csv (ID, STREET, CITY, COUNTRY)
- products.xlsx (ID, PRODUCT, NO_PACKAGES_AVAILABLE, UPDATE)

Paradigm - Functional
Author: Adam Jaszcz
"""

import os
from datetime import datetime
import pandas as pd
from globals import *

def init_databases():
    """
        Checks whether the database and folder structure exists.
        If the files already exist, their contents are not modified.
    """
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

def dodaj_produkt_do_bazy(prod_id, prod_nazwa, cena, liczba_opakowan, update_date=None):
    """
        Adds new product to the Excel file.
        Columns: ID, NAME, PRICE, AMOUNT, UPDATED
    """
    init_databases()
    try:
        p_id = str(prod_id).strip()
        p_name = str(prod_nazwa).strip().upper()
        p_cena = str(cena).strip()
        p_liczba = int(liczba_opakowan)
        p_date = str(update_date) if update_date else datetime.now().strftime("%Y-%m-%d")

        if not p_id or not p_name:
            print("[ERR] ID and product's name cannot be empty.")
            return False

        df = pd.read_excel(PROD_FILE, dtype={"ID": str})

        if p_id in df["ID"].values:
            print(f"[ERR] Product {p_id} already exists in the database.")
            return False

        nowy_wiersz = pd.DataFrame([{
            "ID": p_id,
            "NAME": p_name,
            "PRICE": p_cena,
            "AMOUNT": p_liczba,
            "UPDATED": p_date
        }])

        df = pd.concat([df, nowy_wiersz], ignore_index=True)
        df.to_excel(PROD_FILE, index=False)
        print(f"[DBase] Product: {p_name} successfully added")
        return True

    except ValueError:
        print("[ERR] Incorrect data format.")
        return False
    except PermissionError:
        print(f"[ERR] Close {PROD_FILE}. The file is opened in another program.")
        return False
    except Exception as e:
        print(f"[ERR] Error occured: {e}")
        return False


def usun_produkt_z_bazy(search_value, search_by="ID"):
    """
    Removes the product from the database based on the ID or a product's name.
    """
    init_databases()
    try:
        df = pd.read_excel(PROD_FILE, dtype={"ID": str})
        val = str(search_value).strip()

        if search_by == "ID":
            condition = df["ID"] == val
        else:
            condition = df["PRODUCT"].str.lower() == val.lower()

        if not df[condition].empty:
            df_filtered = df[~condition]
            df_filtered.to_excel(PROD_FILE, index=False)
            print(f"[DBase] Removed the product matching the {search_by}: {val}")
            return True
        else:
            print(f"[DBase] Product that matches {search_by}: {val} not found")
            return False

    except PermissionError:
        print(f"[Błąd Bazy] Nie można zmodyfikować {PROD_FILE}. Zamknij plik.")
        return False


def metryka():
    """
    Computes statistics based on files.
    Returns the number of customers, the number of product types,
    and the total number of packages.
    """
    init_databases()
    try:
        df_cust = pd.read_csv(CUST_FILE)
        df_prod = pd.read_excel(PROD_FILE, dtype={"ID": str})

        metrics = {
            "total_clients": len(df_cust),
            "total_product_types": len(df_prod),
            "total_available_products": int(df_prod["NO_PACKAGES_AVAILABLE"].sum()) if not df_prod.empty else 0
        }
        return metrics
    except Exception:
        return {"total_clients": 0, "total_product_types": 0, "total_available_products": 0}
