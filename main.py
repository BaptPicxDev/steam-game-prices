#############################################
# author : Baptiste PICARD 		 			#
# date : 25/07/2020				 			#
# 								 			#
# overview : Retrieving steam game prices.  #
#											#
#############################################

## Imports
import json # Reading .json files
import datetime # Time computation

# Modules 
from access import * 
from webdrivers import * 
from utils import * 

# Constants
DATA_PATH = './data/config.json'

# Set-Up
ERASE = False
TOJSON = False


if __name__ == "__main__" :
	print("The script is starting.")
	start = datetime.datetime.now()
	variables = json.load(open(DATA_PATH)) # open private data to setup the system
	database = openDatabase(variables['mongoDB'])	
	games_collection = getCollection(database, variables['mongoDB']['collections']['games'])
	prices_collection = getCollection(database, variables['mongoDB']['collections']['prices'])
	# games = getIds(variables["chrome_path"], variables["chrome_webdriver_path"], limit=1)
	if(ERASE) : 
		eraseCollection(games_collection)
		eraseCollection(prices_collection)
	# fillGamesCollection(games_collection, games)
	# fillPricesCollection(games_collection, prices_collection)
	if(TOJSON) : 
		collectionToCSV(games_collection)
	# getCollectionInfo(games_collection)
	# getCollectionInfo(prices_collection)
	# getTypePropotion(games_collection)
	getPriceEvolution(prices_collection, 1220900)
	print("It takes {} seconds to reach the end of this script.".format(datetime.datetime.now() - start))