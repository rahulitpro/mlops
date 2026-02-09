import pandas as pd
import os
import argparse
import logging
from pythonjsonlogger import jsonlogger
import json


def taxi_preprocess_and_save(input_path, output_path, freq_maps_file):
    # 1. Load data
    df = pd.read_parquet(input_path, engine="pyarrow")

    # 2. Selection & Initial Cleaning
    # Using double brackets to avoid the KeyError we discussed earlier
    cols = [
        "PULocationID",
        "DOLocationID",
        "trip_distance",
        "tpep_pickup_datetime",
        "total_amount",
    ]
    df_preprocessed = df[cols].copy()

    # 3. Outlier Filtering
    # These thresholds are your "Silver" layer business rules
    initial_count = len(df_preprocessed)
    df_preprocessed = df_preprocessed[
        (df_preprocessed["trip_distance"] > 0)
        & (df_preprocessed["trip_distance"] < 100)
        & (df_preprocessed["total_amount"] > 2.5)
        & (df_preprocessed["total_amount"] < 500)
    ].copy()

    print(f"Filtered {initial_count - len(df_preprocessed)} outlier rows.")
    # 4. Feature Extraction
    df_preprocessed["pickup_hour"] = df_preprocessed["tpep_pickup_datetime"].dt.hour
    df_preprocessed["pickup_day_of_week"] = df_preprocessed[
        "tpep_pickup_datetime"
    ].dt.dayofweek
    df_preprocessed["pickup_month"] = df_preprocessed["tpep_pickup_datetime"].dt.month
    df_preprocessed.drop(columns=["tpep_pickup_datetime"], inplace=True)

    # 5. Frequency encoding for catagorical features
    freq_artifacts = {}

    for col in ["PULocationID", "DOLocationID"]:
        # Calculate frequency map
        freq_map = df_preprocessed[col].value_counts(normalize=True).to_dict()

        # Store for JSON (convert int keys to str)
        freq_artifacts[col] = {str(k): v for k, v in freq_map.items()}

        # Map the current dataframe
        df_preprocessed[col] = df_preprocessed[col].map(freq_map)

    # Save the frequency maps for future inference
    artifact_path = freq_maps_file
    with open(artifact_path, "w") as f:
        json.dump(freq_artifacts, f, indent=4)

    print(f"Saved frequency encoding artifacts to {artifact_path}")

    # 6. Data Validation (The MLOps Gatekeeper)
    if validate_weekly_data(df_preprocessed):
        # 6. Save Cleaned Data
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_preprocessed.to_parquet(output_path)
        return True
    else:
        print("Pipeline Stopped: Data Validation Failed.")
        return False


def validate_weekly_data(df):
    # Detect Data Drift
    corr = df["trip_distance"].corr(df["total_amount"])
    if corr < 0.80:
        print(f"ALERT: Correlation is {corr:.2f}. Potential Data Corruption.")
        return False

    # Check for unexpected negatives
    if (df["total_amount"] < 0).any():
        print("ALERT: Negative fares detected.")
        return False

    print(f"Validation Passed: Correlation is {corr:.2f}")
    return True


def setup_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_file",
        required=True,
        help="NYS Yellow Taxi raw data in parquet format",
        type=str,
    )
    parser.add_argument(
        "-o",
        "--output_file",
        required=True,
        help="Location to save NYS Yellow Taxi preprocessed data in parquet format",
        type=str,
    )
    parser.add_argument(
        "-f",
        "--freq_maps_file",
        required=True,
        help="Location to save NYS Yellow Taxi frequency maps in json format",
        type=str,
    )
    args = parser.parse_args()
    # Validation: Does the input path exist?
    if not os.path.exists(args.input_file):
        print(f"Input file not found: {args.input_file}")
        exit(1)  # Exit with error code for the orchestrator to see
    return args
