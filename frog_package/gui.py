import sys
import os
import ctypes #for app icon in Windows taskbar
import pandas as pd
from frog_package import globals as gl
from frog_package import product_module, customer_module, manager_baz_danych
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import QIcon
from qfluentwidgets import (NavigationItemPosition, MessageBox, MSFluentWindow,
                            setTheme, Theme, setThemeColor, isDarkTheme, LineEdit,
                            PrimaryPushButton, PushButton, HyperlinkButton, TableWidget,
                            DoubleSpinBox, SpinBox, ComboBox, InfoBar, InfoBarPosition,
                            TitleLabel, CaptionLabel, SubtitleLabel, BodyLabel)
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
            print(f"[ERROR] Could not read settings: {e}")
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
            print(f"[ERROR] Error reading translations file: {e}")
    else:
        print(f"[ERROR] Translation file not found at {gl.LANG_FILE}")

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
    buy_btn.setEnabled(False)

    def check_purchase_inputs():
        has_cid = bool(cust_id_input.text().strip())
        has_prod = bool(product_name.text().strip())

        buy_btn.setEnabled(has_cid and has_prod)

    cust_id_input.textChanged.connect(check_purchase_inputs)
    product_name.textChanged.connect(check_purchase_inputs)

    def process_purchase():
        cid = cust_id_input.text().strip()
        prod = product_name.text().strip()
        qty = qty_input.value()

        if cid and prod:
            status = customer_module.process_purchase_in_db(cid, prod, qty)

            if status == 0:
                msg = MessageBox(tr('success'), f"{tr('purchased')}: {qty}x {prod} {tr('for')} ID: {cid}", widget)
                msg.cancelButton.hide()
                msg.yesButton.setText('OK')
                msg.exec()
                product_name.clear()
                qty_input.setValue(1)
            elif status == 1:
                InfoBar.error(
                    title=tr('error'), content=f"{tr('customer_not_found')}: {cid}",
                    orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=5000, parent=widget
                )
            elif status == 2:
                InfoBar.error(
                    title=tr('error'), content=f"{tr('product')} '{prod}' {tr('not_exists_in_base')}!",
                    orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=5000, parent=widget
                )
            elif status == 3:
                InfoBar.error(
                    title=tr('error'), content=f"{tr('insufficient_stoct')} '{prod}'!",
                    orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=5000, parent=widget
                )

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
    add_btn.setEnabled(False)

    def check_product_inputs():
        has_name = bool(name_input.text().strip())
        add_btn.setEnabled(has_name)

    name_input.textChanged.connect(check_product_inputs)

    table = TableWidget(widget)
    table.setColumnCount(5)
    table.setHorizontalHeaderLabels(['ID', 'Name', 'Price', 'Amount', 'Updated'])

    def load_products_to_table():
        table.setRowCount(0)
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
            product_id, final_amount, updated = product_module.add_product_to_db(name, price, amount)

            if product_id:
                row = table.rowCount()
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(product_id))
                table.setItem(row, 1, QTableWidgetItem(name))
                table.setItem(row, 2, QTableWidgetItem(str(price)))
                table.setItem(row, 3, QTableWidgetItem(str(final_amount)))
                table.setItem(row, 4, QTableWidgetItem(updated))

                name_input.clear()
                amount_input.setValue(100)

                InfoBar.success(
                    title=tr('success'), content=f"{tr('added_product')}: {name}",
                    orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=widget
                )
            else:
                InfoBar.error(
                    title=tr('error'), content=tr('error_add_product'),
                    orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=5000, parent=widget
                )

    def remove_product():
        current_row = table.currentRow()
        if current_row >= 0 and current_row < table.rowCount():
            product_id = table.item(current_row, 0).text()

            manager_baz_danych.usun_produkt_z_bazy(product_id)
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

    original_show_event = widget.showEvent
    def on_show(event):
        load_products_to_table()
        original_show_event(event)
    widget.showEvent = on_show

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
    customer_name.textChanged.connect(lambda: customer_name.setError(False))
    email_input = LineEdit()
    email_input.setPlaceholderText(tr('email'))
    phone_input = LineEdit()
    phone_input.setPlaceholderText(tr('phone'))
    email_input.textChanged.connect(lambda: (email_input.setError(False), phone_input.setError(False)))
    phone_input.textChanged.connect(lambda: (email_input.setError(False), phone_input.setError(False)))
    street_input = LineEdit()
    street_input.setPlaceholderText(tr('street'))
    city_input = LineEdit()
    city_input.setPlaceholderText(tr('city'))
    country_input = LineEdit()
    country_input.setPlaceholderText(tr('country'))
    country_input.textChanged.connect(lambda: country_input.setError(False))

    reg_btn = PrimaryPushButton(tr('reg_customer'), widget, FI.ADD_TO)
    reg_btn.setEnabled(False)

    def check_customer_inputs():
        has_any_text = bool(
            customer_name.text().strip() or
            email_input.text().strip() or
            phone_input.text().strip() or
            street_input.text().strip() or
            city_input.text().strip() or
            country_input.text().strip()
        )
        reg_btn.setEnabled(has_any_text)

    customer_name.textChanged.connect(check_customer_inputs)
    email_input.textChanged.connect(check_customer_inputs)
    phone_input.textChanged.connect(check_customer_inputs)
    street_input.textChanged.connect(check_customer_inputs)
    city_input.textChanged.connect(check_customer_inputs)
    country_input.textChanged.connect(check_customer_inputs)

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
        name = customer_name.text().strip()
        email = email_input.text().strip()
        phone = phone_input.text().strip()
        street = street_input.text().strip()
        city = city_input.text().strip()
        country = country_input.text().strip()

        if not name or not country:
            if not name:
                customer_name.setError(True)
            if not country:
                country_input.setError(True)

            InfoBar.warning(
                title=tr('missing_data'),
                content=tr('fill_name_country'),
                orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4500, parent=widget
            )
            return

        if not email and not phone:
            email_input.setError(True)
            phone_input.setError(True)
            InfoBar.warning(
                title=tr('missing_contact_info'),
                content=tr('provide_email_or_phone'),
                orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4500, parent=widget
            )
            return

        if email and "@" not in email:
            email_input.setError(True)
            email_input.setFocus()
            InfoBar.error(
                title=tr('incorrect_format'),
                content=tr('incorrect_email'),
                orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4500, parent=widget
            )
            return

        if phone:
            clean_phone = phone.replace(" ", "").replace("+", "").replace("-", "")
            if not clean_phone.isdigit():
                phone_input.setError(True)
                phone_input.setFocus()
                InfoBar.error(
                    title=tr('incorrect_format'),
                    content=tr('incorrect_phone'),
                    orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4500, parent=widget
                )
                return

        customer_id = customer_module.register_customer_in_db(name, email, phone, street, city, country)

        if customer_id:
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
            customer_name.setError(False)
            email_input.clear()
            email_input.setError(False)
            phone_input.clear()
            phone_input.setError(False)
            street_input.clear()
            city_input.clear()
            country_input.clear()
            country_input.setError(False)

            InfoBar.success(
                title=tr('success'),
                content=f"{tr('reg_customer_cucces')}: {name} (ID: {customer_id})",
                orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=widget
            )
        else:
            InfoBar.error(
                title=tr('error'),
                content=tr('error_save_customer'),
                orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=5000, parent=widget
            )

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
        msg.cancelButton.hide()
        msg.yesButton.setText('OK')
        msg.exec()

    lang_combo.currentIndexChanged.connect(change_language)

    layout.addWidget(title)
    layout.addSpacing(30)
    layout.addWidget(lang_label)
    layout.addWidget(lang_combo)
    layout.addSpacing(50)
    info_title = SubtitleLabel(tr('app_info'))
    layout.addWidget(info_title)
    layout.addSpacing(10)
    version_label = BodyLabel(f'{tr('version')} 1.0')
    layout.addWidget(version_label)
    layout.addSpacing(5)
    repo_layout = QHBoxLayout()
    repo_btn = HyperlinkButton("https://github.com/admJvsc/projekt-zabka-sklep/tree/main", f'📦 {tr('repo_on_gh')}')
    repo_layout.addWidget(repo_btn)
    repo_layout.addStretch(1)
    layout.addLayout(repo_layout)
    layout.addSpacing(20)
    authors_title = CaptionLabel(f'{tr('authors')}:')
    layout.addWidget(authors_title)
    layout_authors = QHBoxLayout()
    layout_authors.setContentsMargins(0, 0, 0, 0)
    btn_author1 = HyperlinkButton("https://github.com/admJvsc", "admJvsc")
    btn_author2 = HyperlinkButton("https://github.com/Kacperocik", "Kacperocik")
    btn_author3 = HyperlinkButton("https://github.com/4PZ", "4PZ")
    layout_authors.addWidget(btn_author1)
    layout_authors.addWidget(btn_author2)
    layout_authors.addWidget(btn_author3)
    layout_authors.addStretch(1)
    layout.addLayout(layout_authors)
    layout.addSpacing(10)
    layout.addStretch(1)

    return widget


def create_main_window():
    """Initializes and returns the main MSFluentWindow"""
    if os.name == 'nt':
        myappid = 'frog_package'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    window = MSFluentWindow()
    window.resize(950, 750)
    window.setWindowTitle(tr('app_title'))
    window.setWindowIcon(QIcon(gl.ICON_FILE))

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

if __name__ == "__main__":
    run_application()