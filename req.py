from selenium import webdriver
from selenium.webdriver.support.ui import Select
import requests
import random
import time
import os
import functools
from faker import Faker
fake = Faker()
chromedriver_location = "./chromedriver"
print = functools.partial(print, flush=True)

urls = ['https://jobs.kellogg.com/job/Lancaster-Permanent-Production-Associate-Lancaster-PA-17601/817684800/#',
        'https://jobs.kellogg.com/job/Omaha-Permanent-Production-Associate-Omaha-NE-68103/817685900/z',
        'https://jobs.kellogg.com/job/Battle-Creek-Permanent-Production-Associate-Battle-Creek-MI-49014/817685300/',
        'https://jobs.kellogg.com/job/Memphis-Permanent-Production-Associate-Memphis-TN-38114/817685700/'
        ]


data2 = {
    'resume': '//*[@id="49:_file"]',
    'addy': '//*[@id="69:_txtFld"]',
    'city': '//*[@id="73:_txtFld"]',
    'zip': '//*[@id="81:_txtFld"]',
    'job': '//*[@id="101:_txtFld"]',
    'salary': '//*[@id="172:_txtFld"]',
    'country': '//*[@id="195:_select"]'
}
data = {
    'email': '//*[@id="fbclc_userName"]',
    'email-retype': '//*[@id="fbclc_emailConf"]',
    'pass': '//*[@id="fbclc_pwd"]',
    'pass-retype': '//*[@id="fbclc_pwdConf"]',
    'first_name': '//*[@id="fbclc_fName"]',
    'last_name': '//*[@id="fbclc_lName"]',
    'pn': '//*[@id="fbclc_phoneNumber"]',

}


cities = {'Lancaster':	'Pennsylvania',
          'Omaha':	'Nebraska',
          'Battle Creek':	'Michigan',
          'Memphis':	'Tennessee',
          }

zip_codes = {
    'Lancaster':	['17573', '17601', '17602', '17605', '17606', '17699'],
    'Omaha':	['68104', '68105', '68106', '68124', '68127', '68134'],
    'Battle Creek':	['49014', '49015', '49016', '49017', '49018', '49037'],
    'Memphis':	['38116', '38118', '38122', '38127', '38134', '38103'],
}

def start_driver(rand_num):
    try:
        driver = webdriver.Chrome(chromedriver_location)
        driver.get(urls[rand_num])
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
    except Exception as e:
        print(f"failed to start driver: {str(e)}")
        return

def generate_account(driver, rand_num):
    # make fake account info and fill
    email = fake.email()
    password = fake.password()
    for key in data.keys():
        match key:
            case 'email' | 'email-retype':
                info = email
            case 'pass' | 'pass-retype':
                info = password
            case 'first_name' | 'last_name':
                info = fake.first_name()
            case 'pn':
                info = fake.phone_number()

        try:
            driver.find_element_by_xpath(data.get(key)).send_keys(info)
        except Exception as e:
            print(f"failed to fill account info: {str(e)}")
        
    try:
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
    except Exception as e:
        print(f"failed to create account: {str(e)}")
        return

    print(f"successfully made account for fake email {email}")

def fill_out_application_and_submit(driver, rand_num):
    driver.implicitly_wait(10)
    city = list(cities.keys())[rand_num]
    
    # fill out form parts of app
    try:
        driver.find_element_by_xpath('//*[@id="109:topBar"]').click()
        driver.find_element_by_xpath('//*[@id="260:topBar"]').click()

        zip_num = random.randint(0, 4)

        for key in data2.keys():

            match key:
                case 'resume':
                    driver.find_element_by_xpath('//*[@id="48:_attach"]/div[6]').click()
                    info = os.getcwd()+"/src/resume.png"
                case 'addy':
                    info = fake.street_address()
                case 'city':
                    info = city
                case 'zip':
                    zipp = zip_codes[city]
                    info = zipp[zip_num]
                case 'job':
                    info = fake.job()
                case 'salary':
                    info = random.randint(15, 35)

            driver.find_element_by_xpath(data2.get(key)).send_keys(info)
    
    except Exception as e:
        print(f"failed to fill out app forms: {str(e)}")
        return

    print(f"successfully filled out app forms for {city}")

    # fill out dropdowns
    try:
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
    except Exception as e:
        print(f"failed to fill out app dropdowns and submit: {str(e)}")
        return

    print(f"successfully submitted application")

def main():
    rand_num = random.randint(0, 3)
    i = 1
    while (i < 10000):
        driver = start_driver(rand_num)
        if not driver:
            pass

        time.sleep(2)
        generate_account(driver, rand_num)

        fill_out_application_and_submit(driver, rand_num)

        driver.close()
        time.sleep(5)

if __name__ == '__main__':
    main()
    sys.exit()