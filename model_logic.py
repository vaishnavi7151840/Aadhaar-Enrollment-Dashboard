import pandas as pd
import numpy as np

AGE_BUCKET_DEFAULTS = ["age_0_5", "age_5_17", "age_18_greater"]

def load_data(file_like_or_path):
    """Load Aadhaar dataset. Handles CSV and Excel (.xls/.xlsx).
    Note: some files are named .xls but contain CSV text.
    """
    try:
        return pd.read_csv(file_like_or_path)
    except Exception:
        return pd.read_excel(file_like_or_path)

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
        df = df.dropna(subset=["date"])
    return df

def get_age_cols(df: pd.DataFrame):
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    age_cols = [c for c in AGE_BUCKET_DEFAULTS if c in df.columns and c in numeric_cols]
    if age_cols:
        return age_cols
    # fallback: all numeric except pincode
    return [c for c in numeric_cols if c != "pincode"]

def add_total(df: pd.DataFrame, age_cols=None) -> pd.DataFrame:
    df = df.copy()
    if age_cols is None:
        age_cols = get_age_cols(df)
    if age_cols:
        df["total"] = df[age_cols].sum(axis=1)
    else:
        df["total"] = 0
    return df

def yearly_trend(df: pd.DataFrame, value_col: str = "total") -> pd.Series:
    if "date" not in df.columns:
        return pd.Series(dtype=float)
    tmp = df.copy()
    tmp["Year"] = tmp["date"].dt.year
    return tmp.groupby("Year")[value_col].sum().sort_index()


def monthly_age_trend(df: pd.DataFrame, age_cols=None) -> pd.DataFrame:
    """Return month-wise sums for each age bucket."""
    if "date" not in df.columns:
        return pd.DataFrame()
    tmp = df.copy()
    if age_cols is None:
        age_cols = get_age_cols(tmp)
    tmp["Month"] = tmp["date"].dt.to_period("M").astype(str)
    if not age_cols:
        return pd.DataFrame()
    return tmp.groupby("Month")[age_cols].sum().sort_index()


def top_districts_monthly_trend(df: pd.DataFrame, top_n: int = 5, base_col: str = "age_18_greater") -> pd.DataFrame:
    """Return month-wise trend for top N districts based on base_col sum."""
    if "date" not in df.columns or "district" not in df.columns:
        return pd.DataFrame()
    tmp = df.copy()
    tmp["Month"] = tmp["date"].dt.to_period("M").astype(str)
    if base_col not in tmp.columns:
        # fallback: use total if present
        base_col = "total" if "total" in tmp.columns else None
    if base_col is None:
        return pd.DataFrame()
    top = (
        tmp.groupby("district")[base_col]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .index
        .tolist()
    )
    t = tmp[tmp["district"].isin(top)].groupby(["Month", "district"])[base_col].sum().reset_index()
    pivot = t.pivot(index="Month", columns="district", values=base_col).fillna(0).sort_index()
    return pivot
