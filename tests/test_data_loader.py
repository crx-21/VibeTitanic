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


def test_int_columns_are_integer() -> None:
    df = load_train(TRAIN_PATH)
    for col in INT_COLUMNS:
        # Use the dtype-family check rather than an exact string compare, so
        # this stays correct whether the loader returns nullable ``Int64`` or
        # the plain numpy ``int64`` (both are valid integer dtypes).
        assert pd.api.types.is_integer_dtype(df[col].dtype), (
            f"Expected {col} to be an integer dtype, got {df[col].dtype}"
        )


def test_int_columns_are_nullable_int64() -> None:
    """Lock in the ``Int64`` (nullable) choice over plain ``int64``.

    The whole point of the data-loader fix was to use pandas' nullable
    ``Int64`` so we don't silently lose any future missing values. A
    regression to plain ``int64`` would re-introduce the silent NaN→0 bug
    that motivated the change in the first place.
    """
    df = load_train(TRAIN_PATH)
    for col in INT_COLUMNS:
        assert df[col].dtype == pd.Int64Dtype(), (
            f"Expected {col} to be nullable Int64 (pd.Int64Dtype), "
            f"got {df[col].dtype}"
        )


def test_survived_column_is_nullable_int64() -> None:
    """``Survived`` must also be nullable ``Int64`` for the same reason."""
    df = load_train(TRAIN_PATH)
    assert df["Survived"].dtype == pd.Int64Dtype(), (
        f"Expected Survived to be nullable Int64 (pd.Int64Dtype), "
        f"got {df['Survived'].dtype}"
    )


def test_survived_non_binary_raises() -> None:
    """A non-0/1 value in ``Survived`` must raise ``ValueError`` (regression
    guard for the validation in ``_coerce_dtypes``).
    """
    import tempfile

    csv_text = (
        "PassengerId,Survived,Pclass,Name,Sex,Age,SibSp,Parch,Ticket,Fare,"
        "Cabin,Embarked\n"
        "1,2,3,T,1,22.0,1,0,A,7.25,,S\n"
        "2,0,3,T,2,38.0,1,0,B,71.2833,,C\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        f.write(csv_text)
        path = f.name
    try:
        with pytest.raises(ValueError, match="unexpected values"):
            load_train(path)
    finally:
        Path(path).unlink()


def test_int_columns_preserve_na() -> None:
    """A missing value in an ``INT_COLUMNS`` cell must be preserved as ``<NA>``
    in the loaded ``Int64`` column (this is the whole reason the loader uses
    nullable ``Int64`` instead of plain ``int64``).
    """
    import tempfile

    csv_text = (
        "PassengerId,Survived,Pclass,Name,Sex,Age,SibSp,Parch,Ticket,Fare,"
        "Cabin,Embarked\n"
        "1,1,,T,1,22.0,1,0,A,7.25,,S\n"  # Pclass empty
        "2,0,3,T,2,38.0,,0,B,71.2833,,C\n"  # SibSp empty
    )
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        f.write(csv_text)
        path = f.name
    try:
        df = load_train(path)
        assert df["Pclass"].isna().iloc[0], "Pclass NA was not preserved"
        assert df["SibSp"].isna().iloc[1], "SibSp NA was not preserved"
    finally:
        Path(path).unlink()


def test_survived_preserves_na() -> None:
    """A missing ``Survived`` value must load as ``<NA>`` rather than raising
    or silently coercing to a wrong value.
    """
    import tempfile

    csv_text = (
        "PassengerId,Survived,Pclass,Name,Sex,Age,SibSp,Parch,Ticket,Fare,"
        "Cabin,Embarked\n"
        "1,,3,T,1,22.0,1,0,A,7.25,,S\n"
        "2,0,3,T,2,38.0,1,0,B,71.2833,,C\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        f.write(csv_text)
        path = f.name
    try:
        df = load_train(path)
        assert df["Survived"].isna().iloc[0], "Survived NA was not preserved"
        assert df["Survived"].iloc[1] == 0
    finally:
        Path(path).unlink()


def test_load_train_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_train(path="csvs/does_not_exist.csv")


def test_load_test_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_test(path="csvs/does_not_exist.csv")