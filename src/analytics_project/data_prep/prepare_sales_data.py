"""Clean Raw Sales Data

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

from dataclasses import dataclass, field
import logging
from pathlib import Path

import pandas as pd


@dataclass
class SalesConfig:
    project_root: Path = None
    required_columns: list[str] = field(
        default_factory=lambda: [
            "TransactionID",
            "SaleDate",
            "CustomerID",
            "ProductID",
            "StoreID",
            "SaleAmount",
        ]
    )
    outlier_multiplier: float = 1.5
    default_campaign_id: int = 0

    def __post_init__(self):
        if self.project_root is None:
            self.project_root = Path(__file__).resolve().parents[3]

    @property
    def raw_file(self) -> Path:
        return self.project_root / "data" / "raw" / "sales_data.csv"

    @property
    def prepared_file(self) -> Path:
        return self.project_root / "data" / "prepared" / "sales_data_prepared.csv"

    @property
    def log_file(self) -> Path:
        return self.project_root / "logs" / "prepare_sales_data.log"

    @property
    def output_columns(self) -> list[str]:
        return [
            "TransactionID",
            "SaleDate",
            "CustomerID",
            "ProductID",
            "StoreID",
            "CampaignID",
            "SaleAmount",
        ]


class SalesDataPreparer:
    def __init__(self, config: SalesConfig = None):
        self.config = config or SalesConfig()
        self._setup_directories()
        self._setup_logging()
        self.logger = logging.getLogger(__name__)

    def _setup_directories(self) -> None:
        self.config.prepared_file.parent.mkdir(parents=True, exist_ok=True)
        self.config.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self) -> None:
        logging.basicConfig(
            filename=self.config.log_file,
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            filemode="w",
        )

    def prepare(self) -> None:
        """Load, clean, validate, and save sales data."""
        df = pd.read_csv(self.config.raw_file)
        raw_count = len(df)
        self.logger.info("Loaded %s raw sales records.", raw_count)

        df = self._remove_duplicates(df)
        df = self._convert_data_types(df)
        df = self._handle_missing_campaign(df)
        df = self._remove_invalid_records(df)
        df = self._remove_outliers(df)
        df = self._format_dates(df)
        df = self._select_columns(df)

        df.to_csv(self.config.prepared_file, index=False)

        self.logger.info("Saved %s prepared sales records.", len(df))
        self.logger.info("Removed %s sales records.", raw_count - len(df))
        print(f"Sales: {raw_count} raw -> {len(df)} prepared")

    @staticmethod
    def _remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        df = df.drop_duplicates()
        return df.drop_duplicates(subset=["TransactionID"], keep="first")

    @staticmethod
    def _convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
        df["SaleDate"] = pd.to_datetime(df["SaleDate"], errors="coerce")
        df["SaleAmount"] = pd.to_numeric(df["SaleAmount"], errors="coerce")
        df["CampaignID"] = pd.to_numeric(df["CampaignID"], errors="coerce")
        return df

    def _handle_missing_campaign(self, df: pd.DataFrame) -> pd.DataFrame:
        df["CampaignID"] = (
            df["CampaignID"].fillna(self.config.default_campaign_id).astype(int)
        )
        return df

    def _remove_invalid_records(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(subset=self.config.required_columns)
        return df[df["SaleAmount"] > 0]

    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        q1 = df["SaleAmount"].quantile(0.25)
        q3 = df["SaleAmount"].quantile(0.75)
        iqr = q3 - q1
        lower_limit = max(0, q1 - self.config.outlier_multiplier * iqr)
        upper_limit = q3 + self.config.outlier_multiplier * iqr
        return df[(df["SaleAmount"] >= lower_limit) & (df["SaleAmount"] <= upper_limit)]

    @staticmethod
    def _format_dates(df: pd.DataFrame) -> pd.DataFrame:
        df["SaleDate"] = df["SaleDate"].dt.strftime("%Y-%m-%d")
        return df

    def _select_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self.config.output_columns]


if __name__ == "__main__":
    config = SalesConfig()
    preparer = SalesDataPreparer(config)
    preparer.prepare()
