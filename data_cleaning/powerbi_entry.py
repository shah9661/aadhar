from data_cleaning.pipeline import run_pipeline
from data_cleaning.merge import merge_dataframes
from data_cleaning.rules import keys,counts
enrol_df=run_pipeline("api_data_aadhar_enrolment")
demo_df=run_pipeline("api_data_aadhar_demographic")
bio_df=run_pipeline("api_data_aadhar_biometric")

final_df=merge_dataframes([enrol_df,demo_df,bio_df],keys,counts)
