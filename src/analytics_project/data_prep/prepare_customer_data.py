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
- Convert data types (e.g., text to numeric, text to datetime)."""

import logging
from pathlib import Path

import pandas as pd


class CustomerDataPreparer:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).resolve().parents[3]
        self.raw_file = self.project_root / "data" / "raw" / "customers_data.csv"
        self.prepared_file = (
            self.project_root / "data" / "prepared" / "customers_data_prepared.csv"
        )
        self.log_file = self.project_root / "logs" / "prepare_customers_data.log"

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
        """Load, clean, validate, and save customer data."""
        df = pd.read_csv(self.raw_file)
        raw_count = len(df)
        self.logger.info("Loaded %s raw customer records.", raw_count)

        df = self._remove_duplicates(df)
        df = self._clean_text_fields(df)
        df = self._process_dates(df)
        df = self._select_columns(df)

        df.to_csv(self.prepared_file, index=False)

        self.logger.info("Saved %s prepared customer records.", len(df))
        self.logger.info("Removed %s customer records.", raw_count - len(df))
        print(f"Customers: {raw_count} raw -> {len(df)} prepared")

    @staticmethod
    def _remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        df = df.drop_duplicates()
        df = df.drop_duplicates(subset=["CustomerID"], keep="first")
        return df

    @staticmethod
    def _clean_text_fields(df: pd.DataFrame) -> pd.DataFrame:
        df["Name"] = df["Name"].astype(str).str.strip().str.title()
        df["Region"] = (
            df["Region"]
            .astype(str)
            .str.strip()
            .str.replace("-", " ", regex=False)
            .str.title()
        )
        return df

    @staticmethod
    def _process_dates(df: pd.DataFrame) -> pd.DataFrame:
        df["JoinDate"] = pd.to_datetime(df["JoinDate"], errors="coerce")
        df = df.dropna(subset=["CustomerID", "Name", "Region", "JoinDate"])
        df["JoinDate"] = df["JoinDate"].dt.strftime("%Y-%m-%d")
        return df

    @staticmethod
    def _select_columns(df: pd.DataFrame) -> pd.DataFrame:
        return df[["CustomerID", "Name", "Region", "JoinDate"]]


if __name__ == "__main__":
    preparer = CustomerDataPreparer()
    preparer.prepare()
