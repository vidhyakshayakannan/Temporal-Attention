import pandas as pd
import numpy as np
import glob
import os

# Directory containing the CSV files
directory = "/Users/vidhyakshayakannan/Documents/Temporal-Attention/data" 

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
    df = df[(df['RT'] >= 199) & (df['RT'] <= 1000)].copy()
    df = df[(df["Tone"] == 1) & (df["Key"] == "M") | (df["Tone"] == 2) & (df["Key"] == "C")]

    # Separate data into in-tune and out-of-tune based on 'Tone'
    in_tune_df = df[df['Tone'] == 1][['Gap', 'RT']]
    out_of_tune_df = df[df['Tone'] == 2][['Gap', 'RT']]

    # Store data separately for in-tune and out-of-tune
    if subject not in subject_data:
        subject_data[subject] = {'in_tune': [], 'out_of_tune': []}
    subject_data[subject]['in_tune'].append(in_tune_df)
    subject_data[subject]['out_of_tune'].append(out_of_tune_df)

# Prepare final data structure
subjects = list(subject_data.keys())
all_gaps = sorted(set(pd.concat([pd.concat(subject_data[subj]['in_tune'] + subject_data[subj]['out_of_tune'])['Gap'] for subj in subjects])))

data_matrix = np.zeros((len(subjects), len(all_gaps), 2))  # Shape: (subjects, gaps, 2 conditions)

gap_to_index = {gap: i for i, gap in enumerate(all_gaps)}

for subj_index, subject in enumerate(subjects):
    in_tune_combined = pd.concat(subject_data[subject]['in_tune']).groupby('Gap', as_index=False)['RT'].mean()
    out_of_tune_combined = pd.concat(subject_data[subject]['out_of_tune']).groupby('Gap', as_index=False)['RT'].mean()
    
    for _, row in in_tune_combined.iterrows():
        data_matrix[subj_index, gap_to_index[row['Gap']], 0] = row['RT']
    for _, row in out_of_tune_combined.iterrows():
        data_matrix[subj_index, gap_to_index[row['Gap']], 1] = row['RT']

# Print 3D array
print("Final 3D NumPy Array Shape:", data_matrix.shape)
print(data_matrix)