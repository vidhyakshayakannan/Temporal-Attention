import os
import pandas as pd
from pathlib import Path

def process_participant_data(raw_dir='/Users/vidhyakshayakannan/Documents/Temporal-Attention/data/raw', 
                            output_dir='/Users/vidhyakshayakannan/Documents/Temporal-Attention/data/averaged',
                            rt_min=199, rt_max=1000,
                            gap_min=50, gap_max=500):
    """
    Process participant CSV files and calculate RT averages per Gap.
    Removes outliers and incorrect responses before averaging.
    Fills missing gap values with interpolated values.
    
    Args:
        raw_dir: Directory containing participant folders with CSV files
        output_dir: Directory where averaged results will be saved
        rt_min: Minimum acceptable RT (default: 199ms)
        rt_max: Maximum acceptable RT (default: 1000ms)
        gap_min: Minimum gap value to include (default: 50ms)
        gap_max: Maximum gap value to include (default: 500ms)
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all participant folders
    raw_path = Path(raw_dir)
    participant_folders = [f for f in raw_path.iterdir() if f.is_dir()]
    
    print(f"Processing {len(participant_folders)} participants...")
    print(f"RT range filter: {rt_min}-{rt_max} ms")
    print(f"Gap range filter: {gap_min}-{gap_max} ms\n")
    
    # Determine all unique gap values across all participants (within valid range)
    all_gaps_set = set()
    for participant_folder in participant_folders:
        csv_files = list(participant_folder.glob(f"{participant_folder.name}*.csv"))
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                # Filter gaps to valid range
                valid_gaps = df[(df['Gap'] >= gap_min) & (df['Gap'] <= gap_max)]['Gap'].unique()
                all_gaps_set.update(valid_gaps)
            except:
                pass
    
    all_gaps = sorted(list(all_gaps_set))
    print(f"Found {len(all_gaps)} unique gap values across all participants: {min(all_gaps) if all_gaps else 'N/A'} to {max(all_gaps) if all_gaps else 'N/A'}\n")
    
    if not all_gaps:
        print("Error: No valid gap values found!")
        return
    
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
        
        # Filter gap values to valid range
        combined_df = combined_df[(combined_df['Gap'] >= gap_min) & (combined_df['Gap'] <= gap_max)].copy()
        
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
        print(f"  After gap/RT filters: {after_rt_filter}")
        print(f"  After correct response filter: {after_correct_filter} ({after_rt_filter - after_correct_filter} removed)")
        
        if len(combined_df) == 0:
            print(f"  Warning: No valid data remaining for {participant_name}")
            continue
        
        # Create participant output folder
        participant_output_dir = Path(output_dir) / participant_name
        os.makedirs(participant_output_dir, exist_ok=True)
        
        # Helper function to fill missing gaps with interpolation
        def fill_missing_gaps(df_avg, all_gaps, participant_name, rt_col_name):
            """Fill missing gap values with linear interpolation (average of prev and next)"""
            # Create a complete dataframe with all gaps
            complete_df = pd.DataFrame({'Gap': all_gaps})
            
            # Merge with existing data
            merged_df = complete_df.merge(df_avg, on='Gap', how='left')
            
            # Interpolate missing values (linear interpolation between neighbors)
            merged_df[rt_col_name] = merged_df[rt_col_name].interpolate(method='linear', limit_direction='both')
            
            # Report which gaps were filled
            missing_gaps = complete_df[~complete_df['Gap'].isin(df_avg['Gap'])]['Gap'].tolist()
            if missing_gaps:
                print(f"    Filled {len(missing_gaps)} missing gaps with interpolation")
            
            return merged_df
        
        # Calculate in-tune averages per Gap (Tone = 1, Key = M)
        intune_data = combined_df[combined_df['Tone'] == 1]
        if len(intune_data) > 0:
            intune_avg_per_gap = intune_data.groupby('Gap')['RT'].mean().reset_index()
            intune_avg_per_gap.columns = ['Gap', f'{participant_name}InAveRT']
            intune_avg_per_gap = intune_avg_per_gap.sort_values('Gap')
            
            # Fill missing gaps
            intune_avg_per_gap = fill_missing_gaps(
                intune_avg_per_gap, all_gaps, participant_name, f'{participant_name}InAveRT'
            )
            
            intune_avg_per_gap.to_csv(participant_output_dir / f"{participant_name}_inavg.csv", index=False)
            print(f"  In-tune: {len(all_gaps)} gap values (from {len(intune_data)} trials)")
        
        # Calculate out-of-tune averages per Gap (Tone = 2, Key = C)
        outtune_data = combined_df[combined_df['Tone'] == 2]
        if len(outtune_data) > 0:
            outtune_avg_per_gap = outtune_data.groupby('Gap')['RT'].mean().reset_index()
            outtune_avg_per_gap.columns = ['Gap', f'{participant_name}OutAveRT']
            outtune_avg_per_gap = outtune_avg_per_gap.sort_values('Gap')
            
            # Fill missing gaps
            outtune_avg_per_gap = fill_missing_gaps(
                outtune_avg_per_gap, all_gaps, participant_name, f'{participant_name}OutAveRT'
            )
            
            outtune_avg_per_gap.to_csv(participant_output_dir / f"{participant_name}_outavg.csv", index=False)
            print(f"  Out-of-tune: {len(all_gaps)} gap values (from {len(outtune_data)} trials)")
        
        # Calculate combined averages per Gap (all correct responses)
        combined_avg_per_gap = combined_df.groupby('Gap')['RT'].mean().reset_index()
        combined_avg_per_gap.columns = ['Gap', f'{participant_name}CombinedAveRT']
        combined_avg_per_gap = combined_avg_per_gap.sort_values('Gap')
        
        # Fill missing gaps
        combined_avg_per_gap = fill_missing_gaps(
            combined_avg_per_gap, all_gaps, participant_name, f'{participant_name}CombinedAveRT'
        )
        
        combined_avg_per_gap.to_csv(participant_output_dir / f"{participant_name}_combinedavg.csv", index=False)
        print(f"  Combined: {len(all_gaps)} gap values (from {len(combined_df)} trials)")
    
    print("\n✓ Processing complete!")
    print(f"Results saved to '{output_dir}' directory")

if __name__ == "__main__":
    # Run the processing
    # You can adjust rt_min, rt_max, gap_min, and gap_max if needed
    process_participant_data(rt_min=199, rt_max=1000, gap_min=50, gap_max=500)