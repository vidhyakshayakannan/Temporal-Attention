import pandas as pd

df = pd.read_csv('/Users/vidhyakshayakannan/Documents/Temporal-Attention/data/averaged/angelyn/angelyn_in_tune_avg_rt.csv')
angelyn_in_tune_average = df['AngelynInAveRT'].mean()


df = pd.read_csv('/Users/vidhyakshayakannan/Documents/Temporal-Attention/data/averaged/mahalakshmi/mahalakshmi_in_tune_avg_rt.csv')
maha_in_tune_average = df['MahalakshmiInAveRT'].mean()


df = pd.read_csv('/Users/vidhyakshayakannan/Documents/Temporal-Attention/data/averaged/angelyn/angelyn_out_of_tune_avg_rt.csv')
angelyn_out_tune_average = df['OutAveRT'].mean()


df = pd.read_csv('/Users/vidhyakshayakannan/Documents/Temporal-Attention/data/averaged/mahalakshmi/mahalakshmi_out_of_tune_avg_rt.csv')
maha_out_tune_average = df['OutAveRT'].mean()




data = {
    'In-Tune': [angelyn_in_tune_average, maha_in_tune_average],
    'Out-of-Tune': [angelyn_out_tune_average, maha_out_tune_average]
}

index = ['Angelyn', 'Mahalakshmi']

df = pd.DataFrame(data, index=index)

print(df)