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
import urllib.request as request

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
	cmpt = 0
	for index_item, item in enumerate(items) : 
		if(games_collection.documentExistsOrNotDemo.find({"steam_id" : item["steam_id"]}).count() > 0 ) :
			pass
		else :
			nb_items = games_collection.count()
			item['index'] = nb_items 
			games_collection.insert_one(item)
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
	items = getCollectionItems(games_collection)
	for index, item in enumerate(items) :
		flag = True
		while(flag) : 		
			try : 
				data = json.load(request.urlopen('http://store.steampowered.com/api/appdetails?appids='+str(item["steam_id"])))[str(item["steam_id"])]
				print("{} - Data loaded.".format(index)) 
				flag = False 
			except Exception as excp :
				print("{} - {}.".format(index, excp))
				time.sleep(20)			 
		if(data['success'] == True) :
			if('price_overview' in data['data'].keys()) : 
				prices = data['data']['price_overview']
				new_price = {
						"datetime" : datetime.datetime.now(), 'is_free' : False, 'currency': prices['currency'], 'initial': prices['initial'], 
						'final': prices['final'], 'discount_percent': prices['discount_percent'], 
						'initial_formatted': prices['initial_formatted'], 'final_formatted': prices['final_formatted']
						}
			else : 
				prices = data['data']
				new_price = {
						"datetime" : datetime.datetime.now(), 'is_free': prices['is_free']
						}
			if(prices_collection.documentExistsOrNotDemo.find({"steam_id" : item["steam_id"]}).count() > 0) :
				prices_collection.update_one({"steam_id" : item["steam_id"]},{'$push': {'prices': new_price}})
				print("Collection filled : {} - {}".format(cmpt + 1, prices_collection.find_one({"steam_id" : item["steam_id"]})))
			else : 
				nb_items = prices_collection.count()
				new_item = {"index" : nb_items, "steam_id" : item["steam_id"], "prices" : [new_price]					}
				prices_collection.insert_one(new_item)
				print("Collection filled : {} - {}".format(cmpt + 1, new_item))
			cmpt += 1
		else : 
			pass
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
