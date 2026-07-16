"""Clean raw product data."""

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
