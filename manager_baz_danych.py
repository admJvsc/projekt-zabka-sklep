"""
Moduł manager_baz_danych.py

Funkcja: Obsługa dostarczonych plików bazy danych sklepu Żabka.
Zgodność z kolumnami:
- customer.csv (ID, NAME, E-MAIL, PHONE, CREATED, UPDATED)
- address.csv (ID, STREET, CITY, COUNTRY)
- products.xlsx (ID, PRODUCT, NO_PACKAGES_AVAILABLE, UPDATE)

Paradygmat - funkcyjny
Autor: Adam Jaszcz
"""

import os
from datetime import datetime
import pandas as pd
from globals import *

def init_databases():
    """
        Sprawdza, czy struktura baz danych i folderów istnieje.
        Jeśli pliki już są, nie modyfikuje ich zawartości.
    """
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

def dodaj_produkt_do_bazy(prod_id, prod_nazwa, liczba_opakowan, update_date=None):
    """
        Dodaje nowy produkt do pliku Excel zgodnie z Twoją strukturą kolumn.
        Kolumny: ID, PRODUCT, NO_PACKAGES_AVAILABLE, UPDATE

        Obsługa wyjątków: Zabezpieczenie przed błędami formatu liczb oraz blokadą pliku.
    """
    init_databases()
    try:
        p_id = str(prod_id).strip()
        p_name = str(prod_nazwa).strip().upper()
        p_liczba = int(liczba_opakowan)
        p_date = str(update_date) if update_date else datetime.now().strftime("%Y-%m-%d")

        if not p_id or not p_name:
            print("[BŁĄD] ID oraz nazwa produktu nie mogą być puste.")
            return False

        df = pd.read_excel(PROD_FILE, dtype={"ID": str})

        if p_id in df["ID"].values:
            print(f"[BŁĄD] Produkt o ID {p_id} już istnieje w bazie.")
            return False

        nowy_wiersz = pd.DataFrame([{
            "ID": p_id,
            "PRODUCT": p_name,
            "NO_PACKAGES_AVAILABLE": p_liczba,
            "UPDATE": p_date
        }])

        df = pd.concat([df, nowy_wiersz], ignore_index=True)
        df.to_excel(PROD_FILE, index=False)
        print(f"[Baza] Pomyślnie dodano produkt: {p_name}")
        return True

    except ValueError:
        print("[BŁĄD] Niepoprawny format danych. Ilość pakietów musi być liczbą całkowitą.")
        return False
    except PermissionError:
        print(f"[BŁĄD] Zamknij plik {PROD_FILE}. Jest otwarty w innym programie.")
        return False
    except Exception as e:
        print(f"[BŁĄD] Wystąpił błąd: {e}")
        return False


def usun_produkt_z_bazy(search_value, search_by="ID"):
    """
    Usuwa produkt z bazy na podstawie ID lub Nazwy towaru.
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
            print(f"[Baza] Usunięto produkt dopasowany do {search_by}: {val}")
            return True
        else:
            print(f"[Baza] Nie znaleziono produktu o {search_by}: {val}")
            return False

    except PermissionError:
        print(f"[Błąd Bazy] Nie można zmodyfikować {PROD_FILE}. Zamknij plik.")
        return False


def metryka():
    """
    Zlicza statystyki na podstawie plików.
    Zwraca liczbę klientów, liczbę rodzajów produktów oraz sumę wszystkich opakowań.
    """
    init_databases()
    try:
        df_cust = pd.read_csv(CUST_FILE)
        df_prod = pd.read_excel(PROD_FILE, dtype={"ID": str})

        metrics = {
            "total_klientow": len(df_cust),
            "total_typow_produktow": len(df_prod),
            "total_przedmiotow_dostepnych": int(df_prod["NO_PACKAGES_AVAILABLE"].sum()) if not df_prod.empty else 0
        }
        return metrics
    except Exception:
        return {"total_klientow": 0, "total_typow_produktow": 0, "total_przedmiotow_dostepnych": 0}
