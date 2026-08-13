"""Tests for ``src.data_loader``.

These tests assume the Kaggle CSVs are present at ``csvs/train.csv`` and
``csvs/test.csv``. If they're missing, the loader raises ``FileNotFoundError``
and these tests fail with a clear message rather than something cryptic.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import (
    CATEGORICAL_COLUMNS,
    EXPECTED_COMMON_COLUMNS,
    INT_COLUMNS,
    load_test,
    load_train,
)

TRAIN_PATH = Path("csvs/train.csv")
TEST_PATH = Path("csvs/test.csv")


def test_train_has_expected_shape_and_columns() -> None:
    df = load_train(TRAIN_PATH)
    # 891 rows is the canonical Kaggle Titanic training set size.
    assert df.shape[0] == 891, f"Expected 891 rows, got {df.shape[0]}"
    for col in EXPECTED_COMMON_COLUMNS + ("Survived",):
        assert col in df.columns, f"Train CSV missing column: {col}"


def test_test_has_expected_shape_and_columns() -> None:
    df = load_test(TEST_PATH)
    # 418 rows is the canonical Kaggle Titanic test set size.
    assert df.shape[0] == 418, f"Expected 418 rows, got {df.shape[0]}"
    for col in EXPECTED_COMMON_COLUMNS:
        assert col in df.columns, f"Test CSV missing column: {col}"
    # The test set is the unlabeled one — Survived must NOT be present.
    assert "Survived" not in df.columns, "Test CSV should not contain Survived"


def test_train_target_is_binary() -> None:
    df = load_train(TRAIN_PATH)
    assert set(df["Survived"].unique().tolist()).issubset({0, 1})


def test_categorical_columns_are_pandas_category() -> None:
    df = load_train(TRAIN_PATH)
    for col in CATEGORICAL_COLUMNS:
        # ``is_categorical_dtype`` is deprecated in pandas 2.x; use the
        # ``CategoricalDtype`` check instead.
        assert isinstance(df[col].dtype, pd.CategoricalDtype), (
            f"Expected {col} to be categorical, got {df[col].dtype}"
        )


def test_int_columns_are_int64() -> None:
    df = load_train(TRAIN_PATH)
    for col in INT_COLUMNS:
        assert df[col].dtype == "int64", (
            f"Expected {col} to be int64, got {df[col].dtype}"
        )


def test_load_train_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_train(path="csvs/does_not_exist.csv")


def test_load_test_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_test(path="csvs/does_not_exist.csv")