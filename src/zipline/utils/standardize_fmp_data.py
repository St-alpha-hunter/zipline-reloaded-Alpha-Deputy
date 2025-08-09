import pandas as pd


def standardize_fmp_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize raw FMP data to uniform column format.

    Expected input: DataFrame with raw FMP fields.
    Output: Columns ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'dividend', 'split_ratio']
    """

    # 确保基础字段存在（FMP里有）
    expected_cols = ["date", "symbol", "open", "high", "low", "close", "volume", "dividend", "split_ratio"]

    # 添加默认值字段
    if "dividend" not in df.columns:
        df["dividend"] = 0.0
    if "split_ratio" not in df.columns:
        df["split_ratio"] = 1.0

    # 筛选字段，避免缺字段导致错误
    df = df[[col for col in expected_cols if col in df.columns]]

    # 按统一顺序排列列
    for col in expected_cols:
        if col not in df.columns:
            df[col] = 0.0 if col in ["dividend", "split_ratio"] else pd.NA

    df = df[expected_cols]
    return df
