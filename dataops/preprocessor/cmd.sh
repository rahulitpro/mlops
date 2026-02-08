#!/bin/bash

python nys_yellow_taxi_tripdata_preprocessor.py -i data/raw/ -o data/preprocessed/cleaned_yellow_tripdata.parquet -f data/preprocessed/cleaned_yellow_tripdata_freq_maps.json