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
# We pin the category set explicitly so train and test always share the same
# CategoricalDtype, even if one split happens to miss a rare value (e.g. an
# Embarked='Q' row only in test). Without this, ``astype("category")`` infers
# the categories per-call, and train/test end up with different dtype objects
# — which then breaks anything categorical-aware downstream (one-hot encoding,
# target encoding, XGBoost with enable_categorical=True, etc.).
CATEGORICAL_COLUMNS = ("Sex", "Embarked")
#: Canonical category order for each categorical column. Stable across calls
#: so that ``pd.api.types.is_categorical(df["Sex"])`` and equality checks
#: between train and test hold. ``Embarked`` lists the three known ports; the
#: missing-value handling is done in ``_coerce_dtypes`` via ``categories=...``.
CATEGORICAL_DTYPES: dict[str, pd.CategoricalDtype] = {
    "Sex": pd.CategoricalDtype(categories=["female", "male"], ordered=False),
    "Embarked": pd.CategoricalDtype(categories=["C", "Q", "S"], ordered=False),
}

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
        # disaster for a classification model. Drop NA before sorting because
        # ``sorted`` on an ``Int64`` Series containing ``<NA>`` raises
        # ``TypeError: boolean value of NA is ambiguous``.
        unique = sorted(out["Survived"].dropna().unique().tolist())
        if unique not in ([0], [1], [0, 1]):
            raise ValueError(
                f"Train CSV 'Survived' column has unexpected values: {unique}. "
                "Expected only 0 and 1."
            )

    for col in CATEGORICAL_COLUMNS:
        if col in out.columns:
            # Pin the dtype to the canonical categories (see CATEGORICAL_DTYPES)
            # rather than ``astype("category")``, which would infer categories
            # from whatever rows appear in this particular DataFrame and could
            # produce a different dtype on train vs test.
            out[col] = out[col].astype(CATEGORICAL_DTYPES[col])

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
    "CATEGORICAL_DTYPES",
    "INT_COLUMNS",
    "load_train",
    "load_test",
]