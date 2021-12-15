import requests
import functools
import os
import random
import re
import sys
import time
import argparse
from selenium.webdriver.chrome import options

from faker import Faker
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from resume_faker import make_resume
from pdf2image import convert_from_path

from webdriver_manager.chrome import ChromeDriverManager
os.environ['WDM_LOG_LEVEL'] = '0'

from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=500)
processes = []

from constants.common import *
from constants.fileNames import *
from constants.classNames import *
from constants.elementIds import *
from constants.email import *
from constants.location import *
from constants.parser import *
from constants.urls import *
from constants.xPaths import *

os.environ["PATH"] += ":/usr/local/bin" # Adds /usr/local/bin to my path which is where my ffmpeg is stored

fake = Faker()

# Add printf: print with flush by default. This is for python 2 support.
# https://stackoverflow.com/questions/230751/how-can-i-flush-the-output-of-the-print-function-unbuffer-python-output#:~:text=Changing%20the%20default%20in%20one%20module%20to%20flush%3DTrue
printf = functools.partial(print, flush=True)

#Option parsing
parser = argparse.ArgumentParser(SCRIPT_DESCRIPTION,epilog=EPILOG)
parser.add_argument('--debug',action='store_true',default=DEBUG_DISABLED,required=False,help=DEBUG_DESCRIPTION,dest='debug')
parser.add_argument('--mailtm',action='store_true',default=MAILTM_DISABLED,required=False,help=MAILTM_DESCRIPTION,dest='mailtm')
args = parser.parse_args()
# END TEST

def initialize_driver(random_city, driver):
    driver.get(CITIES_TO_URLS[random_city])
    driver.implicitly_wait(10)
    time.sleep(15)
    #WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, CREATE_AN_ACCOUNT_BUTTON)))
    driver.find_element_by_xpath(APPLY_NOW_BUTTON_1).click()
    driver.find_element_by_xpath(APPLY_NOW_BUTTON_2).click()
    driver.find_element_by_xpath(CREATE_AN_ACCOUNT_BUTTON).click()
    return driver


def generate_account(driver, fake_identity):
    # make fake account info and fill

    email = fake.free_email()
    password = fake.password()

    for key in XPATHS_2.keys():
        if key in ('email', 'email-retype'):
            info = fake_identity['email']
        elif key in ('pass', 'pass-retype'):
            info = password
        elif key == 'first_name':
            info = fake_identity['first_name']
        elif key == 'last_name':
            info = fake_identity['last_name']
        elif key == 'pn':
            info = fake.phone_number()

        driver.find_element_by_xpath(XPATHS_2.get(key)).send_keys(info)

    time.sleep(random.randint(0, 2))
    select = Select(driver.find_element_by_id(COUNTRY_REGION_CODE_LABEL))
    select.select_by_value(COUNTRY_CODE_US)
    select = Select(driver.find_element_by_id(COUNTRY_REGION_OF_RESIDENCE_LABEL))
    select.select_by_value(COUNTRY_CODE_US)

    driver.find_element_by_xpath(READ_ACCEPT_DATA_PRIVACY_STATEMENT_ANCHORTAG).click()
    time.sleep(1.5)
    driver.find_element_by_xpath(ACCEPT_BUTTON).click()
    time.sleep(2)
    driver.find_element_by_xpath(CREATE_ACCOUNT_BUTTON).click()
    time.sleep(1.5)
    for i in range(120):
        time.sleep(1.5)
        if (args.mailtm == MAILTM_DISABLED):
            mail = requests.get(f'https://api.guerrillamail.com/ajax.php?f=check_email&seq=1&sid_token={fake_identity.get("sid")}').json().get('list')

            if mail:
                passcode = re.findall('(?<=n is ).*?(?=<)', requests.get(f'https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={mail[0].get("mail_id")}&sid_token={fake_identity.get("sid")}').json().get('mail_body'))[0]
                break

        elif (args.mailtm == MAILTM_ENABLED):
            mail = requests.get("https://api.mail.tm/messages?page=1", headers={'Authorization':f'Bearer {fake_identity.get("sid")}'}).json().get('hydra:member')

            if mail:
                passcode = re.findall('(?<=n is ).*', requests.get(f'https://api.mail.tm{mail[0].get("@id")}', headers={'Authorization':f'Bearer {fake_identity.get("sid")}'}).json().get('text'))[0]
                break
    else:
        args.mailtm ^= True
        main() # I should probably find a better way to do this.

    driver.find_element_by_xpath(VERIFY_EMAIL_INPUT).send_keys(passcode)
    driver.find_element_by_xpath(VERIFY_EMAIL_BUTTON).click()

    printf(f"successfully made account for fake email {email}")


def fill_out_application_and_submit(driver, random_city, fake_identity):
    # make resume
    resume_filename = fake_identity['last_name']+'-Resume'
    make_resume(fake_identity['first_name']+' '+fake_identity['last_name'], fake_identity['email'], resume_filename+'.pdf')
    images = convert_from_path(resume_filename+'.pdf')
    images[0].save(resume_filename+'.png', 'PNG')

    # wait for page to load
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, PROFILE_INFORMATION_DROPDOWN)))

    # fill out form parts of app
    driver.find_element_by_xpath(PROFILE_INFORMATION_DROPDOWN).click()
    driver.find_element_by_xpath(CANDIDATE_SPECIFIC_INFORMATION_DROPDOWN).click()

    for key in XPATHS_1.keys():

        if key == 'resume':
            driver.find_element_by_xpath(UPLOAD_A_RESUME_BUTTON).click()
            info = os.getcwd() + '/'+resume_filename+'.png'
        elif key == 'addy':
            info = fake.street_address()
        elif key == 'city':
            info = random_city
        elif key == 'zip':
            info = CITIES_TO_ZIP_CODES[random_city]
        elif key == 'job':
            info = fake.job()
        elif key == 'salary':
            first = random.randrange(15000, 30000, 5000)
            info = f'{format(first, ",")}-{format(random.randrange(first + 5000, 35000, 5000), ",")}'

        driver.find_element_by_xpath(XPATHS_1.get(key)).send_keys(info)

    printf(f"successfully filled out app forms for {random_city}")

    # fill out dropdowns
    select = Select(driver.find_element_by_id(CITIZEN_QUESTION_LABEL))
    select.select_by_visible_text(YES)
    select = Select(driver.find_element_by_id(COUNTRY_OF_ORIGIN_LABEL))
    select.select_by_visible_text(FULL_NAME_US)
    select = Select(driver.find_element_by_id(EIGHTEEN_YEARS_OLD_LABEL))
    select.select_by_visible_text(YES)
    select = Select(driver.find_element_by_id(REQUIRE_SPONSORSHIP_LABEL))
    select.select_by_visible_text(NO)
    select = Select(driver.find_element_by_id(PREVIOUSLY_WORKED_LABEL))
    select.select_by_visible_text(NO)
    select = Select(driver.find_element_by_id(PREVIOUSLY_PARTNERED_LABEL))
    select.select_by_visible_text(NO)
    select = Select(driver.find_element_by_id(RELATIVE_WORKER_LABEL))
    select.select_by_visible_text(NO)
    select = Select(driver.find_element_by_id(ESSENTIAL_FUNCTIONS_LABEL))
    select.select_by_visible_text(YES)
    select = Select(driver.find_element_by_id(PREVIOUSLY_PARTNERED_LABEL))
    select.select_by_visible_text(NO)
    time.sleep(1)
    select = Select(driver.find_element_by_id(GENDER_LABEL))
    gender = random.choice(GENDERS_LIST)
    select.select_by_visible_text(gender)
    driver.find_element_by_xpath(MIXER_QUESTION_1_LABEL).click()
    driver.find_element_by_xpath(MIXER_QUESTION_2_LABEL).click()

    els = driver.find_elements_by_xpath(LONG_PERIODS_QUESTION_LABEL)
    [el.click() for el in els]

    time.sleep(5)
    driver.find_element_by_xpath(APPLY_BUTTON).click()
    printf(f"successfully submitted application")

    # take out the trash
    os.remove(resume_filename+'.pdf')
    os.remove(resume_filename+'.png')

def random_email(name=None):
    if name is None:
        name = fake.name()

    mailGens = [lambda fn, ln, *names: fn + ln,
                lambda fn, ln, *names: fn + "_" + ln,
                lambda fn, ln, *names: fn[0] + "_" + ln,
                lambda fn, ln, *names: fn + ln + str(int(1 / random.random() ** 3)),
                lambda fn, ln, *names: fn + "_" + ln + str(int(1 / random.random() ** 3)),
                lambda fn, ln, *names: fn[0] + "_" + ln + str(int(1 / random.random() ** 3)), ]

    return random.choices(mailGens, MAIL_GENERATION_WEIGHTS)[0](*name.split(" ")).lower() + "@" + \
           requests.get('https://api.mail.tm/domains').json().get('hydra:member')[0].get('domain')

def run():
    try:
        options = Options()
        if (args.debug == DEBUG_DISABLED):
            options.add_argument(f"user-agent={USER_AGENT}")
            options.add_argument('disable-blink-features=AutomationControlled')
            options.headless = True
            driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
            driver.set_window_size(1440, 900)
        elif (args.debug == DEBUG_ENABLED):
            driver = webdriver.Chrome(ChromeDriverManager().install())
    except:
        print(f"FAILED TO START DRIVER: {e}")
        # No pass, this error is fatal


    while True:
        random_city = random.choice(list(CITIES_TO_URLS.keys()))
        try:
            initialize_driver(random_city, driver)
        except Exception as e:
            print(f"FAILED TO INITIALIZE DRIVER: {e}")
            pass

        time.sleep(2)

        fake_first_name = fake.first_name()
        fake_last_name = fake.last_name()
        if (args.mailtm == MAILTM_DISABLED):
            printf(f"USING GUERRILLA TO CREATE EMAIL")
            response = requests.get('https://api.guerrillamail.com/ajax.php?f=get_email_address').json()

            fake_email = response.get('email_addr')
            mail_sid = response.get('sid_token')
            printf(f"EMAIL CREATED")

        elif (args.mailtm == MAILTM_ENABLED):
            printf(f"USING MAILTM TO CREATE EMAIL")
            fake_email = requests.post('https://api.mail.tm/accounts', data='{"address":"'+random_email(fake_first_name+' '+fake_last_name)+'","password":" "}', headers={'Content-Type': 'application/json'}).json().get('address')
            mail_sid = requests.post('https://api.mail.tm/token', data='{"address":"'+fake_email+'","password":" "}', headers={'Content-Type': 'application/json'}).json().get('token')
            printf(f"EMAIL CREATED")

        fake_identity = {
            'first_name': fake_first_name,
            'last_name': fake_last_name,
            'email': fake_email,
            'sid' : mail_sid
        }

        try:
            generate_account(driver, fake_identity)
        except Exception as e:
            printf(f"FAILED TO CREATE ACCOUNT: {e}")
            pass

        try:
            fill_out_application_and_submit(driver, random_city, fake_identity)
        except Exception as e:
            printf(f"FAILED TO FILL OUT APPLICATION AND SUBMIT: {e}")
            pass
            driver.close()
            continue

        driver.close()
        time.sleep(5)


def main():
    global processes
    global executor

    parallel = int(input("How many parallel windows?: "))

    for i in range(parallel):
        processes.append(executor.submit(run))

if __name__ == '__main__':
    main()
    sys.exit()
