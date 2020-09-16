import pandas as pd
import json

json_array = [{"lat":3,"lon":9},{"lat":3,"lon":9}]
data_list = []
for item in json_array:
    data_list.append([item["lat"],item["lat"]])

data_colnames_RawData = ['lat', 'lon']

df_RawData = pd.DataFrame(data_list, columns=data_colnames_RawData)
print(df_RawData.to_json(orient='records'))
# print([{"lat":3,"lon":9},{"lat":3,"lon":9}])