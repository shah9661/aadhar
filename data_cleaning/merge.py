import pandas as pd
from functools import reduce
def merge_dataframes(
    dfs: list[pd.DataFrame],
    keys: list[str],
    fill_zero_cols: list[str]
) -> pd.DataFrame:
  # 1. Merge all DataFrames using outer join
    merged_df = reduce(
        lambda left, right: left.merge(right, on=keys, how='outer'),
        dfs
    )

    # 2. Fill NaN only in explicitly provided columns
    cols_to_fill = [c for c in fill_zero_cols if c in merged_df.columns]
    merged_df[cols_to_fill] = merged_df[cols_to_fill].fillna(0)

    # 3. Downcast integer columns (safe & memory efficient)
    for col in merged_df.select_dtypes(include=['int64', 'int32','float64']).columns:
        merged_df[col] = pd.to_numeric(merged_df[col], downcast='integer')

    return merged_df
