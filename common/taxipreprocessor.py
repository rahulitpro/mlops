import pandas as pd
import json


class TaxiPreprocessor:
    def __init__(self, freq_map_path=None):
        self.freq_maps = {}
        if freq_map_path:
            with open(freq_map_path, "r") as f:
                self.freq_maps = json.load(f)

    def transform(self, df):
        """Applies the same logic used in preprocessing."""
        df = df.copy()

        # 1. Feature Extraction from datetime
        if not pd.api.types.is_datetime64_any_dtype(df["tpep_pickup_datetime"]):
            df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])

        df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
        df["pickup_day_of_week"] = df["tpep_pickup_datetime"].dt.dayofweek
        df["pickup_month"] = df["tpep_pickup_datetime"].dt.month

        # 2. Apply Frequency Encoding (using the saved JSON mappings)
        for col in ["PULocationID", "DOLocationID"]:
            if col in self.freq_maps:
                # Map using the JSON keys (strings). Default to 0.0 if ID is new/unknown
                df[col] = df[col].astype(str).map(self.freq_maps[col]).fillna(0.0)

        # 3. Drop the raw datetime column used for training
        df = df.drop(columns=["tpep_pickup_datetime"])

        # Ensure column order matches what the model expects
        expected_cols = [
            "PULocationID",
            "DOLocationID",
            "trip_distance",
            "pickup_hour",
            "pickup_day_of_week",
            "pickup_month",
        ]
        return df[expected_cols]
