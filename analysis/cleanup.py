import os
import pandas as pd
from pathlib import Path

def process_participant_data(raw_dir='/Users/vidhyakshayakannan/Documents/Temporal-Attention/data/raw', 
                            output_dir='/Users/vidhyakshayakannan/Documents/Temporal-Attention/data/averaged',
                            rt_min=199, rt_max=1000):
    """
    Process participant CSV files and calculate RT averages per Gap.
    Removes outliers and incorrect responses before averaging.
    
    Args:
        raw_dir: Directory containing participant folders with CSV files
        output_dir: Directory where averaged results will be saved
        rt_min: Minimum acceptable RT (default: 199ms)
        rt_max: Maximum acceptable RT (default: 1000ms)
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all participant folders
    raw_path = Path(raw_dir)
    participant_folders = [f for f in raw_path.iterdir() if f.is_dir()]
    
    print(f"Processing {len(participant_folders)} participants...")
    print(f"RT range filter: {rt_min}-{rt_max} ms\n")
    
    for participant_folder in participant_folders:
        participant_name = participant_folder.name
        print(f"\nProcessing: {participant_name}")
        
        # Find all CSV files for this participant
        csv_files = sorted(list(participant_folder.glob(f"{participant_name}*.csv")))
        
        if not csv_files:
            print(f"  Warning: No CSV files found for {participant_name}")
            continue
        
        print(f"  Found {len(csv_files)} CSV files")
        
        # Read all CSV files
        all_data = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                all_data.append(df)
            except Exception as e:
                print(f"  Error reading {csv_file.name}: {e}")
        
        if not all_data:
            print(f"  Warning: No valid data for {participant_name}")
            continue
        
        # Concatenate all data
        combined_df = pd.concat(all_data, ignore_index=True)
        original_count = len(combined_df)
        
        # Filter out any missing RT values
        combined_df = combined_df.dropna(subset=['RT'])
        
        # Convert Key to string to handle any type issues
        combined_df['Key'] = combined_df['Key'].astype(str)
        
        # Remove RT outliers
        combined_df = combined_df[(combined_df['RT'] >= rt_min) & (combined_df['RT'] <= rt_max)].copy()
        after_rt_filter = len(combined_df)
        
        # Keep only correct responses: (Tone=1 & Key=M) OR (Tone=2 & Key=C)
        combined_df = combined_df[
            ((combined_df["Tone"] == 1) & (combined_df["Key"] == "M")) | 
            ((combined_df["Tone"] == 2) & (combined_df["Key"] == "C"))
        ].copy()
        after_correct_filter = len(combined_df)
        
        print(f"  Original trials: {original_count}")
        print(f"  After RT filter ({rt_min}-{rt_max}ms): {after_rt_filter} ({original_count - after_rt_filter} removed)")
        print(f"  After correct response filter: {after_correct_filter} ({after_rt_filter - after_correct_filter} removed)")
        
        if len(combined_df) == 0:
            print(f"  Warning: No valid data remaining for {participant_name}")
            continue
        
        # Create participant output folder
        participant_output_dir = Path(output_dir) / participant_name
        os.makedirs(participant_output_dir, exist_ok=True)
        
        # Calculate in-tune averages per Gap (Tone = 1, Key = M)
        intune_data = combined_df[combined_df['Tone'] == 1]
        if len(intune_data) > 0:
            intune_avg_per_gap = intune_data.groupby('Gap')['RT'].mean().reset_index()
            intune_avg_per_gap.columns = ['Gap', f'{participant_name}InAveRT']
            intune_avg_per_gap = intune_avg_per_gap.sort_values('Gap')
            intune_avg_per_gap.to_csv(participant_output_dir / f"{participant_name}_inavg.csv", index=False)
            print(f"  In-tune: {len(intune_avg_per_gap)} gap values averaged ({len(intune_data)} trials)")
        
        # Calculate out-of-tune averages per Gap (Tone = 2, Key = C)
        outtune_data = combined_df[combined_df['Tone'] == 2]
        if len(outtune_data) > 0:
            outtune_avg_per_gap = outtune_data.groupby('Gap')['RT'].mean().reset_index()
            outtune_avg_per_gap.columns = ['Gap', f'{participant_name}OutAveRT']
            outtune_avg_per_gap = outtune_avg_per_gap.sort_values('Gap')
            outtune_avg_per_gap.to_csv(participant_output_dir / f"{participant_name}_outavg.csv", index=False)
            print(f"  Out-of-tune: {len(outtune_avg_per_gap)} gap values averaged ({len(outtune_data)} trials)")
        
        # Calculate combined averages per Gap (all correct responses)
        combined_avg_per_gap = combined_df.groupby('Gap')['RT'].mean().reset_index()
        combined_avg_per_gap.columns = ['Gap', f'{participant_name}CombinedAveRT']
        combined_avg_per_gap = combined_avg_per_gap.sort_values('Gap')
        combined_avg_per_gap.to_csv(participant_output_dir / f"{participant_name}_combinedavg.csv", index=False)
        print(f"  Combined: {len(combined_avg_per_gap)} gap values averaged ({len(combined_df)} trials)")
    
    print("\n✓ Processing complete!")
    print(f"Results saved to '{output_dir}' directory")

if __name__ == "__main__":
    # Run the processing
    # You can adjust rt_min and rt_max if needed
    process_participant_data(rt_min=199, rt_max=1000)