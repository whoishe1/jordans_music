import pandas as pd
import os

dfs = os.listdir(".\data\spotify")

output = []
for i in dfs:
    df = rf".\data\spotify\{i}"
    pdf = pd.read_csv(df)
    output.append(pdf)


fdf = pd.concat(output)

x = fdf.sort_values(by=["artists", "trackname", "name_of_playlist"])

x = x.drop_duplicates(subset=["artists", "trackname"])
