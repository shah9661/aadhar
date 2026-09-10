from data_cleaning.pipeline import run_pipeline
from database.connection import load_to_postgres


def main():

    print("Starting Aadhaar data pipeline...")

    print("\nProcessing enrolment data...")

    enrol_df = run_pipeline("api_data_aadhar_enrolment")

    print("\nProcessing demographic data...")

    demo_df = run_pipeline("api_data_aadhar_demographic")

    print("\nProcessing biometric data...")

    bio_df = run_pipeline("api_data_aadhar_biometric")

    print("\nLoading data into PostgreSQL...")

    load_to_postgres(enrol_df,"fact_enrolment")

    load_to_postgres( demo_df,"fact_demographic")

    load_to_postgres(bio_df,"fact_biometric")

    print("\nPipeline completed successfully!")

if __name__ == "__main__":
    main()