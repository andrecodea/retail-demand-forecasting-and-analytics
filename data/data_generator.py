"""Synthetic dataset generator for the project.

This module creates an extended supermarket sales CSV based on the
original small sample (`data/supermarket_sales.csv`). It uses
weighted sampling and simple rules to produce plausible transaction
rows and writes the result to `data/supermarket_sales_extended.csv`.
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import logging
import sys

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_data(target_rows: int = 6641) -> None:
    """Generate a synthetic supermarket sales dataset and save to CSV.

    The function reads the base CSV (`data/supermarket_sales.csv`) to
    obtain category values and samples new rows according to configured
    weights and ranges. The output file is written to
    `data/supermarket_sales_extended.csv`.

    Parameters
    - target_rows (int): number of rows to generate (default: 6641).

    Returns
    - None: side effect is writing the CSV file to disk.
    """

    # Load base CSV and extract category values
    try:
        df = pd.read_csv("data/supermarket_sales.csv", sep=';', decimal=',')
        cities = df["City"].unique()
        customer_type = df["Customer type"].unique()
        gender = df["Gender"].unique()
        payment = df['Payment'].unique()
    except Exception as e:
        logger.error(f"Error reading CSV base: {e}")
        sys.exit()

    # Branch, payment and product weights
    branch_weights = {"Mandalay": 30, "Naypyitaw": 15, "Yangon": 55}
    payment_method_weights = {"Ewallet": 40, "Credit card": 45, "Cash": 15}
    product_weights = {
        "Food and beverages": 60,
        "Health and beauty": 10,
        "Sports and travel": 5,
        "Home and lifestyle": 10,
        "Electronic accessories": 5,
        "Fashion accessories": 10,
    }

    # Price ranges per product category
    price_ranges = {
        "Food and beverages": (1, 190),
        "Health and beauty": (7, 290),
        "Sports and travel": (20, 370),
        "Home and lifestyle": (5, 500),
        "Electronic accessories": (30, 1290),
        "Fashion accessories": (17, 330),
    }

    # Prepare weighted lists
    products_list = list(product_weights.keys())
    products_weights_list = list(product_weights.values())
    branches_list = list(branch_weights.keys())
    branches_weights_list = list(branch_weights.values())
    payment_method_list = list(payment_method_weights.keys())
    payment_method_weights_list = list(payment_method_weights.values())

    weighted_products_list = random.choices(products_list, weights=products_weights_list, k=target_rows)
    weighted_payment_methods_list = random.choices(payment_method_list, weights=payment_method_weights_list, k=target_rows)
    weighted_branches_list = random.choices(branches_list, weights=branches_weights_list, k=target_rows)

    # Start date for generated transactions
    start_date = datetime.strptime("01/01/2026", "%d/%m/%Y")

    new_data = []
    logger.info(f"Generating dataset with {target_rows} rows.")

    # Generate rows
    try:
        for i in range(target_rows):
            days = random.randint(0, 364)
            duration = timedelta(days=days)

            current_product = weighted_products_list[i]
            current_payment_method = weighted_payment_methods_list[i]
            current_branch = weighted_branches_list[i]

            min_price, max_price = price_ranges[current_product]

            quantity_growth = int(days / 600) * 1
            quantity = random.randint(1, 10) + quantity_growth

            price_inflation = int(days / 365) * 5
            price = random.randint(min_price, max_price) + price_inflation

            total = (price * quantity) * 1.05
            gross_margin_percentage = 0.0479
            gross_income = total * gross_margin_percentage

            actual_date = start_date + duration

            row = {
                'Invoice ID': f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(100,999)}",
                'Date': actual_date,
                'City': current_branch,
                'Gender': random.choice(gender),
                'Customer type': random.choice(customer_type),
                'Product line': current_product,
                'Payment': current_payment_method,
                'Unit price': round(price, 2),
                'Quantity': quantity,
                'Total': round(total, 2),
                'Gross margin percentage': gross_margin_percentage,
                'Gross income': round(gross_income, 2),
                'Rating': round(random.uniform(1, 10), 1),
            }

            new_data.append(row)
    except Exception as e:
        logger.error(f"Error while generating DataFrame rows: {e}")
        sys.exit()

    # Write output CSV
    file_path = "data/supermarket_sales_extended.csv"
    df_final = pd.DataFrame(new_data)
    df_final.to_csv(file_path, index=False, sep=';', decimal=',')

    logger.info(f"DataFrame with {target_rows} rows generated with success at the path: '{file_path}'.")


if __name__ == "__main__":
    generate_data()
