"""Clean  raw sales data."""

import logging
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "sales_data.csv"
PREPARED_FILE = PROJECT_ROOT / "data" / "prepared" / "sales_data_prepared.csv"
LOG_FILE = PROJECT_ROOT / "logs" / "prepare_sales_data.log"

PREPARED_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filemode="w",
)

logger = logging.getLogger(__name__)


def prepare_sales() -> None:
    """Load, clean, validate, and save sales data."""
    df = pd.read_csv(RAW_FILE)
    raw_count = len(df)

    logger.info("Loaded %s raw sales records.", raw_count)

    # Remove exact duplicates and duplicate transaction IDs.
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=["TransactionID"], keep="first")

    # Convert columns to their correct data types.
    df["SaleDate"] = pd.to_datetime(df["SaleDate"], errors="coerce")
    df["SaleAmount"] = pd.to_numeric(df["SaleAmount"], errors="coerce")
    df["CampaignID"] = pd.to_numeric(df["CampaignID"], errors="coerce")

    # Treat a missing campaign as no campaign.
    df["CampaignID"] = df["CampaignID"].fillna(0).astype(int)

    # Remove records missing required information.
    required_columns = [
        "TransactionID",
        "SaleDate",
        "CustomerID",
        "ProductID",
        "StoreID",
        "SaleAmount",
    ]
    df = df.dropna(subset=required_columns)

    # Remove zero or negative sales amounts.
    df = df[df["SaleAmount"] > 0]

    # Remove extreme SaleAmount outliers using the IQR method.
    q1 = df["SaleAmount"].quantile(0.25)
    q3 = df["SaleAmount"].quantile(0.75)
    iqr = q3 - q1
    lower_limit = max(0, q1 - 1.5 * iqr)
    upper_limit = q3 + 1.5 * iqr

    df = df[(df["SaleAmount"] >= lower_limit) & (df["SaleAmount"] <= upper_limit)]

    # Restore the standard YYYY-MM-DD date format.
    df["SaleDate"] = df["SaleDate"].dt.strftime("%Y-%m-%d")

    # Keep the expected columns in the expected order.
    df = df[
        [
            "TransactionID",
            "SaleDate",
            "CustomerID",
            "ProductID",
            "StoreID",
            "CampaignID",
            "SaleAmount",
        ]
    ]

    df.to_csv(PREPARED_FILE, index=False)

    logger.info("Saved %s prepared sales records.", len(df))
    logger.info("Removed %s sales records.", raw_count - len(df))

    print(f"Sales: {raw_count} raw -> {len(df)} prepared")


if __name__ == "__main__":
    prepare_sales()
