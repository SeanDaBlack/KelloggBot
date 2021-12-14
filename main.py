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

from webdriver_manager.chrome import ChromeDriverManager
os.environ['WDM_LOG_LEVEL'] = '0'

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

def start_driver(random_city):
    options = webdriver.ChromeOptions()
    if (args.debug == DEBUG_DISABLED):
        options.add_argument(f"user-agent={USER_AGENT}")
        options.add_argument('disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--incognito')
        options.headless = True
        driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        driver.set_window_size(1440, 900)
    elif (args.debug == DEBUG_ENABLED):
        driver = webdriver.Chrome(ChromeDriverManager().install())
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
            info = fake_identity['phone']

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
    make_resume(fake_identity['first_name']+' '+fake_identity['last_name'], fake_identity['email'], fake_identity['phone'], resume_filename)

    # wait for page to load
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, PROFILE_INFORMATION_DROPDOWN)))

    # fill out form parts of app
    driver.find_element_by_xpath(PROFILE_INFORMATION_DROPDOWN).click()
    driver.find_element_by_xpath(CANDIDATE_SPECIFIC_INFORMATION_DROPDOWN).click()

    for key in XPATHS_1.keys():
        if key == 'resume':
            driver.find_element_by_xpath(UPLOAD_A_RESUME_BUTTON).click()
            info = os.getcwd() + '/'+resume_filename+'.pdf'
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
        if key == 'resume': time.sleep(8) # wait for "loading" animation

    printf(f"successfully filled out app forms for {random_city}")

    # fill out dropdowns
    select = Select(driver.find_element_by_name(CITIZEN_QUESTION_LABEL))
    select.select_by_visible_text(YES)
    select = Select(driver.find_element_by_name(COUNTRY_OF_ORIGIN_LABEL))
    select.select_by_visible_text(FULL_NAME_US)
    select = Select(driver.find_element_by_name(EIGHTEEN_YEARS_OLD_LABEL))
    select.select_by_visible_text(YES)
    select = Select(driver.find_element_by_name(REQUIRE_SPONSORSHIP_LABEL))
    select.select_by_visible_text(NO)
    select = Select(driver.find_element_by_name(PREVIOUSLY_WORKED_LABEL))
    select.select_by_visible_text(NO)
    select = Select(driver.find_element_by_name(PREVIOUSLY_PARTNERED_LABEL))
    select.select_by_visible_text(NO)
    select = Select(driver.find_element_by_name(RELATIVE_WORKER_LABEL))
    select.select_by_visible_text(NO)
    select = Select(driver.find_element_by_name(ESSENTIAL_FUNCTIONS_LABEL))
    select.select_by_visible_text(YES)
    select = Select(driver.find_element_by_name(PREVIOUSLY_PARTNERED_LABEL))
    select.select_by_visible_text(NO)
    time.sleep(1)
    select = Select(driver.find_element_by_name(GENDER_LABEL))
    gender = random.choice(GENDERS_LIST)
    select.select_by_visible_text(gender)
    driver.find_element_by_xpath(MIXER_QUESTION_1_LABEL).click()
    driver.find_element_by_xpath(MIXER_QUESTION_2_LABEL).click()
    driver.find_element_by_xpath('//select[@name="' + STATE_LABEL + '"]/option[text()="' + CITIES_TO_STATES[random_city] + '"]').click()
    driver.find_element_by_xpath('//select[@name="' + PRESENT_EMPLOYEE + '"]/option[text()="' + random.choice([YES, NO]) + '"]').click()
    driver.find_element_by_xpath('//select[@name="' + REFERRAL_LABEL + '"]/option[text()="' + random.choice(REFERRAL_LIST) + '"]').click()
    driver.find_element_by_xpath('//select[@name="' + ETHNICITY_LABEL + '"]/option[text()="' + random.choice(ETHNICITY_LIST) + '"]').click()

    els = driver.find_elements_by_xpath(LONG_PERIODS_QUESTION_LABEL)
    [el.click() for el in els]

    fill_out_education_info(driver)
    fill_out_work_history(driver)

    time.sleep(3)
    driver.find_element_by_xpath(APPLY_BUTTON).click()
    time.sleep(3)
    try:
        driver.find_element_by_xpath('//*[@class="rcmSuccessBackToResultsBtn"]')
        print(f"successfully submitted application")
    except Exception as e:
        print(e)
        print('There may be unfilled items. Stop script and complete the application manually or wait to abort')
        time.sleep(5)

    # take out the trash
    os.remove(resume_filename+'.pdf')


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

def fill_out_education_info(driver):
    try:
        driver.find_element_by_xpath(DEGREE_COMPLETION_LABEL + '/option[text()="' + random.choice(GRADUATION_STATUS) + '"]').click()
        driver.find_element_by_xpath(DEGREE_MAJOR_LABEL + '/option[text()="' + random.choice(DEGREE_MAJORS) + '"]').click()
        driver.find_element_by_xpath(DEGREE_TYPE_LABEL + '/option[text()="' + random.choice(DEGREE_TYPES) + '"]').click()
        print('successfully filled out degree information')
    except Exception as e:
        print(f'Education info probably not required: {e}')
    time.sleep(2)


def fill_out_work_history(driver):
    for i in range(2):
        try:
            driver.find_element_by_xpath('(//select[@name="' + INDUSTRY_LABEL + '"]/option[text()="' + random.choice(INDUSTRY_LIST) + '"])[' + str(i+1) + ']').click()
        except Exception as e:
            print(f'Probably no work experience section: {e}')
            pass


def main():
    while True:
        random_city = random.choice(list(CITIES_TO_URLS.keys()))
        try:
            driver = start_driver(random_city)
        except Exception as e:
            printf(f"FAILED TO START DRIVER: {e}")
            pass

        time.sleep(2)

        fake_first_name = fake.first_name()
        fake_last_name = fake.last_name()
        fake_phone = fake.phone_number()
        
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
            'phone': fake_phone,
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


if __name__ == '__main__':
    main()
    sys.exit()
