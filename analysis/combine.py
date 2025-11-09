from pathlib import Path
import pandas as pd

base_dir = Path("data/averaged")

patterns = {
    "combinedInAveRT": "*/*_inavg.csv",
    "combinedOutAveRT": "*/*_outavg.csv",
    "combinedAveRT": "*/*_combinedavg.csv"
}

output_dir = base_dir / "all_combined"
output_dir.mkdir(exist_ok=True)

def combine_and_average(pattern, output_name):
    files = list(base_dir.glob(pattern))
    if not files:
        print(f"No files found for {pattern}")
        return

    dfs = []
    for f in files:
        df = pd.read_csv(f)
        dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)

    # Identify the numeric column that’s not 'Gap'
    numeric_cols = [col for col in combined_df.select_dtypes(include='number').columns if col.lower() != 'gap']

    if not numeric_cols:
        print(f"No numeric RT column found in files matching {pattern}")
        return

    rt_col = numeric_cols[0]  # usually something like combinedInAveRT, etc.

    # Average across participants grouped by Gap
    avg_df = (
        combined_df.groupby("Gap", as_index=False)[rt_col]
        .mean()
        .rename(columns={rt_col: output_name})
    )

    # Save output
    output_path = output_dir / f"{output_name}.csv"
    avg_df.to_csv(output_path, index=False)
    print(f"✅ Saved {output_path} with {len(avg_df)} rows.")

# Run all
for name, pattern in patterns.items():
    combine_and_average(pattern, name)
