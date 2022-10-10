import pandas as pd
import os

os.getcwd()

dfs = os.listdir("..\data\spotify")

output = []
for i in dfs:
    df = rf"..\data\spotify\{i}"
    pdf = pd.read_csv(df)
    output.append(pdf)


fdf = pd.concat(output)

x = fdf.sort_values(by=["artists", "trackname", "name_of_playlist"])
a = x[x['name_of_playlist'] == 'the one']
a = a.drop_duplicates(subset=["artists", "trackname"])
x = x.drop_duplicates(subset=["artists", "trackname"])

one_set = a.copy()
whole_set = x[x['name_of_playlist'] == 'the one']


z = pd.merge(one_set,whole_set, how = 'outer', on = 'track_id',indicator = True)

z[z['_merge'] == 'left_only']
z[z['_merge'] == 'right_only']


x[x['name_of_playlist'] == 'the five']

len(x)