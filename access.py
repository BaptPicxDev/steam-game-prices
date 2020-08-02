# -*- coding: utf-8 -*-

#############################################
# author : Baptiste PICARD 		 			#
# date : 26/07/2020				 			#
# 								 			#
# overview : Access database and 			#
# collections.  							#
#											#
#############################################

## Imports
import os 
import csv
import time #  
import json # Reading .json files
import pandas as pd 
import datetime # Time computation
import pymongo
from urllib2 import urlopen

# Modules 

# Functions 
def openDatabase(json_mongoDB) : 
	"""
		overview : return the database (using pymongo) which contains all the collection.
		entries :
			- json_file : The data loaded are data in json format. This data provide information about the connection.
		returns :
			- database : database NoSql (mongoDB) with all collections.
	"""
	link = json_mongoDB['link']
	link = link.replace('<user>', json_mongoDB['id']).replace('<password>', json_mongoDB['pwd']).replace('<dbname>', json_mongoDB['database'])
	client = pymongo.MongoClient(link)
	return client[json_mongoDB['database']]

def getCollection(db, collection_name) :
	"""
		overview : return the collection with all the datas in, using a database and the collection_name.
		inputs :
			- database :  database NoSql which contains all the collection.
			- collection_name : string which represents the name of the collection.
		returns :
			- collection : collection with all its datas.
	"""
	return db[collection_name] 

def eraseCollection(collection) :
	"""
		overview : Erase all the elements of the collection.
		entries :
			- collection : collection of our database.
	"""
	print('Deleting all the datas in the database : ',str(collection.name))
	collection.delete_many({})

def fillGamesCollection(games_collection, items) : 
	"""
		overview : fill a collection.
			Each item is a dictionnary.
		inputs : 
			- collection : mongoDB collection.
			- items :  list of item. 
	"""
	print('Fill the collection : ', str(games_collection.name))
	print('{} items to check.'.format(str(len(items))))
	cmpt = 0
	for index_item, item in enumerate(items) : 
		if(games_collection.find({"steam_id" : item["steam_id"]}).count() > 0 ) :
			print("{}/{} - Steam App {} already exists.".format(index, len(items), games_collection.name, item["steam_id"]))
		else :
			item['index'] = games_collection.count()
			item['steam_id'] = int(item['steam_id'])
			flag = True  
			while(flag) : 
				try : 
					data = json.load(urlopen('http://store.steampowered.com/api/appdetails?appids='+str(item["steam_id"])))[str(item["steam_id"])]
					if(data['success']==True and 'release_date' in data['data'].keys()) :
						item['release_date'] = data['data']['release_date']['date']
						item['coming_soon'] = data['data']['release_date']['coming_soon']
						flag=False
					else : 
						break
				except Exception as exc : 
					print("{} - Can't loaded data from Steam API : {}".format(index_item, exc))
					time.sleep(20)
			games_collection.insert_one(item)
			print("{}/{} - {} filled : {} - {}".format(index, len(items), games_collection.name, cmpt + 1, games_collection.find_one({"steam_id" : item["steam_id"]})['steam_id']))
			cmpt += 1
	print('Collection filled with ',cmpt,' items.')

def fillPricesCollection(games_collection, prices_collection) : 
	"""
		overview : fill a collection.
			Each item is a dictionnary.
		inputs : 
			- collection : mongoDB collection.
			- items :  list of item. 
	"""
	print('Fill the collection : ', str(prices_collection.name))
	cmpt = 0
	for index, item in enumerate(games_collection.find({})) :
		if(prices_collection.find({"steam_id" : item["steam_id"]}).count() == 0 or prices_collection.find_one({"steam_id" : item["steam_id"]})['prices'][-1]['date'] < datetime.date.today().strftime('%Y-%m-%d')) :
			flag = True
			while(flag) : 		
				try : 
					data = json.load(urlopen('http://store.steampowered.com/api/appdetails?appids='+str(item["steam_id"])))[str(item["steam_id"])]
					flag = False 
				except Exception as excp :
					print("{} - {}.".format(index, excp))
					time.sleep(60)			 
			if(data['success'] == True) :
				if('price_overview' in data['data'].keys()) : 
					prices = data['data']['price_overview']
					new_price = {
							"index" : 0, "date" : datetime.date.today().strftime('%Y-%m-%d'), 'is_free' : False, 'currency': prices['currency'], 
							'discount_percent': prices['discount_percent'], 
							'price': float(prices['final_formatted'].replace(',', '.').replace('-', '').replace('€', '').replace('CDN$', ''))
							}
				else : 
					prices = data['data']
					new_price = {
							"index" : 0, "date" : datetime.date.today().strftime('%Y-%m-%d'), "is_free": prices['is_free'], 
							"currency": "EUR", "discount_percent": 0, "price": 0.0
							}
				if(prices_collection.find({"steam_id" : item["steam_id"]}).count() > 0) :
					new_price['index'] = len(prices_collection.find_one({"steam_id" : item["steam_id"]})['prices'])
					if(prices_collection.find_one({'steam_id' : item["steam_id"]})['prices'][-1]["date"] != new_price['date']) :
						prices_collection.update_one({"steam_id" : item["steam_id"]},{'$push': {'prices': new_price}})
						print("{}/{} - {} filled : {} - {}".format(index, games_collection.find({}).count(), prices_collection.name, cmpt + 1, prices_collection.find_one({"steam_id" : item["steam_id"]})['steam_id']))
					else : 
						print("{}/{} - {} can't be filled. There is already a price for {} the {} ".format(index, games_collection.find({}).count(), prices_collection.name, prices_collection.find_one({"steam_id" : item["steam_id"]})["steam_id"], prices_collection.find_one({"steam_id" : item["steam_id"]})['steam_id'], new_price['date']))
				else : 
					new_item = {"index" : prices_collection.find({}).count(), "steam_id" : item["steam_id"], "prices" : [new_price]}
					prices_collection.insert_one(new_item)
					print("{}/{} - {} filled by a new item : {} - {}".format(index, games_collection.find({}).count(), prices_collection.name, cmpt + 1, new_item["steam_id"]))
				cmpt += 1
			else : 
				pass
		else : 
			print("{}/{} - {} don't need to be filled : There is already a price for {} the {} ".format(index, games_collection.find({}).count(), prices_collection.name, prices_collection.find_one({"steam_id" : item["steam_id"]})['steam_id'], datetime.date.today().strftime('%Y-%m-%d')))
	print('Collection filled with ',cmpt,' items.')

def getCollectionItems(collection) :
	"""
		overview : return a collection.
		inputs : 
			- collection : mongoDB collection.
			- items :  list of item (=list of dictionnary). 
	"""
	return list(collection.find({}))

def collectionToCSV(collection) : 
	"""
		overview : collection to .csv file.
		inputs : 
			- collection : mongoDB collection.
	"""
	a = []
	data = collection.find({})
	csv_file_name = str(collection.name).replace('-', '_')+".csv"
	if os.path.exists('./data/'+csv_file_name) :
		deleteFile('./data/'+csv_file_name)
	df = pd.DataFrame(list(data))
	df = df.drop('_id', axis=1)
	try : 
		df.to_csv('./data/'+csv_file_name)
		print("File ./data/"+csv_file_name+" created.")
	except Exception as exc : 
		print("Unble to create th file : ./data/"+csv_file_name) 
		print(exc)

def deleteFile(file) :
	"""
		overview : delete a  file.
		inputs : 
			- file :  file.
	"""
	if os.path.exists(file) :
		os.remove(file)
		print('File ',file,' deleted.')
