import sys
import os
import pandas as pd
import globals as gl
import product_module
import customer_module
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidgetItem
from PySide6.QtSvgWidgets import QSvgWidget
from qfluentwidgets import (NavigationItemPosition, MessageBox,
                            setTheme, Theme, MSFluentWindow, TitleLabel, LineEdit,
                            PrimaryPushButton, PushButton, TableWidget,
                            CaptionLabel, DoubleSpinBox, SpinBox, setThemeColor, ComboBox)
from qfluentwidgets import FluentIcon as FI


def load_language():
    """Reads the language code from settings.csv. Defaults to 'en'."""
    if os.path.exists(gl.SETT_FILE):
        try:
            df = pd.read_csv(gl.SETT_FILE, header=None)
            lang_row = df[df[0] == 'language']
            if not lang_row.empty:
                return str(lang_row.iloc[0, 1])
        except Exception as e:
            print(f"Warning: Could not read settings: {e}")
    return 'en'

def save_language(lang_code):
    """Saves the selected language code to settings.csv."""
    df = pd.DataFrame([['language', lang_code]])
    df.to_csv(gl.SETT_FILE, index=False, header=False)

CURRENT_LANG = load_language()

def load_translations():
    """Reads translations from translations.csv using pandas and builds the texts dictionary."""
    translations = {'en': {}, 'pl': {}}

    if os.path.exists(gl.LANG_FILE):
        try:
            df = pd.read_csv(gl.LANG_FILE)
            for _, row in df.iterrows():
                key = str(row['key'])
                en_text = str(row['en']) if pd.notna(row['en']) else key
                pl_text = str(row['pl']) if pd.notna(row['pl']) else key

                translations['en'][key] = en_text.replace('\\n', '\n')
                translations['pl'][key] = pl_text.replace('\\n', '\n')
        except Exception as e:
            print(f"Warning: Error reading translations file: {e}")
    else:
        print(f"Warning: Translation file not found at {gl.LANG_FILE}")

    return translations

TEXTS = load_translations()

def tr(key):
    """Returns the text in the currently loaded language. Returns the key if not found."""
    return TEXTS.get(CURRENT_LANG, TEXTS['en']).get(key, key)


def create_shopping_interface(parent=None):
    """Shopping module interface for customers"""
    widget = QWidget(parent)
    widget.setObjectName("shopping_interface")
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(20, 20, 20, 20)

    title = TitleLabel(tr('pos'))
    logo_widget = QSvgWidget(gl.LOGO_FILE)
    logo_widget.setFixedSize(256, 103)

    cust_id_input = LineEdit()
    cust_id_input.setPlaceholderText(tr('step1_ph'))

    product_name = LineEdit()
    product_name.setPlaceholderText(tr('step2_ph'))

    qty_label = CaptionLabel(tr('step3'))
    qty_input = SpinBox()
    qty_input.setRange(1, 100)

    buy_btn = PrimaryPushButton(tr('confirm_purch'), widget, FI.SHOPPING_CART)

    def process_purchase():
        cid = cust_id_input.text()
        prod = product_name.text()
        qty = qty_input.value()

        if cid and prod:
            success = customer_module.process_purchase_in_db(cid, prod, qty)

            if success:
                msg = MessageBox("Success", f"Purchased: {qty}x {prod} for ID: {cid}", widget)
                msg.exec()
                product_name.clear()
                qty_input.setValue(1)
            else:
                msg = MessageBox("Error", f"Customer ID: {cid} not found!", widget)
                msg.exec()

    buy_btn.clicked.connect(process_purchase)

    layout.addWidget(title)
    layout.addWidget(logo_widget, alignment=Qt.AlignCenter)
    layout.addWidget(CaptionLabel(tr('step1')))
    layout.addWidget(cust_id_input)
    layout.addSpacing(10)
    layout.addWidget(CaptionLabel(tr('step2')))
    layout.addWidget(product_name)
    layout.addSpacing(10)
    layout.addWidget(qty_label)
    layout.addWidget(qty_input)
    layout.addSpacing(5)
    layout.addWidget(buy_btn)
    layout.addStretch(1)

    return widget


def create_product_interface(parent=None):
    """Product Management Interface"""
    widget = QWidget(parent)
    widget.setObjectName("product_interface")
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(20, 20, 20, 20)

    title = TitleLabel(tr('product_man'))
    name_input = LineEdit()
    name_input.setPlaceholderText(tr('step2_ph'))
    price_label = CaptionLabel(tr('product_price'))
    price_input = DoubleSpinBox()
    price_input.setRange(0.01, 9999.99)

    amount_label = CaptionLabel(tr('product_amount'))
    amount_input = SpinBox()
    amount_input.setRange(1, 9999)
    amount_input.setValue(100)

    add_btn = PrimaryPushButton(tr('add_product'), widget, FI.ADD)

    table = TableWidget(widget)
    table.setColumnCount(5)
    table.setHorizontalHeaderLabels(['ID', 'Name', 'Price', 'Amount', 'Updated'])

    def load_products_to_table():
        products = product_module.get_all_products()
        for row_data in products:
            row = table.rowCount()
            table.insertRow(row)
            for col, data in enumerate(row_data):
                table.setItem(row, col, QTableWidgetItem(str(data)))

    load_products_to_table()

    remove_btn = PushButton(tr('rem_select'), widget, FI.DELETE)

    def add_product():
        name = name_input.text()
        price = price_input.value()
        amount = amount_input.value()

        if name:
            product_id, amount, updated = product_module.add_product_to_db(name, price, amount)

            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(product_id))
            table.setItem(row, 1, QTableWidgetItem(name))
            table.setItem(row, 2, QTableWidgetItem(str(price)))
            table.setItem(row, 3, QTableWidgetItem(str(amount)))
            table.setItem(row, 4, QTableWidgetItem(updated))

            name_input.clear()
            amount_input.setValue(100)

    def remove_product():
        current_row = table.currentRow()
        if current_row >= 0 and current_row < table.rowCount():
            product_id = table.item(current_row, 0).text()

            product_module.remove_product_from_db(product_id)
            table.removeRow(current_row)

            table.clearSelection()
            table.setCurrentCell(-1, -1)

    add_btn.clicked.connect(add_product)
    remove_btn.clicked.connect(remove_product)

    layout.addWidget(title)
    layout.addSpacing(30)
    layout.addWidget(name_input)
    layout.addSpacing(10)
    layout.addWidget(price_label)
    layout.addWidget(price_input)
    layout.addSpacing(10)
    layout.addWidget(amount_label)
    layout.addWidget(amount_input)
    layout.addSpacing(5)
    layout.addWidget(add_btn)
    layout.addSpacing(10)
    layout.addWidget(table)
    layout.addWidget(remove_btn)

    return widget


def create_customer_interface(parent=None):
    """Customer Management Interface"""
    widget = QWidget(parent)
    widget.setObjectName("customer_interface")
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(20, 20, 20, 20)

    title = TitleLabel(tr('customer_man'))

    customer_name = LineEdit()
    customer_name.setPlaceholderText(tr('full_name'))
    email_input = LineEdit()
    email_input.setPlaceholderText(tr('email'))
    phone_input = LineEdit()
    phone_input.setPlaceholderText(tr('phone'))
    street_input = LineEdit()
    street_input.setPlaceholderText(tr('street'))
    city_input = LineEdit()
    city_input.setPlaceholderText(tr('city'))
    country_input = LineEdit()
    country_input.setPlaceholderText(tr('country'))

    reg_btn = PrimaryPushButton(tr('reg_customer'), widget, FI.ADD_TO)

    table = TableWidget(widget)
    table.setColumnCount(7)
    table.setHorizontalHeaderLabels(['ID', 'Name', 'E-mail', 'Phone', 'Street', 'City', 'Country'])

    def load_customers_to_table():
        customers = customer_module.get_all_customers()
        for row_data in customers:
            row = table.rowCount()
            table.insertRow(row)
            for col, data in enumerate(row_data):
                table.setItem(row, col, QTableWidgetItem(str(data)))

    load_customers_to_table()

    remove_btn = PushButton(tr('rem_select'), widget, FI.DELETE)

    def register_customer():
        name = customer_name.text()
        email = email_input.text()
        phone = phone_input.text()
        street = street_input.text()
        city = city_input.text()
        country = country_input.text()

        if name:
            customer_id = customer_module.register_customer_in_db(name, email, phone, street, city, country)

            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(customer_id))
            table.setItem(row, 1, QTableWidgetItem(name))
            table.setItem(row, 2, QTableWidgetItem(email))
            table.setItem(row, 3, QTableWidgetItem(phone))
            table.setItem(row, 4, QTableWidgetItem(street))
            table.setItem(row, 5, QTableWidgetItem(city))
            table.setItem(row, 6, QTableWidgetItem(country))

            customer_name.clear()
            email_input.clear()
            phone_input.clear()
            street_input.clear()
            city_input.clear()
            country_input.clear()

    def remove_customer():
        current_row = table.currentRow()
        if current_row >= 0 and current_row < table.rowCount():
            customer_id = table.item(current_row, 0).text()

            customer_module.remove_customer_from_db(customer_id)
            table.removeRow(current_row)

            table.clearSelection()
            table.setCurrentCell(-1, -1)

    reg_btn.clicked.connect(register_customer)
    remove_btn.clicked.connect(remove_customer)

    layout.addWidget(title)
    layout.addSpacing(30)
    layout.addWidget(CaptionLabel(tr('per_data')))
    layout.addWidget(customer_name)
    layout.addWidget(email_input)
    layout.addWidget(phone_input)
    layout.addSpacing(10)
    layout.addWidget(CaptionLabel(tr('addr_data')))
    layout.addWidget(street_input)
    layout.addWidget(city_input)
    layout.addWidget(country_input)
    layout.addSpacing(5)
    layout.addWidget(reg_btn)
    layout.addSpacing(10)
    layout.addWidget(table)
    layout.addWidget(remove_btn)

    return widget


def create_settings_interface(parent=None):
    """Application Settings Interface"""
    widget = QWidget(parent)
    widget.setObjectName("settings_interface")
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(20, 20, 20, 20)

    title = TitleLabel(tr('settings'))
    lang_label = CaptionLabel(tr('select_lang'))

    lang_combo = ComboBox()
    lang_combo.addItem("English", userData="en")
    lang_combo.addItem("Polski", userData="pl")

    if CURRENT_LANG == 'pl':
        lang_combo.setCurrentIndex(1)
    else:
        lang_combo.setCurrentIndex(0)

    def change_language(index):
        lang_code = lang_combo.itemData(index)

        save_language(lang_code)

        msg = MessageBox(tr('settings'), tr('restart_req'), widget)
        msg.exec()

    lang_combo.currentIndexChanged.connect(change_language)

    layout.addWidget(title)
    layout.addSpacing(30)
    layout.addWidget(lang_label)
    layout.addWidget(lang_combo)
    layout.addStretch(1)

    return widget


def create_main_window():
    """Initializes and returns the main MSFluentWindow"""
    window = MSFluentWindow()
    window.resize(950, 750)
    window.setWindowTitle('Frog Package v1.0 — Żabka Online Admin')
    window.setWindowIcon(FI.BASKETBALL.icon())

    product_interface = create_product_interface(window)
    customer_interface = create_customer_interface(window)
    shopping_interface = create_shopping_interface(window)
    settings_interface = create_settings_interface(window)

    window.addSubInterface(shopping_interface, FI.SHOPPING_CART, tr('shop'))
    window.addSubInterface(product_interface, FI.TILES, tr('products'))
    window.addSubInterface(customer_interface, FI.PEOPLE, tr('customers'))
    window.addSubInterface(
        settings_interface,
        FI.SETTING,
        tr('settings'),
        position=NavigationItemPosition.BOTTOM
    )

    return window


def run_application():
    """Initializes and runs the Fluent GUI application."""
    app = QApplication(sys.argv)

    setThemeColor('#008B38')
    setTheme(Theme.AUTO)

    window = create_main_window()
    window.show()
    sys.exit(app.exec())