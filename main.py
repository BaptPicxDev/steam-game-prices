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

# Constants
DATA_PATH = './data/config.json'


if __name__ == "__main__" :
	start = datetime.datetime.now()
	variables = json.load(open(DATA_PATH)) # open private data to setup the system
	database = openDatabase(variables['mongoDB'])	
	games_collection = getCollection(database, variables['mongoDB']['collections']['games'])
	prices_collection = getCollection(database, variables['mongoDB']['collections']['prices'])
	# games = getIds(variables["chrome_path"], variables["chrome_webdriver_path"], limit=10)
	# fillGamesCollection(games_collection, games)
	# fillPricesCollection(games_collection, prices_collection)
	collectionToCSV(games_collection)
	print("It takes {} seconds to reach the end of this script.".format(datetime.datetime.now() - start))