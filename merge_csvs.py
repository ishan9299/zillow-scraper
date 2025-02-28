import pandas as pd
import glob
import os

def merge_csv_files(directory_path, output_file):
    csv_files = glob.glob(os.path.join(directory_path, "*.csv"))

    if not csv_files:
        print(f"No CSV files found in {directory_path}")
        return

    dfs = []

    for i, csv_file in enumerate(csv_files):
        print(f"Reading file {i+1}/{len(csv_files)}: {os.path.basename(csv_file)}")

        if i == 0:
            df = pd.read_csv(csv_file)
            dfs.append(df)
        else:
            df = pd.read_csv(csv_file, header=0)
            dfs.append(df)
    merged_df = pd.concat(dfs, ignore_index=True)

    merged_df.to_csv(output_file, index=False)
    print(f"Successfully merged {len(csv_files)} CSV files into {output_file}")
    print(f"Total rows in merged file: {len(merged_df)}")

if __name__ == "__main__":
    input_directory = "data/csv"
    output_file = "data/data.csv"

    merge_csv_files(input_directory, output_file)
