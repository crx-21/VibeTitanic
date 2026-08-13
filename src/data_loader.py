"""Data loading utilities for the Titanic dataset.

Two thin wrappers around ``pandas.read_csv`` that give us:

* A stable, explicit schema (consistent dtypes across calls).
* Clear error messages when the file is missing or the columns are wrong.
* A single place to change if the CSV layout ever changes.

The module exposes two public functions:

* :func:`load_train` — returns the labeled training set (891 rows).
* :func:`load_test`  — returns the unlabeled test set (418 rows).

Both functions validate that the input CSV exists and contains the columns
we expect. They do *not* impute missing values, encode categoricals, or do
any feature engineering — those concerns live in ``src.features``.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# Columns every Titanic CSV is expected to carry. ``Survived`` is train-only.
EXPECTED_COMMON_COLUMNS = (
    "PassengerId",
    "Pclass",
    "Name",
    "Sex",
    "Age",
    "SibSp",
    "Parch",
    "Ticket",
    "Fare",
    "Cabin",
    "Embarked",
)
EXPECTED_TRAIN_EXTRA = ("Survived",)
EXPECTED_TEST_EXTRA: tuple[str, ...] = ()

# Columns we want as pandas Categorical (low cardinality, repeated strings).
CATEGORICAL_COLUMNS = ("Sex", "Embarked")

# Columns that must be integer-typed for downstream code.
INT_COLUMNS = ("PassengerId", "Pclass", "SibSp", "Parch")


def _validate_columns(df: pd.DataFrame, expected: tuple[str, ...], *, label: str) -> None:
    """Raise ``ValueError`` if ``df`` is missing any of ``expected`` columns."""
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(
            f"{label} CSV is missing required columns: {missing}. "
            f"Got columns: {list(df.columns)}"
        )


def _coerce_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``df`` with stable, explicit dtypes."""
    out = df.copy()

    for col in INT_COLUMNS:
        if col in out.columns:
            # ``Int64`` (capital I) is nullable; ``int64`` is not. Use Int64 so
            # we don't silently lose any future missing values.
            out[col] = pd.array(out[col], dtype="Int64")

    if "Survived" in out.columns:
        out["Survived"] = pd.array(out["Survived"], dtype="Int64")
        # Sanity-check the target is binary. Silent 0/2 values would be a
        # disaster for a classification model.
        unique = sorted(out["Survived"].unique().tolist())
        if unique not in ([0], [1], [0, 1]):
            raise ValueError(
                f"Train CSV 'Survived' column has unexpected values: {unique}. "
                "Expected only 0 and 1."
            )

    for col in CATEGORICAL_COLUMNS:
        if col in out.columns:
            out[col] = out[col].astype("category")

    return out


def _resolve_path(path: str | Path) -> Path:
    """Resolve a path to an absolute ``Path`` and verify the file exists."""
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(
            f"Titanic CSV not found at: {p}\n"
            "Tip: drop the Kaggle train.csv / test.csv into the csvs/ folder."
        )
    return p


def load_train(path: str | Path = "csvs/train.csv") -> pd.DataFrame:
    """Load ``csvs/train.csv`` and return a DataFrame with stable dtypes.

    Parameters
    ----------
    path:
        Filesystem path to the training CSV. Defaults to ``csvs/train.csv``,
        which is where the Kaggle file is expected to live.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If required columns (including ``Survived``) are missing, or if the
        ``Survived`` column contains values other than 0 and 1.
    """
    resolved = _resolve_path(path)
    df = pd.read_csv(resolved)
    _validate_columns(
        df, EXPECTED_COMMON_COLUMNS + EXPECTED_TRAIN_EXTRA, label="Train"
    )
    return _coerce_dtypes(df)


def load_test(path: str | Path = "csvs/test.csv") -> pd.DataFrame:
    """Load ``csvs/test.csv`` and return a DataFrame with stable dtypes.

    The test set intentionally has no ``Survived`` column — the whole point
    is that we predict it. This function only checks for the *common*
    columns and does not require ``Survived``.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the common required columns are missing.
    """
    resolved = _resolve_path(path)
    df = pd.read_csv(resolved)
    _validate_columns(
        df, EXPECTED_COMMON_COLUMNS + EXPECTED_TEST_EXTRA, label="Test"
    )
    return _coerce_dtypes(df)


__all__ = [
    "EXPECTED_COMMON_COLUMNS",
    "EXPECTED_TRAIN_EXTRA",
    "CATEGORICAL_COLUMNS",
    "INT_COLUMNS",
    "load_train",
    "load_test",
]