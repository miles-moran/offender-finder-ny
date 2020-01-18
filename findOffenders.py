
from lxml import html
import requests
import time
from pprint import pprint
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Sex Offenders").worksheet('New York')

def addOffender(offender):
    formatted = ''
    for i in range(0, len(offender['addresses'])):
        address = offender['addresses'][i]
        formatted += address
        if i != len(offender['addresses'])-1:
            formatted += ' && '
    sheet.append_row([offender['first'] + offender['last'], offender['href'], formatted])

def scrape():
    cont = True
    chromedriver_location = '/chromedriver.exe'
    browser = webdriver.Chrome(chromedriver_location)
    URL = 'https://www.criminaljustice.ny.gov/SomsSUBDirectory/search_index.jsp'
    browser.get(URL)
    while cont is True:
        print(' ')
        print('Hit ENTER -> CTRL-C to Quit')
        input('Complete CAPTCHA -> Press Enter to Continue:')
        offenderIds = []
        links = browser.find_elements_by_xpath("//td[@align='left']//a")
        hrefs = []
        for link in links:
            href = link.get_attribute("href")
            hrefs.append(href)
        for href in hrefs:
            browser.get(href)
            time.sleep(.5)
            domiciled = browser.find_element_by_xpath('//ul[@class="somsTopTable nameyTable label-value"]')
            offenderId = domiciled.find_element_by_xpath('//li[1]//span[@class="value"]')
            lastName = domiciled.find_element_by_xpath('//li[2]//span[@class="value"]')
            firstName = domiciled.find_element_by_xpath('//li[3]//span[@class="value"]')
            addresses = browser.find_elements_by_xpath('//ul[@class="address label-value"]//li[3]//span[@class="value"]')
            residences = []
            for address in addresses:
                residences.append(address.text.replace('\n', '-'))
            offender = {
                'id': offenderId.text,
                'last': lastName.text,
                'first': firstName.text,
                'addresses': residences,
                'href': href
            }
            if offender['id'] in offenderIds:
                continue
            offenderIds.append(offender['id'])
            pprint(offender)
            addOffender(offender)
        print('\a')
        print('End of List Reached. Hit ENTER -> CTRL-C to Quit or Enter Another ZIP')
        print(' ')
        browser.get(URL)
scrape()