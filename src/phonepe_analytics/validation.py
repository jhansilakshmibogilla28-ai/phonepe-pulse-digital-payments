import pandas as pd


REQUIRED_TRANSACTION_COLUMNS = {
    "year",
    "quarter",
    "period",
    "category",
    "transaction_count",
    "transaction_amount",
}


def validate_transactions(df: pd.DataFrame) -> None:
    """Validate the aggregated transaction table."""
    if df.empty:
        raise ValueError("Transaction dataset is empty.")

    missing = REQUIRED_TRANSACTION_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required transaction columns: {sorted(missing)}"
        )

    if df["transaction_count"].isna().any():
        raise ValueError("transaction_count contains missing values.")

    if df["transaction_amount"].isna().any():
        raise ValueError("transaction_amount contains missing values.")

    if (df["transaction_count"] < 0).any():
        raise ValueError("transaction_count contains negative values.")

    if (df["transaction_amount"] < 0).any():
        raise ValueError("transaction_amount contains negative values.")

    if not df["quarter"].between(1, 4).all():
        raise ValueError("quarter must be between 1 and 4.")


def validate_output_files(paths: dict) -> None:
    """Confirm expected pipeline outputs were created."""
    missing = [name for name, path in paths.items() if not path.exists()]

    if missing:
        raise FileNotFoundError(
            f"Missing pipeline outputs: {', '.join(missing)}"
        )
