import pandas as pd
from utils import setup_logger, get_args, taxi_preprocess_and_save

if __name__ == "__main__":
    Logger = setup_logger("NYS YT Preprocessor")
    try:
        args = get_args()

        Logger.info(f"--- Starting Preprocessing for {args.input_file} ---")

        taxi_preprocess_and_save(args.input_file, args.output_file, args.freq_maps_file)

    except Exception as e:
        Logger.error(f"Failed to preprocess {args.input_file}: {e}")
    else:
        Logger.info(
            f"Successfully saved cleaned data to {args.output_file} and {args.freq_maps_file}"
        )
        df = pd.read_parquet(args.output_file)
        print(df.head())
        print(df.info(show_counts=True))
