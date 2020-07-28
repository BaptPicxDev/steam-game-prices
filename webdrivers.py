#############################################
# author : Baptiste PICARD 		 			#
# date : 26/07/2020				 			#
# 								 			#
# overview : Retrieving steam game prices.  #
#											#
#############################################

# Imports
import time
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options # Webdriver options

def getIds(chrome_path, chrome_webdriver_path, limit=1) :
	game_data = []
	cmpt_item = 0
	options = Options() # Set up the option
	options.binary_location = chrome_path # Give the chrome path 
	driver = webdriver.Chrome(chrome_options=options, executable_path=chrome_webdriver_path) # Creating the Web driver
	driver.get("https://steamdb.info/apps/") 
	time.sleep(5)
	n_pages = int(driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[3]/div/h1[1]").text.split('/')[-1])
	for page in range(1, n_pages+1) :
		driver.get("https://steamdb.info/apps/page"+str(page)) 
		games = driver.find_elements_by_class_name("app")
		for index, game in enumerate(games) : 
			game_text = game.text.split('\n')
			if(len(game_text)==4) :
				game_id = game_text[0] 
				game_name = game_text[1] 
				game_type = game_text[2]
				data = {"steam_id" : game_id, "name" : game_name, "type" : game_type}
				if(data not in game_data) :
					game_data.append(data)
				print('Page {} Item {} | {}.'.format(page, index, data))
				cmpt_item += 1
			else : 
				pass
		if(limit!="max" and page>=limit) :
			break
	driver.close()
	return game_data