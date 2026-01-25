from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def load_and_optimize_csv(folder: str) -> pd.DataFrame:
    base_dir = PROJECT_ROOT / folder
    files = list(base_dir.glob("*.csv"))

    if not files:
        raise FileNotFoundError(f"No CSV files found in {base_dir}")
    
    df = pd.concat(
        (pd.read_csv(f) for f in files),
        ignore_index=True
    )

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')

    return df
