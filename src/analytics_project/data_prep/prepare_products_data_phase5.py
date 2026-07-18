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
- Convert data types (e.g., text to numeric, text to datetime)."""

from dataclasses import dataclass
import logging
from pathlib import Path

import pandas as pd


@dataclass
class OutlierConfig:
    lower_multiplier: float = 1.5
    upper_multiplier: float = 1.5


class ProductDataPreparer:
    def __init__(self, project_root: Path = None, outlier_config: OutlierConfig = None):
        self.project_root = project_root or Path(__file__).resolve().parents[3]
        self.raw_file = self.project_root / "data" / "raw" / "products_data.csv"
        self.prepared_file = (
            self.project_root / "data" / "prepared" / "products_data_prepared.csv"
        )
        self.log_file = self.project_root / "logs" / "prepare_products_data.log"
        self.outlier_config = outlier_config or OutlierConfig()

        self._setup_directories()
        self._setup_logging()
        self.logger = logging.getLogger(__name__)

    def _setup_directories(self) -> None:
        self.prepared_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self) -> None:
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            filemode="w",
        )

    def prepare(self) -> None:
        """Load, clean, validate, and save product data."""
        df = pd.read_csv(self.raw_file)
        raw_count = len(df)
        self.logger.info("Loaded %s raw product records.", raw_count)

        df = self._remove_duplicates(df)
        df = self._clean_text_fields(df)
        df = self._convert_prices(df)
        df = self._process_stock_quantity(df)
        df = self._remove_invalid_records(df)
        df = self._remove_outliers(df)
        df = self._compute_stock_status(df)
        df = self._select_columns(df)

        df.to_csv(self.prepared_file, index=False)

        self.logger.info("Saved %s prepared product records.", len(df))
        self.logger.info("Removed %s product records.", raw_count - len(df))
        print(f"Products: {raw_count} raw -> {len(df)} prepared")

    @staticmethod
    def _remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        df = df.drop_duplicates()
        df = df.drop_duplicates(subset=["ProductID"], keep="first")
        return df

    @staticmethod
    def _clean_text_fields(df: pd.DataFrame) -> pd.DataFrame:
        df["ProductName"] = df["ProductName"].astype(str).str.strip()
        df["Category"] = df["Category"].astype(str).str.strip().str.title()
        return df

    @staticmethod
    def _convert_prices(df: pd.DataFrame) -> pd.DataFrame:
        df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
        return df

    @staticmethod
    def _process_stock_quantity(df: pd.DataFrame) -> pd.DataFrame:
        """Convert StockQuantity to numeric, handling missing values."""
        if "StockQuantity" in df.columns:
            df["StockQuantity"] = pd.to_numeric(df["StockQuantity"], errors="coerce")
        else:
            df["StockQuantity"] = 0
        return df

    @staticmethod
    def _remove_invalid_records(df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(subset=["ProductID", "ProductName", "Category", "UnitPrice"])
        df = df[df["UnitPrice"] > 0]
        return df

    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        q1 = df["UnitPrice"].quantile(0.25)
        q3 = df["UnitPrice"].quantile(0.75)
        iqr = q3 - q1
        lower_limit = q1 - self.outlier_config.lower_multiplier * iqr
        upper_limit = q3 + self.outlier_config.upper_multiplier * iqr

        return df[(df["UnitPrice"] >= lower_limit) & (df["UnitPrice"] <= upper_limit)]

    @staticmethod
    def _compute_stock_status(df: pd.DataFrame) -> pd.DataFrame:
        """Compute StockStatus based on StockQuantity."""

        def determine_status(qty):
            if pd.isna(qty):
                return "Unknown"
            elif qty == 0:
                return "Out of Stock"
            elif qty < 10:
                return "Low Stock"
            elif qty < 50:
                return "In Stock"
            else:
                return "Well Stocked"

        df["StockStatus"] = df["StockQuantity"].apply(determine_status)
        return df

    @staticmethod
    def _select_columns(df: pd.DataFrame) -> pd.DataFrame:
        return df[
            [
                "ProductID",
                "ProductName",
                "Category",
                "UnitPrice",
                "StockQuantity",
                "StockStatus",
            ]
        ]


if __name__ == "__main__":
    preparer = ProductDataPreparer()
    preparer.prepare()
