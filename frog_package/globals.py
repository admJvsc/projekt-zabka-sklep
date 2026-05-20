import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'DATABASE')

PROD_FILE = os.path.join(DB_DIR, 'products.xlsx')
CUST_FILE = os.path.join(DB_DIR, 'customer.csv')
ADDR_FILE = os.path.join(DB_DIR, 'address.csv')
SETT_FILE = os.path.join(DB_DIR, 'settings.csv')
LANG_FILE = os.path.join(DB_DIR, 'translations.csv')
LOGO_FILE = os.path.join(DB_DIR, 'logo.svg')
ICON_FILE = os.path.join(DB_DIR, 'icon.png')