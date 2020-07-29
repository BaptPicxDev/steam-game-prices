#############################################
# author : Baptiste PICARD 		 			#
# date : 25/07/2020				 			#
# 								 			#
# overview : Study the Games and the 		#
# Prices of the Steam apps.					#
#											#
#############################################

# Imports
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt

# Modules 
from access import * 

# Functions 
def getCollectionInfo(collection) :
	print("\nGetting info about the collection {}".format(collection.name))
	df = pd.DataFrame(list(collection.find({})))
	df = df.drop('_id', axis=1)
	print("Shape : {} (rows/cols)".format(df.shape))
	print("{} Columns : {}".format(len(df.columns), df.columns))
	print("{} uniques steam index.".format(len(df['steam_id'].unique())))
	for col in df.columns : 
		if(col!="index" and col!="prices" and col!="steam_id") :
			print('-> Column : {}'.format(col)) 
			print("{} unique values".format(len(df[col].unique())))
			if(col=='type') : 
				print("Unique values : {}".format(df[col].unique()))
	print("-------------------------------")

def getTypePropotion(collection_games) : 
	print("Visualization of the type proportion in the collection :  {}".format(collection_games.name))
	df = pd.DataFrame(list(collection_games.find({})))
	total = df.type.count()
	plt.figure(figsize=(16,9))
	plt.title("Type proportion in "+str(collection_games.name))
	ax = sns.countplot(x='type',data=df)
	for p in ax.patches:
		ax.annotate('{}%'.format((p.get_height()/total)*100), (p.get_x()+0.21, p.get_height()+1))
	plt.xlabel("App type")
	plt.show()

def getPriceEvolution(collection_prices, steam_id) : 
	print("Visualization of the evolution of a steam game :  {}".format(steam_id))
	if(collection_prices.find({'steam_id' : steam_id}).count() > 0) : 
		prices = collection_prices.find_one({'steam_id' : steam_id})['prices']
		x, y, ticks = [], [], []
		for item in prices : 
			x.append(item['index'])
			ticks.append(str(item['datetime'].strftime("%d/%m/%Y")))
			y.append(item['price'])
		plt.figure(figsize=(16,9))
		plt.title("Price evolution of "+str(collection_prices.find_one({'steam_id' : steam_id})['steam_id']))
		plt.xticks([i for i in range(0, len(prices), 1)], ticks, rotation=45)
		sns.lineplot(x=x, y=y, markers=True)
		plt.xlabel("Time")
		plt.ylabel("Price ("+prices[0]['currency']+")")
		plt.show()
	else  :
		print('No steam app : {}'.format(steam_id)) 