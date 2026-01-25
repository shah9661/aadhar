import pandas as pd
from typing import List, Dict, Any
def apply_value_map(
    df: pd.DataFrame,
    column: str,
    mapping: dict,
    dropna: bool = False
) -> pd.DataFrame:
    df = df.copy()
    df[column] = df[column].replace(mapping)
    if dropna:
        df = df.dropna(subset=[column])
    return df
def apply_state_district_rules(
    df: pd.DataFrame,
    rules: List[Dict[str, Any]],
    state_col: str = "state",
    district_col: str = "district"
) -> pd.DataFrame:
    df = df.copy()

    for rule in rules:
        mask = df[state_col] == rule["match_state"]

        if "match_district" in rule:
            mask &= df[district_col] == rule["match_district"]

        if "new_state" in rule:
            df.loc[mask, state_col] = rule["new_state"]

        if "new_district" in rule:
            df.loc[mask, district_col] = rule["new_district"]

    return df