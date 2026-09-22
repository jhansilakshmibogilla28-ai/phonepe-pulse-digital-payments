import pandas as pd
import pytest

from src.phonepe_analytics.validation import (
    validate_output_files,
    validate_transactions,
)


def test_validate_transactions_pass():
    df = pd.DataFrame(
        {
            "year": [2026],
            "quarter": [2],
            "period": ["Q2 2026"],
            "category": ["P2P"],
            "transaction_count": [100],
            "transaction_amount": [1000],
        }
    )

    validate_transactions(df)


def test_validate_transactions_empty():
    df = pd.DataFrame()

    with pytest.raises(ValueError, match="Transaction dataset is empty"):
        validate_transactions(df)


def test_validate_transactions_missing_columns():
    df = pd.DataFrame(
        {
            "year": [2026],
            "quarter": [2],
        }
    )

    with pytest.raises(ValueError, match="Missing required transaction columns"):
        validate_transactions(df)


def test_validate_transactions_negative_values():
    df = pd.DataFrame(
        {
            "year": [2026],
            "quarter": [2],
            "period": ["Q2 2026"],
            "category": ["P2P"],
            "transaction_count": [-100],
            "transaction_amount": [1000],
        }
    )

    with pytest.raises(
        ValueError,
        match="transaction_count contains negative",
    ):
        validate_transactions(df)


def test_validate_transactions_invalid_quarter():
    df = pd.DataFrame(
        {
            "year": [2026],
            "quarter": [5],
            "period": ["Q5 2026"],
            "category": ["P2P"],
            "transaction_count": [100],
            "transaction_amount": [1000],
        }
    )

    with pytest.raises(
        ValueError,
        match="quarter must be between 1 and 4",
    ):
        validate_transactions(df)
