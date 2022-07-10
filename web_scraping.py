# import requests, urlopen
from urllib.request import Request, urlopen
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By #added
from selenium.webdriver.support.ui import WebDriverWait #added
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC #added
from bs4 import BeautifulSoup
import re
from geopy.geocoders import Nominatim
from selenium.webdriver.chrome.options import Options
import time
import csv
import os

def get_soup(url):
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
	req = Request(url, headers=headers)
	webpage = urlopen(req).read()
	soup = BeautifulSoup(webpage, 'html.parser')

	return soup

if __name__ == '__main__':

	base = "https://blinkit.com"
	base_url = "https://blinkit.com/cn/vegetables-fruits/vegetables/cid/1487/1489"

	# Iterate all the base categories and their subcategories urls
	soup = get_soup(base)
	database = []
	categories = []
	sub_categories = []

	# print(soup.body)
	# exit()
	geolocator = Nominatim(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")
	location = geolocator.geocode("560040")
	print(location.address)
	print(location.latitude)
	print(location.longitude)
	# service = Service(executable_path=ChromeDriverManager().install())
	service = Service(executable_path="/Users/kbondugula/Documents/chromedriver")
	params = {
		"latitude": location.latitude,
		"longitude": location.longitude,
		"accuracy": 100
	}

	# chromrdriver = "/Users/kbondugula/Documents/chromedriver"
	# os.environ["webdriver.chrome.driver"] = chromrdriver
	# driver = webdriver.Chrome(chromrdriver)

	# chrome_options = Options()
	options = Options()
	options.add_argument('start-maximized')
	options.add_argument('disable-infobars')
	options.add_argument('--disable-extensions')
	# chrome_options.add_experimental_option('prefs', {
		# 'geolocation': True
	# })
	driver = webdriver.Chrome(service = service)
	driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)
	driver.get(base)
	loc_input = driver.find_element(By.XPATH, "//button[@class='btn location-box mask-button']")
	loc_input.click()
	time.sleep(10)
	html = driver.page_source
	soup = BeautifulSoup(html, 'html.parser')
	# driver.close()
	# exit()

	for i in soup.findAll("li", class_= re.compile("FooterLinks__ListItem-")):
		if i.text in categories:
			continue

		new_url = base + str(i.a.get("href"))
		# print(new_url)
		category = i.text
		categories.append(category)
		# driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)
		driver.get(new_url)
		# loc_input = driver.find_element(By.XPATH, "//button[@class='btn location-box mask-button']")
		# loc_input.click()
		time.sleep(3)
		new_soup = BeautifulSoup(driver.page_source, 'html.parser')

		print('\n ######################  Start of Category : ' + str(category) + ' ########################\n')

		# # Iterate through the subcategories to find the items
		for j in new_soup.findAll("li", class_=re.compile("category-list__item no-link no-hover no-child")):
			sub_category = j.text
			new_url_1 = base + j.a.get('href')
			driver.get(new_url_1)
			time.sleep(3)

			SCROLL_PAUSE_TIME = 0.5
			last_height = driver.execute_script("return document.body.scrollHeight")
			while True:
			    # Scroll down to bottom
			    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

			    # Wait to load page
			    time.sleep(SCROLL_PAUSE_TIME)

			    # Calculate new scroll height and compare with last scroll height
			    new_height = driver.execute_script("return document.body.scrollHeight")
			    if new_height == last_height:
			        break
			    last_height = new_height
			time.sleep(4)
			new_soup_1 = BeautifulSoup(driver.page_source, 'html.parser')

			print('\n ###################### Start of Sub Category ' + str(sub_category) + " #######################\n")

			n_products = 0
			# Iterate through the items in this sub-category
			for j_1 in new_soup_1.findAll("a", class_=re.compile("product__wrapper")):
				new_url_2 = base + j_1.get('href')
				# print(new_url_2)
				# exit()
				driver.get(new_url_2)
				time.sleep(5)
				# exit()
				new_soup_2 = BeautifulSoup(driver.page_source, 'html.parser')
				product_name = new_soup_2.body.find("span", class_=re.compile("ProductName")).text

				row = []
				brand = 'NA'
				weight = 'NA'
				mrp = 'NA'
				price = 'NA'
				shelf_life = 'NA'
				country_of_origin = 'NA'
				exp_date = 'NA'
				unit = 'NA'
				# Iterate through the item details in the list
				for j_2 in new_soup_2.body.findAll("div", class_=re.compile("ProductAttributes-")):
					if j_2.find('p').text == 'Unit':
						unit = j_2.div.text
					elif j_2.find('p').text == 'Shelf Life':
						shelf_life = j_2.div.text
					elif j_2.find('p').text == 'Country of Origin':
						country_of_origin = j_2.div.text
					elif j_2.find('p').text == 'Expiry Date':
						exp_date = j_2.div.text

				brand = new_soup_2.body.find("div", class_=re.compile("BrandContainer"))
				if brand is not None:
					brand = brand.text
				else:
					brand = 'NA'

				weight = unit
				prices = (new_soup_2.body.find("div", class_=re.compile("Price")).text).split(" ")

				if len(prices) == 1:
					price = mrp = (prices[0])[1:]
				else:
					price = (prices[0])[1:]
					mrp = (prices[1])[1:]

				if price == 'ut':
					price = 'Out of Stock'
					mrp = 'Out of Stock'

				print('Category : ', category)
				print('Sub-category : ', sub_category)
				print('Brand : ', brand)
				print('ProductName : ', product_name)
				print('Weight : ', weight)
				print('MRP : ', mrp)
				print('Price : ', price)
				print('Shelf Life : ', shelf_life)
				print('Country of Origin : ', country_of_origin)
				print('Expiry Date : ', exp_date)
				print('Unit : ', unit)

				n_products = n_products + 1
					# print(j_2.div.text)
				row_ = [category, sub_category, brand, product_name, weight, mrp, price, shelf_life, country_of_origin, exp_date, unit]

				with open('product_data5.csv', 'a') as f:
					# create the csv writer
					writer = csv.writer(f)
					writer.writerow(row_)

				print('Product data saved ..... ')
				print('\n')


			print('N Products in ' + str(category) + ' with ' + str(sub_category) + ' is : ', n_products)
			print('\n ###################### End of Sub Category ' + str(sub_category) + " #######################\n")
		print('\n ######################  End of Category : ' + str(category) + ' ########################\n')
