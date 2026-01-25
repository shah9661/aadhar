import pandas as pd
def rename_columns(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    df = df.copy()
    valid_mapping = {
        old: new
        for old, new in mapping.items()
        if old in df.columns
    }

    return df.rename(columns=valid_mapping)

def aggregate(df):
    return df.groupby(['date','state','district','pincode'], as_index=False).sum()
