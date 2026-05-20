import pandas as pd

import product_module
import utils

def update_customer(customer_id: str):
    customer_frame: pd.DataFrame = utils.customer_frame()

    row_mask: pd.Series = customer_frame["ID"].astype(str) == customer_id.strip()

    if not row_mask.any():
        return

    customer_frame.loc[row_mask, "UPDATED"] = utils.today()
    utils.save_customer_frame(customer_frame)

def get_all_customers() -> list[tuple]:
    customer_frame: pd.DataFrame = utils.customer_frame()
    address_frame: pd.DataFrame = utils.address_frame()

    merged_frame: pd.DataFrame = customer_frame.merge(address_frame, on="ID", how="left").fillna("")

    records: list[tuple] = []

    for _, row in merged_frame.iterrows():
        records.append((
            str(row["ID"]).strip(),
            str(row["NAME"]).strip(),
            str(row["E-MAIL"]).strip(),
            str(row["PHONE"]).strip(),
            str(row["STREET"]).strip(),
            str(row["CITY"]).strip(),
            str(row["COUNTRY"]).strip(),
        ))

    return records

def register_customer_in_db(name: str, email: str, phone: str, street: str, city: str, country: str) -> str:
    customer_frame: pd.DataFrame = utils.customer_frame()
    address_frame: pd.DataFrame = utils.address_frame()

    customer_id: str = utils.next_customer_id(customer_frame)

    today: str = utils.today()

    customer_row: dict[str, str] = {
        "ID": customer_id,
        "NAME": name.strip(),
        "E-MAIL": email.strip(),
        "PHONE": phone.strip(),
        "CREATED": today,
        "UPDATED": today,
    }

    address_row: dict[str, str] = {
        "ID": customer_id,
        "STREET": street.strip(),
        "CITY": city.strip(),
        "COUNTRY": country.strip(),
    }

    customer_frame = pd.concat([customer_frame, pd.DataFrame([customer_row])], ignore_index=True)
    address_frame = pd.concat([address_frame, pd.DataFrame([address_row])], ignore_index=True)

    utils.save_customer_frame(customer_frame)
    utils.save_address_frame(address_frame)

    return customer_id

def process_purchase_in_db(customer_id: str, product_name: str, quantity: int) -> int:
    customer_frame: pd.DataFrame = utils.customer_frame()
    normalized_customer_id: str = customer_id.strip()

    if not utils.has_customer(customer_frame, normalized_customer_id):
        return 1

    purchase_status: int = product_module.purchase_product(product_name, quantity)

    if purchase_status != 0:
        return purchase_status

    update_customer(normalized_customer_id)
    return 0

def remove_customer_from_db(customer_id: str):
    customer_frame: pd.DataFrame = utils.customer_frame()
    address_frame: pd.DataFrame = utils.address_frame()

    normalized_id = customer_id.strip()

    customer_mask = customer_frame["ID"].astype(str) != normalized_id
    customer_frame = customer_frame[customer_mask]

    address_mask = address_frame["ID"].astype(str) != normalized_id
    address_frame = address_frame[address_mask]

    utils.save_customer_frame(customer_frame)
    utils.save_address_frame(address_frame)