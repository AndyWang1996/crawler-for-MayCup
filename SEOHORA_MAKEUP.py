import requests
import time
import random
import json
from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

# curPath = os.getcwd()
# tempPath = 'Product'
# targetPath = curPath + os.path.sep + tempPath
# if not os.path.exists(targetPath):
# 	os.makedirs(targetPath)

# driver path
path = '/Users/francisfeng/Desktop/MAKEUP/chromedriver'

# headless mode
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')

flag = True
fail_page = 0
all_items = 0
success_count = 0
fail_count = 0

def get_page_num(brower):
	bs = BeautifulSoup(brower.page_source, 'html.parser').find('div', {'class', 'module-pagination-page'})
	all_num = bs.find_all('a')
	page_num = all_num[len(all_num)-1].string

	return page_num

def get_url_list(brower):
	url_list = []
	bs = BeautifulSoup(brower.page_source, 'html.parser')
	product = bs.find('div', {'class': 'cate_prod_cont'})
	for product_list in product.find_all('li'):
		product_url = product_list.find('div', {'class': 'p_productCN'}).find('a')['href']
		# print(product_url)
		url_list.append(product_url)

	return url_list

def get_product_details(new_brower):
	bs = BeautifulSoup(new_brower.page_source, 'html.parser')
	content = bs.find('div', {'class', 'ProductMainMixture'})
	if content.find('p', {'class': 'three'}).string != None:
		product_price = "¥" + content.find('p', {'class': 'three'}).string
	else:
		product_price = "price_info_lost"
	image = bs.find('div', {'class', 'productImageChange'}).find('div', {'class', 'imgOrVideo'}).find('img')['src']
	product_name = bs.find('div', {'class', 'productImageChange'}).find('div', {'class', 'imgOrVideo'}).find('img')['title']

	return product_price, product_name, image

def get_data(i, all_page_num, brower, file_number):
	global all_items
	global success_count
	global fail_count
	
	current_success = 0
	current_fail = 0
	current_all = 0

	fail_page = i

	try:
		url_list = get_url_list(brower)
		
		for url in url_list:
			all_items += 1
			current_all += 1
			new_brower = webdriver.Chrome(executable_path = path, options = chrome_options)
			new_brower.get(url)
			try:
				success_count += 1
				current_success += 1
				
				time.sleep(1)
				
				price, name, image = get_product_details(new_brower)

				if '/' in name:
					name = name.replace('/', '_')

				print(name)

				product_url = url
				product_name = name
				product_img = image
				product_price = price

				# save product as JSON
				data = {"name": product_name, "price": product_price, "imagelink": product_img, "productlink": product_url}
				json_builder(data, file_number)

				new_brower.quit()

			except:
				fail_count += 1
				current_fail += 1
				print("!!!Error, cannot get this item!!!")
				new_brower.quit()
		
		print()
		print("=================================")
		print("Page " + str(i))
		print()
		print("All Item Number: " + str(all_items))
		print("All Success Item Number: " + str(success_count))
		print("All Fail Item Number: " + str(fail_count))
		print()
		print("Current Item Number: " + str(current_all))
		print("Current Success Item Number: " + str(current_success))
		print("Current Fail Item Number: " + str(current_fail))
		print("=================================")
		print()

		if i != all_page_num:
			next = brower.find_element_by_xpath("//a[contains(text(),'下一页 >')]")
			brower.execute_script("arguments[0].click();", next)
			time.sleep(1)

	except:
		print('Fail page is ' + str(fail_page))
		print('Error, restart!!!')
		
		success_count = success_count - current_success
		fail_count = fail_count - current_fail
		all_items = all_items - current_all
		
		brower.quit()
		all_pages(fail_page, file_number)

def json_builder(data, file_number):
	file_name = "Makeup_" + str(file_number)
	with open(file_name, 'a', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False)

def all_pages(page_number, file_number):
	URL = 'https://www.sephora.cn/function/?cat=&fun=&attr=%E5%8A%9F%E6%95%88&hasInventory=1&sortField=1&sortMode=desc&currentPage=' \
			+ str(page_number) + '&filters='
	brower = webdriver.Chrome(executable_path = path, options = chrome_options)
	brower.get(URL)
	
	num = get_page_num(brower)
	
	for n in range(page_number-1, int(num)):
		get_data(n + 1, num, brower, file_number)

	brower.quit()


if __name__ == '__main__':
	# the program will go until the world ends
	i = 0
	while flag:
		i = i % 3
		all_pages(1, i)
		i += 1
		time.sleep(20)