import pandas as pd
import glob
import os

# Directory containing the CSV files
directory = "/Users/vidhyakshayakannan/Documents/Cognitive Neuroscience Research/Python Experiments/data"  # Update this to your directory path

# Load all CSV files from all subdirectories
data_files = glob.glob(os.path.join(directory, '**', '*.csv'), recursive=True)

# Dictionary to store data by subject
subject_data = {}

for file_path in data_files:
    # Extract subject name (e.g., Lila1 from Lila1.1.csv)
    filename = os.path.basename(file_path)
    subject = filename.split('.')[0]

    # Read the CSV file
    df = pd.read_csv(file_path)

    # Separate data into in-tune and out-of-tune based on 'Tone'
    in_tune_df = df[df['Tone'] == 1][['Gap', 'RT']]
    out_of_tune_df = df[df['Tone'] == 2][['Gap', 'RT']]

    # Store data separately for in-tune and out-of-tune
    if subject not in subject_data:
        subject_data[subject] = {'in_tune': [], 'out_of_tune': []}
    subject_data[subject]['in_tune'].append(in_tune_df)
    subject_data[subject]['out_of_tune'].append(out_of_tune_df)

# Prepare final combined DataFrame
final_rows = []
for subject, data in subject_data.items():
    in_tune_combined = pd.concat(data['in_tune']).groupby('Gap', as_index=False)['RT'].mean()
    out_of_tune_combined = pd.concat(data['out_of_tune']).groupby('Gap', as_index=False)['RT'].mean()
    
    # Merge in-tune and out-of-tune data on 'Gap'
    merged_df = pd.merge(in_tune_combined, out_of_tune_combined, on='Gap', how='outer', suffixes=('_in_tune', '_out_of_tune'))
    merged_df['Subject'] = subject
    final_rows.append(merged_df)

# Concatenate all subjects' data
final_df = pd.concat(final_rows)[['Subject', 'Gap', 'RT_in_tune', 'RT_out_of_tune']]

# Save the result to a new CSV file
output_path = os.path.join(directory, "combined_subjects_averaged.csv")
final_df.to_csv(output_path, index=False)

print(f"Saved combined averaged data for all subjects to {output_path}")
print(final_df)