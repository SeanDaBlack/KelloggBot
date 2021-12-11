import functools
import os
import random
import sys
import time

import requests
import speech_recognition as sr
from faker import Faker
from pydub import AudioSegment
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from constants.classNames import *
from constants.common import *
from constants.elementIds import *
from constants.email import *
from constants.filenames import *
from constants.location import *
from constants.tagNames import *
from constants.urls import *
from constants.xPaths import *

fake = Faker()
chromedriver_location = CHROMEDRIVER_PATH
filename = CAPTCHA_MP3_FILENAME
speech_recognition_recognizer = sr.Recognizer()
# Change default in module for print to flush
# https://stackoverflow.com/questions/230751/how-can-i-flush-the-output-of-the-print-function-unbuffer-python-output#:~:text=Changing%20the%20default%20in%20one%20module%20to%20flush%3DTrue
print = functools.partial(print, flush=True)


def start_driver(random_city):
    driver = webdriver.Chrome(chromedriver_location)
    driver.get(CITIES_TO_URLS[random_city])
    driver.implicitly_wait(10)
    time.sleep(2)
    driver.find_element_by_xpath(APPLY_NOW_BUTTON_1).click()
    driver.find_element_by_xpath(APPLY_NOW_BUTTON_2).click()
    driver.find_element_by_xpath(CREATE_AN_ACCOUNT_BUTTON).click()
    return driver


def generate_account(driver):
    # make fake account info and fill

    name = fake.name()
    first_name = name.split(" ")[0]
    last_name = name.split(" ")[1]
    email = fake.free_email()
    password = fake.password()
    for key in XPATHS_2.keys():
        match key:
            case 'email' | 'email-retype':
                info = email
            case 'pass' | 'pass-retype':
                info = password
            case 'first_name':
                info = first_name
            case 'last_name':
                info = last_name
            case 'pn':
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
    googleClass = driver.find_elements_by_class_name(CAPTCHA_BOX)[0]
    time.sleep(2)
    outerIFrame = googleClass.find_element_by_tag_name(IFRAME)
    time.sleep(1)
    outerIFrame.click()
    time.sleep(2)
    allIframesLen = len(driver.find_elements_by_tag_name(IFRAME))
    time.sleep(1)
    audioBtnFound = False
    audioBtnIndex = -1
    for i in range(allIframesLen):
        driver.switch_to.default_content()
        iframe = driver.find_elements_by_tag_name(IFRAME)[i]
        driver.switch_to.frame(iframe)
        driver.implicitly_wait(2)
        try:
            print(f'TRYING {i + 1} of {allIframesLen} ...')
            audioBtn = driver.find_element_by_id(RECAPTCHA_AUDIO_BUTTON) or driver.find_element_by_id(RECAPTCHA_ANCHOR)
            audioBtn.click()
            audioBtnFound = True
            audioBtnIndex = i
            break
        except Exception as e:
            print(f'TRY {i + 1} of {allIframesLen} FAILED: {e}')
            pass
    if audioBtnFound:
        try:
            while True:
                href = driver.find_element_by_id(AUDIO_SOURCE).get_attribute('src')
                response = requests.get(href, stream=True)
                saveFile(response, filename)
                response = audioToText(filename)
                print(f'TRYING "{response}" TO SOLVE RECAPTCHA...')
                driver.switch_to.default_content()
                iframe = driver.find_elements_by_tag_name(IFRAME)[audioBtnIndex]
                driver.switch_to.frame(iframe)
                inputButton = driver.find_element_by_id(AUDIO_RESPONSE)
                inputButton.send_keys(response)
                inputButton.send_keys(Keys.ENTER)
                time.sleep(2)
                errorMsg = driver.find_elements_by_class_name(AUDIO_ERROR_MESSAGE)[0]
                if errorMsg.text == "" or errorMsg.value_of_css_property('display') == 'none':
                    print("RECAPTCHA DEFEATED")
                    break
        except Exception as e:
            print(e)
            print(
                'Oops, something happened. Check above this message for errors or check the chrome window to see if captcha locked you out...')
    else:
        print('Button not found. This should not happen.')
    time.sleep(2)
    driver.switch_to.default_content()
    driver.find_element_by_xpath(CREATE_ACCOUNT_BUTTON).click()
    time.sleep(1.5)

    print(f"successfully made account for fake email {email}")


def fill_out_application_and_submit(driver, random_city):
    driver.implicitly_wait(10)

    # fill out form parts of app
    driver.find_element_by_xpath(PROFILE_INFORMATION_DROPDOWN).click()
    driver.find_element_by_xpath(CANDIDATE_SPECIFIC_INFORMATION_DROPDOWN).click()

    for key in XPATHS_1.keys():

        match key:
            case 'resume':
                driver.find_element_by_xpath(UPLOAD_A_RESUME_BUTTON).click()
                info = os.getcwd() + RESUME_PATH
            case 'addy':
                info = fake.street_address()
            case 'city':
                info = random_city
            case 'zip':
                info = CITIES_TO_ZIP_CODES[random_city]
            case 'job':
                info = fake.job()
            case 'salary':
                info = random.randint(15, 35)

        driver.find_element_by_xpath(XPATHS_1.get(key)).send_keys(info)

    print(f"successfully filled out app forms for {random_city}")

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
    print(f"successfully submitted application")
    time.sleep(5)


def random_email(name=None):
    if name is None:
        name = fake.name()

    mailGens = [lambda fn, ln, *names: fn + ln,
                lambda fn, ln, *names: fn + "." + ln,
                lambda fn, ln, *names: fn + "_" + ln,
                lambda fn, ln, *names: fn[0] + "." + ln,
                lambda fn, ln, *names: fn[0] + "_" + ln,
                lambda fn, ln, *names: fn + ln + str(int(1 / random.random() ** 3)),
                lambda fn, ln, *names: fn + "." + ln + str(int(1 / random.random() ** 3)),
                lambda fn, ln, *names: fn + "_" + ln + str(int(1 / random.random() ** 3)),
                lambda fn, ln, *names: fn[0] + "." + ln + str(int(1 / random.random() ** 3)),
                lambda fn, ln, *names: fn[0] + "_" + ln + str(int(1 / random.random() ** 3)), ]

    emailChoices = [float(line[2]) for line in EMAIL_DATA]

    return random.choices(mailGens, MAIL_GENERATION_WEIGHTS)[0](*name.split(" ")).lower() + "@" + \
           random.choices(EMAIL_DATA, emailChoices)[0][1]


def audioToText(mp3Path):
    # convert wav to mp3
    sound = AudioSegment.from_mp3(mp3Path)
    sound.export(CAPTCHA_WAV_FILENAME, format="wav")

    with sr.AudioFile(CAPTCHA_WAV_FILENAME) as source:
        audio_text = speech_recognition_recognizer.listen(source)
        try:
            text = speech_recognition_recognizer.recognize_google(audio_text)
            print('Converting audio transcripts into text ...')
            return text
        except Exception as e:
            print(e)
            print('Sorry.. run again...')


def saveFile(content, filename):
    with open(filename, "wb") as handle:
        for data in content.iter_content():
            handle.write(data)


def main():
    while True:
        random_city = random.choice(list(CITIES_TO_URLS.keys()))
        try:
            driver = start_driver(random_city)
        except Exception as e:
            print(f"FAILED TO START DRIVER: {e}")
            pass

        time.sleep(2)

        try:
            generate_account(driver)
        except Exception as e:
            print(f"FAILED TO CREATE ACCOUNT: {e}")
            pass

        try:
            fill_out_application_and_submit(driver, random_city)
        except Exception as e:
            print(f"FAILED TO FILL OUT APPLICATION AND SUBMIT: {e}")
            pass
            driver.close()
            continue

        driver.close()
        time.sleep(5)


if __name__ == '__main__':
    main()
    sys.exit()
