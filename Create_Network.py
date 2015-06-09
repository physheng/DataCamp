# Read json file and print dictionary
import json
import numpy as np
import pandas as pd
import itertools

# Load json file
data = []
with open('test.json') as f:
	for line in f:
		data.append(json.loads(line))

df = pd.DataFrame(data)
df_sorted = df.sort('year')

network = open('gameNetwork.csv','w')
#print df_sorted
for index, row in df_sorted.iterrows():
	if len(row['Credits']) > 1:
		developer_pair = list(itertools.combinations(row['Credits'],2))
		for j in range(len(developer_pair)):
			#print (developer_pair[j][0], developer_pair[j][1], row['year'])
			network.write("%s, %s, %s\n" %(developer_pair[j][0], developer_pair[j][1], row['year']) )

network.close()


# # Create network file
# network = open('gameNetwork.csv','w')
# for i in range(len(data)):
# #for key in data[i]:
# 	if len(data[i]["Credits"]) == 1:
# 		network.write("%s, %s, %s\n" %(data[i]['Credits'], data[i]['Credits'], data[i]['year']))
# 	elif len(data[i]['Credits']) > 1:
# 		developer_pair = list(itertools.combinations(data[i]['Credits'],2))
# 		for j in range(len(developer_pair)):
# 			network.write("%s, %s, %s\n" %(developer_pair[j][0], developer_pair[j][1], data[i]['year']) )
# 	else:
# 		pass

# network.close()

