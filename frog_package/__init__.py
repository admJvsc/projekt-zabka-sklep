"""
Frog Package

DESCRIPTION
A GUI-based application designed for managing customer databases
and product inventory. It provides a POS (Point of Sale) interface
for processing sales with automatic database updates and file generation
in CSV, XLSX, and TXT formats.

PACKAGE CONTAINS:
- gui: Main graphical interface based on qfluentwidgets
- globals: Global variables and file paths
- manager_baz_danych: Database I/O operations and validation
- product_module: Inventory and product logic
- customer_module: Customer database logic
- utils: Helper functions for DataFrames

AUTHORS:
Adam J, Kacper K, Dawid Ch
"""

__all__ = [
    "gui",
    "globals",
    "manager_baz_danych",
    "product_module",
    "customer_module",
    "utils"
]