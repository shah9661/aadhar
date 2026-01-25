import pandas as pd
from typing import List
def apply_special_fixes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df.loc[(df['state'] == 'maharashtra') & (df['district'] == 'raigarh'), 'district'] = 'raigad'
    df.loc[(df['district'] == 'rupnagar') & (df['state'] == 'chandigarh'), 'state'] = 'punjab'
    df.loc[(df['district'] == 'bijapur') & (df['state'] == 'karnataka'), 'district'] = 'vijayapura'
    df.loc[(df['district'] == 'kamrup') & (df['state'] == 'meghalaya'), 'state'] = 'assam'

    return df

def fix_state_by_district(
    df: pd.DataFrame,
    rules: List[dict],
    state_col: str = "state",
    district_col: str = "district"
) -> pd.DataFrame:

    df = df.copy()

    for rule in rules:
        mask = (
            df[district_col].isin(rule["districts"]) &
            (df[state_col] == rule["from_state"])
        )
        df.loc[mask, state_col] = rule["to_state"]

    return df


