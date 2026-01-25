from data_cleaning.overrides import apply_state_district_rules
from data_cleaning.rules import*
from data_cleaning.loaders import load_and_optimize_csv
from data_cleaning.text_clean import normalize_columns
from data_cleaning.duplicated import drop_duplicates_and_nulls
from data_cleaning.overrides import*
from data_cleaning.fixes import*
from data_cleaning.rules import*
from data_cleaning.transform import aggregate,rename_columns

def run_pipeline(pattern):
    df = load_and_optimize_csv(pattern) # load data 

    df = drop_duplicates_and_nulls(df) # remove dulicate and null

    df = normalize_columns(df, ['state','district']) # normalize

    df = apply_value_map(df,'state',state_fix_map) # fixing state

    df = apply_state_district_rules(df,state_district_rules) # remove imbiguity

    df = apply_value_map(df,'district',district_fix_map) # fixing district
    
    df = apply_special_fixes(df) # name correct

    df= fix_state_by_district(df,andhra_pradesh_to_telangana) # state andhra pradesh to ladkh 

    df= fix_state_by_district(df,jammu_kashmir_to_ladakh) # state jammu kashmir to ladakh
    df= rename_columns(df,rename_column)
    df = aggregate(df) # sum of all fixis

    return df