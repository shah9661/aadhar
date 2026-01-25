import pandas as pd
def normalize_text(series: pd.Series) -> pd.Series:
    return (
        series
        .astype(str)
        .str.lower()
        .str.strip()

        # replace mojibake dash artifacts with space
        .str.replace(r'â[\x80-\x9f]+', ' ', regex=True)

        # replace all hyphen/dash variants with space (FIXED)
        .str.replace(r'[-‐‒–—−]', ' ', regex=True)
        .str.replace(r'[‐-‒–—−]', ' ', regex=True)

        # replace punctuation/symbols with space
        .str.replace(r'[?&/.,*\'"]', ' ', regex=True)

        # remove bracketed text
        .str.replace(r'\(.*?\)', '', regex=True)

        # collapse multiple spaces
        .str.replace(r'\s+', ' ', regex=True)
        .str.strip()
    )
def normalize_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in cols:
        if col in df.columns:
            df[col] = normalize_text(df[col])
    return df
# This internally call two functions
