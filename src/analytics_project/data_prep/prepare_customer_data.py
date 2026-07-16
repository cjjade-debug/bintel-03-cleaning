"""Clean Raw Customers Data

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
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "customers_data.csv"
PREPARED_FILE = PROJECT_ROOT / "data" / "prepared" / "customers_data_prepared.csv"
LOG_FILE = PROJECT_ROOT / "logs" / "prepare_customers_data.log"

PREPARED_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filemode="w",
)

logger = logging.getLogger(__name__)


def prepare_customers() -> None:
    """Load, clean, validate, and save customer data."""
    df = pd.read_csv(RAW_FILE)
    raw_count = len(df)

    logger.info("Loaded %s raw customer records.", raw_count)

    # Remove exact duplicate rows.
    df = df.drop_duplicates()

    # Remove duplicate customer IDs, keeping the first record.
    df = df.drop_duplicates(subset=["CustomerID"], keep="first")

    # Clean text fields.
    df["Name"] = df["Name"].astype(str).str.strip().str.title()
    df["Region"] = (
        df["Region"]
        .astype(str)
        .str.strip()
        .str.replace("-", " ", regex=False)
        .str.title()
    )

    # Convert the date and remove invalid dates.
    df["JoinDate"] = pd.to_datetime(df["JoinDate"], errors="coerce")
    df = df.dropna(subset=["CustomerID", "Name", "Region", "JoinDate"])

    # Restore the standard YYYY-MM-DD date format.
    df["JoinDate"] = df["JoinDate"].dt.strftime("%Y-%m-%d")

    # Keep the expected columns in the expected order.
    df = df[["CustomerID", "Name", "Region", "JoinDate"]]

    df.to_csv(PREPARED_FILE, index=False)

    logger.info("Saved %s prepared customer records.", len(df))
    logger.info("Removed %s customer records.", raw_count - len(df))

    print(f"Customers: {raw_count} raw -> {len(df)} prepared")


if __name__ == "__main__":
    prepare_customers()
