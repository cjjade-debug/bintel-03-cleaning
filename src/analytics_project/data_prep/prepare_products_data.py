"""Clean Raw Products Data

An example of cleaning and preparing raw smart sales data.
Cleaning and preparation is a critical step in any BI workflow.
It is different for every project and every dataset.

This example is designed to be copied and modified.
On new datasets, you will need to change the cleaning and preparation logic.
This example is only an illustration.

Cleaning can be 80-90% of the work in a BI project.
It is often the most time-consuming step and
to do it well requires domain knowledge, attention to detail,
tenacity, and resourcefulness.

It is often the most important step because
if the data is not clean, the analysis will be wrong and
the business decisions will be wrong.

Common cleaning and preparation tasks include:
- Remove duplicate rows.
- Remove rows with missing or invalid values.
- Normalize inconsistent values (e.g., "East", "east", " EAST ").
- Convert data types (e.g., text to numeric, text to datetime).

Author: Cassie J. McCoin
Date: 2026-07
"""

import logging
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "products_data.csv"
PREPARED_FILE = PROJECT_ROOT / "data" / "prepared" / "products_data_prepared.csv"
LOG_FILE = PROJECT_ROOT / "logs" / "prepare_products_data.log"

PREPARED_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filemode="w",
)

logger = logging.getLogger(__name__)


def prepare_products() -> None:
    """Load, clean, validate, and save product data."""
    df = pd.read_csv(RAW_FILE)
    raw_count = len(df)

    logger.info("Loaded %s raw product records.", raw_count)

    # Remove exact duplicate rows and duplicate product IDs.
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=["ProductID"], keep="first")

    # Clean text fields.
    df["ProductName"] = df["ProductName"].astype(str).str.strip()
    df["Category"] = df["Category"].astype(str).str.strip().str.title()

    # Convert price values to numbers.
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")

    # Remove missing values and impossible prices.
    df = df.dropna(subset=["ProductID", "ProductName", "Category", "UnitPrice"])
    df = df[df["UnitPrice"] > 0]

    # Remove extreme UnitPrice outliers using the IQR method.
    q1 = df["UnitPrice"].quantile(0.25)
    q3 = df["UnitPrice"].quantile(0.75)
    iqr = q3 - q1
    lower_limit = q1 - 1.5 * iqr
    upper_limit = q3 + 1.5 * iqr

    df = df[(df["UnitPrice"] >= lower_limit) & (df["UnitPrice"] <= upper_limit)]

    # Keep the expected columns in the expected order.
    df = df[["ProductID", "ProductName", "Category", "UnitPrice"]]

    df.to_csv(PREPARED_FILE, index=False)

    logger.info("Saved %s prepared product records.", len(df))
    logger.info("Removed %s product records.", raw_count - len(df))

    print(f"Products: {raw_count} raw -> {len(df)} prepared")


if __name__ == "__main__":
    prepare_products()
