from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import requests
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent 
import lxml
import pandas as pd
global Contact_List 
import time
Contact_List = pd.DataFrame(columns = ['Name', 'Number'])

# Creating fake agent

useragent = UserAgent() 
header = useragent.chrome
url = 'https://www.google.com/search?q='

#Fetching contact page 

def google_query():
	s = requests.Session() 
	query = input('Looking for: ')
	browser = webdriver.Firefox(executable_path = '/home/devesh/Documents/Google/geckodriver.exe')
	#search_request = url + query + '&ie=utf-8&oe=utf-8'
	#google_response = s.get(search_request, headers = {'User-Agent':header}).text
	browser.get('https://www.google.com')
	search = browser.find_element_by_xpath("//input[@title = 'Search']") 
	time.sleep(1)
	search.send_keys(query)
	time.sleep(1.5)
	button = browser.find_element_by_class_name('gNO89b')
	button.click()
	google_response = browser.page_source
	google_response_soup = bs(google_response, 'lxml')
	contact_list_page_url = google_response_soup.find('div', class_='zkIadb')
	return contact_list_page_url.div.a['href'], query

#Scrape contacts on pages 

def scrape_contacts(contact_list_page_url):
	time.sleep(10)
	global Contact_List
	names = []
	numbers = []
	s = requests.Session() 
	contact_list_page_url =  'https://www.google.com' + contact_list_page_url
	print(contact_list_page_url)
	contact_page_response = s.get(contact_list_page_url, headers = {'user-agent':header}).text
	contact_page_response_soup = bs(contact_page_response, 'lxml')
	contact_list = contact_page_response_soup.find('div', class_='rl_full-list')
	contacts = contact_list.div.div.find_all('div', attrs = {'jsname':'GZq3Ke'})

	# Scrpae name and number from a contact 
	for i in contacts:
		try:
			j = i.find('div', class_="cXedhc")
			numbers.append(j.span.find_all('div')[2].text)
			names.append(j.div.text)
		except:
			print(Exception)
			pass
	name_series = pd.Series(names)
	number_series = pd.Series(numbers)
	name_number = pd.DataFrame(list(zip(name_series, number_series)), columns = ['Name','Number'])
	Contact_List = Contact_List.append(name_number, ignore_index=True)
	
	#Contact_List.insert(value=number_series, column='Number')	
	try:
		next_page_url = contact_page_response_soup.find('a', class_='pn', href=True)
		if next_page_url.text == 'Previous':
			next_page_url = contact_page_response_soup.find_all('a', class_='pn', href=True)[1]

		return scrape_contacts(next_page_url['href'])
	except:
		return print('Done')

contact_list_page_url,query = google_query()
scrape_contacts(contact_list_page_url)
print(Contact_List)
Contact_List.to_csv('/home/devesh/Desktop/Scraped_Data/{}.csv'.format(query))

