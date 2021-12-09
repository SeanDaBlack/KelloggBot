from selenium import webdriver
from selenium.webdriver.support.ui import Select
import requests
import random
import time
import os
from faker import Faker
fake = Faker()
chromedriver_location = "./chromedriver"

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


i = 1



while(i < 10000):
    
    j = random.randint(0, 4)
    try:
        driver = webdriver.Chrome(chromedriver_location)
        driver.get(urls[j])
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
    except Exception as e:
        print("failed 1: " + str(e))
        pass
    time.sleep(2)
    # print(random.choice(list(cities.items()))[0])
    email = fake.email()
    password = fake.password()
    for key in data.keys():

        if key == 'email':
            info = email
        if key == 'email-retype':
            info = email
        if key == 'pass':
            info = password
        if key == 'pass-retype':
            info = password
        if key == 'first_name':
            info = fake.first_name()
        if key == 'last_name':
            info = fake.first_name()
        if key == 'pn':
            info = fake.phone_number()

        try:
            driver.find_element_by_xpath(data.get(key)).send_keys(info)
        except:
            print("failed 2")


        # '//*[@id="dataPrivacyId"]'
        # '//*[@id="dlgButton_20:"]'

        # '//*[@id="fbclc_createAccountButton"]'

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
        driver.find_element_by_xpath(
            '//*[@id="fbclc_createAccountButton"]').click()

        print(i)
        time.sleep(1.5)
        i += 1
    except:
        pass

    # time.sleep(1.5)
    driver.implicitly_wait(10)
    # //*[@id="48:_attachLabel"] #send pic//*[@id="109:topBar"]
    driver.find_element_by_xpath('//*[@id="109:topBar"]').click()
    driver.find_element_by_xpath('//*[@id="260:topBar"]').click()

    if j == 0:
        city = 'Lancaster'
    elif j == 1:
        city = 'Omaha'
    elif j == 2:
        city = 'Battle Creek'
    elif j == 3:
        city = 'Memphis'

    num = random.randint(0, 4)

    for key in data2.keys():

        if key == 'resume':
            driver.find_element_by_xpath(
                '//*[@id="48:_attach"]/div[6]').click()

            info = os.getcwd()+"/src/resume.png"
        if key == 'addy':
            info = fake.street_address()
        if key == 'city':
            info = city
            print(city)
        if key == 'zip':
            zipp = zip_codes[city]
            info = zipp[num]
        if key == 'job':
            info = fake.job()
        # if key == 'addy':
        #     info = fake.first_name()
        if key == 'salary':
            info = random.randint(15, 35)
        # if key == 'country':
        #     info = fake.phone_number()
        # if key == 'salary':
        #     info = fake.phone_number()

        try:
            driver.find_element_by_xpath(data2.get(key)).send_keys(info)
        except Exception as e:
            print("failed 2: " + str(e))
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
        gender = ['Male', 'Female', 'Other']
        select = Select(driver.find_element_by_id('235:_select'))
        g = random.choice(gender)
        print(g)
        select.select_by_visible_text(g)

        # label[text()='Patient's Name']
        # //*[@id="130:_radiolabel"]
        # //*[@id="130:_anchor"]
        # driver.find_element_by_class_name("")

        driver.find_element_by_xpath('//label[text()="350 LBS"]').click()
        driver.find_element_by_xpath('//label[text()="800 LBS"]').click()
        els = driver.find_elements_by_xpath('//label[text()="Yes"]')
        for el in els:
            el.click()
        # driver.find_element_by_xpath('//label[text()="Yes"]').click()
        # driver.find_element_by_xpath('//label[text()="Yes"]').click()

        # driver.find_element_by_xpath('//*[@id="121:_radio"]').click()
        # driver.find_element_by_xpath('//*[@id="128:_radio"]').click()
        # driver.find_element_by_xpath('//*[@id="138:_radio"]').click()
        # driver.find_element_by_xpath('//*[@id="143:_radio"]').click()

        time.sleep(5)
        driver.find_element_by_xpath('//*[@id="261:_submitBtn"]').click()
        # time.sleep(10)
    except:
        pass

    driver.close()
    time.sleep(5)
