import pandas as pd
def drop_duplicates_and_nulls(df: pd.DataFrame,) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates()
    df = df.dropna()
    return df
