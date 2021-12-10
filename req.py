from selenium import webdriver
from selenium.webdriver.support.ui import Select
import requests
import random
import json
import time
import os
import functools
from faker import Faker
fake = Faker()
chromedriver_location = "/usr/local/bin/chromedriver"
print = functools.partial(print, flush=True)

#worksite or jobsite
class Site:
    def __init__(self,id,city,state,zips,url) -> None:
        self.id = id
        self.city = city
        self.state = state
        self.zips = zips
        self.url = url
    
    def get_city(self):
        return self.city

    def get_id(self):
        return self.id

    def get_state(self):
        return self.state

    def get_url(self):
        return self.url

    def get_random_zip(self):
        return self.zips[random.randint(0,len(self.zips)-1)]

    def get_zips(self):
        return self.zips

class PageTextField:
    def __init__(self,fieldDict,name) -> None:
        self.dict = fieldDict
        self.name = name
    def get_dict(self):
        return self.dict
    def get_name(self):
        return self.name
    def get_id(self,key):
        return self.dict[key][0]
    def get_type(self,key):
        return self.dict[key][1]
    


# Drives application process using worksite and textfield information
class Application:
    def __init__(self,sites,fields) -> None:
        self.sites = sites
        self.fields = fields
        self.instancesite = -128

    def find_fields(self,name):
        for field in self.fields:
            if field.get_name() == name:
                return field
            else:
                continue
        return 0

    def find_site(self,id):
        for site in self.sites:
            if site.get_id() == id:
                return site
            else:
                continue
        return 0

    def start_driver(self,rand_num):
        driver = webdriver.Chrome(chromedriver_location)
        self.instancesite = self.find_site(rand_num)
        driver.get(self.instancesite.get_url())
        # driver.manage().timeouts().pageLoadTimeout(5, SECONDS)
        # time.sleep(10)
        driver.implicitly_wait(10)
        time.sleep(2)
        driver.find_element_by_xpath(
            '//*[@id="content"]/div/div[2]/div/div[1]/div[1]/div/div/button').click()
        driver.find_element_by_xpath(
            '//*[@id="applyOption-top-manual"]').click()
        driver.find_element_by_xpath(
            '//*[@id="page_content"]/div[2]/div/div/div[2]/div/div/div[2]/a').click()
        return driver

    def generate_account(self,driver):
        # make fake account info and fill

        email = fake.email()
        password = fake.password()
        data = self.find_fields("data")
        for key in data.get_dict():
            match data.get_type(key):
                case "email":
                    info = email
                case "password":
                    info = password
                case "firstname" | "lastname":
                    info = fake.first_name()
                case "phonenumber":
                    info = fake.phone_number()

            driver.find_element_by_xpath(data.get_id(key)).send_keys(info)
            
        time.sleep(random.randint(0, 2))
        select = Select(driver.find_element_by_id('fbclc_ituCode'))
        select.select_by_value('US')
        select = Select(driver.find_element_by_id('fbclc_country'))
        select.select_by_value('US')

        driver.find_element_by_xpath('//*[@id="dataPrivacyId"]').click()
        time.sleep(1.5)
        driver.find_element_by_xpath('//*[@id="dlgButton_20:"]').click()
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="fbclc_createAccountButton"]').click()

        time.sleep(1.5)

        print(f"successfully made account for fake email {email}")

    def fill_out_application_and_submit(self,driver):

        driver.implicitly_wait(10)
        city = self.instancesite.get_city()
        
        # fill out form parts of app
        driver.find_element_by_xpath('//*[@id="109:topBar"]').click()
        driver.find_element_by_xpath('//*[@id="260:topBar"]').click()

        data2 = self.find_fields("data2")
        for key in data2.get_dict():

            match data2.get_type(key):
                case "resume":
                    driver.find_element_by_xpath('//*[@id="48:_attach"]/div[6]').click()
                    info = os.getcwd()+"/src/resume.png"
                case "address":
                    info = fake.street_address()
                case "city":
                    info = city
                case "zipcode":
                    info = self.instancesite.get_random_zip()
                case "job":
                    info = fake.job()
                case "salary":
                    info = random.randint(15, 35)

            driver.find_element_by_xpath(data2.get_id(key)).send_keys(info)

        print(f"successfully filled out app forms for {city}")

        # fill out dropdowns
        select = Select(driver.find_element_by_id('154:_select'))
        select.select_by_visible_text('Yes')
        select = Select(driver.find_element_by_id('195:_select'))
        select.select_by_visible_text('United States')

        select = Select(driver.find_element_by_id('211:_select'))
        select.select_by_visible_text('Yes')
        select = Select(driver.find_element_by_id('215:_select'))
        select.select_by_visible_text('No')
        select = Select(driver.find_element_by_id('219:_select'))
        select.select_by_visible_text('No')
        select = Select(driver.find_element_by_id('223:_select'))
        select.select_by_visible_text('No')
        select = Select(driver.find_element_by_id('227:_select'))
        select.select_by_visible_text('No')
        select = Select(driver.find_element_by_id('231:_select'))
        select.select_by_visible_text('Yes')
        select = Select(driver.find_element_by_id('223:_select'))
        select.select_by_visible_text('No')

        time.sleep(1)

        select = Select(driver.find_element_by_id('235:_select'))
        gender = random.choice(['Male', 'Female', 'Other'])
        select.select_by_visible_text(gender)

        driver.find_element_by_xpath('//label[text()="350 LBS"]').click()
        driver.find_element_by_xpath('//label[text()="800 LBS"]').click()
        els = driver.find_elements_by_xpath('//label[text()="Yes"]')
        for el in els:
            el.click()

        time.sleep(5)
        driver.find_element_by_xpath('//*[@id="261:_submitBtn"]').click()
        print(f"successfully submitted application")

def loadSites(fname):
    sites = []
    try:
        with open(fname) as f:
            data = json.load(f)
            for jsite in data["sites"]:
                id = jsite["id"]
                city = jsite["city"]
                state = jsite["state"]
                url = jsite["website"]
                zipcodes = jsite["zipcodes"]
                site = Site(id,city,state,zipcodes,url)
                sites.append(site)
        return sites
                
    except Exception as e:
        print(f"Failed to grab sites from file: {str(e)}")
        return sites

def loadFields(fname):
    fieldlist = []
    try:
        with open(fname) as f:
            data = json.load(f)
            for lis in data:
                textfields = PageTextField(data[lis][0],lis)
                fieldlist.append(textfields)
        return fieldlist
    except Exception as e:
        print(f"Failed to grab fields from file: {str(e)}")

def main():
    sites = loadSites("sites.json")
    fields = loadFields("fields.json")
    
    for _ in range(10000):
        app = Application(sites,fields)
        randSiteIndex = random.randint(0,len(sites)-1)


        try:
            driver = app.start_driver(randSiteIndex)
        except Exception as e:
            print(f"failed to start driver: {str(e)}")
            pass

        time.sleep(2)

        try:
            app.generate_account(driver)
        except Exception as e:
            print(f"failed to create account: {str(e)}")
            pass

        try:
            app.fill_out_application_and_submit(driver)
        except Exception as e:
            print(f"failed to fill out app and submit: {str(e)}")
            pass

        driver.close()
        time.sleep(5)
    

if __name__ == '__main__':
    main()
    exit(0)