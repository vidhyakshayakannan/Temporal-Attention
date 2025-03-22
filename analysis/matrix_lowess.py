import pandas as pd
import numpy as np
import glob
import os
from statsmodels.nonparametric.smoothers_lowess import lowess

def process_csv_files(file_paths):
    # List to store data from each file
    data_list = []
    
    for file in file_paths:
        df = pd.read_csv(file)
        
        # Extract subject name from filename
        subject_name = os.path.basename(file).split('.')[0]
        df['Subject Name'] = subject_name
        
        # Group by Gap and compute Average RT in Tune and Out of Tune
        gap_grouped = df.groupby('Gap').apply(lambda x: pd.Series({
            'Average RT In Tune': x[(x['Tone'] == 1) & (x['Key'] == 'M')]['RT'].mean(),
            'Average RT Out of Tune': x[(x['Tone'] == 2) & (x['Key'] == 'C')]['RT'].mean()
        })).reset_index()
        
        gap_grouped['Subject Name'] = subject_name
        
        # Fill NaN values with the average of previous and next gap values
        for col in ['Average RT In Tune', 'Average RT Out of Tune']:
            gap_grouped[col] = gap_grouped[col].interpolate(method='linear', limit_direction='both')
        
        # Apply LOWESS smoothing
        frac = 0.4 
        gap_grouped['Smoothed RT In Tune'] = lowess(gap_grouped['Average RT In Tune'], gap_grouped['Gap'], frac=frac, return_sorted=False)
        gap_grouped['Smoothed RT Out of Tune'] = lowess(gap_grouped['Average RT Out of Tune'], gap_grouped['Gap'], frac=frac, return_sorted=False)
        
        # Append to list
        data_list.append(gap_grouped)
    
    # Concatenate all data into a single DataFrame
    full_data = pd.concat(data_list, ignore_index=True)
    
    # Convert DataFrame to 3D NumPy array (Subjects x Features)
    subjects = full_data['Subject Name'].unique()
    num_subjects = len(subjects)
    num_features = 4  # RT In Tune, RT Out of Tune, Gap, Subject Name (as string dtype)
    
    dtype = np.dtype([('Subject Name', 'U50'), ('Smoothed RT In Tune', 'f8'), ('Smoothed RT Out of Tune', 'f8'), ('Gap', 'f8')])
    array_3d = np.zeros(num_subjects, dtype=dtype)
    
    subject_map = {subj: i for i, subj in enumerate(subjects)}
    count = 0
    for idx, row in full_data.iterrows():
        subject_idx = subject_map[row['Subject Name']]
        array_3d[subject_idx] = (row['Subject Name'], row['Smoothed RT In Tune'], row['Smoothed RT Out of Tune'], row['Gap'])
    
        # Print values for every gap
        print(f"Subject: {row['Subject Name']}, Gap: {row['Gap']}, Smoothed RT In Tune: {row['Smoothed RT In Tune']}, Smoothed RT Out of Tune: {row['Smoothed RT Out of Tune']}")
        count = count+1
    print(count)
    return full_data, array_3d
    

file_paths = ["/Users/vidhyakshayakannan/Documents/Cognitive Neuroscience Research/Python Experiments/lila/Lila1.1.csv", "/Users/vidhyakshayakannan/Documents/Cognitive Neuroscience Research/Python Experiments/lila/Lila1.2.csv", "/Users/vidhyakshayakannan/Documents/Cognitive Neuroscience Research/Python Experiments/lila/Lila1.3.csv","/Users/vidhyakshayakannan/Documents/Cognitive Neuroscience Research/Python Experiments/navya/Navya1.1.csv", "/Users/vidhyakshayakannan/Documents/Cognitive Neuroscience Research/Python Experiments/navya/Navya1.2.csv", "/Users/vidhyakshayakannan/Documents/Cognitive Neuroscience Research/Python Experiments/navya/Navya1.3.csv", "/Users/vidhyakshayakannan/Documents/Cognitive Neuroscience Research/Python Experiments/soumeya/Soumeya1.1.csv"]
processed_df, array_3d = process_csv_files(file_paths)

processed_df.to_csv("/Users/vidhyakshayakannan/Documents/Cognitive Neuroscience Research/Python Experiments/processed_data.csv", index=False)
np.save("/Users/vidhyakshayakannan/Documents/Cognitive Neuroscience Research/Python Experiments/rt_data_3d.npy", array_3d)

subject_counts = processed_df['Subject Name'].value_counts()
print(subject_counts)