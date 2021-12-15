from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

import random
import imaplib
import email
import re

def start_driver() -> webdriver.Chrome :
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get('https://mail.com/')
    driver.implicitly_wait(10)
    return driver

def login(driver: webdriver.Chrome, username: str, password: str):
    # login
    driver.find_element_by_id('login-button').click()
    driver.find_element_by_id('login-email').send_keys(username)
    driver.find_element_by_id('login-password').send_keys(password)
    driver.find_element_by_class_name('login-submit').click()

    # go to mail settings
    driver.find_element_by_xpath('//a[@data-item-name="more"]').click()
    driver.find_element_by_xpath('//a[@data-item-name="mail_settings"]').click()
    driver.switch_to.frame(driver.find_element_by_id('thirdPartyFrame_mail'))

    # go to alias addresses
    driver.find_element_by_xpath('//a[@data-webdriver="ALL_EMAIL_ADDRESSES"]').click()
 
def add_alias(driver: webdriver.Chrome, alias: str) -> str:
    # delete old alias
    try:
        actions = ActionChains(driver)
        actions.move_to_element(driver.find_element_by_class_name('is-last'))
        actions.perform()
        driver.find_element_by_xpath('//a[@title="Delete Alias Address"]').click()
        driver.find_element_by_xpath('//button[@data-webdriver="primary"]').click()
    except Exception as e:
        print('Unable to remove old alias. Likely it did not exist.')

    # add new alias
    driver.find_element_by_xpath('//input[@data-webdriver="localPart"]').send_keys(alias)
    dropdown = Select(driver.find_element_by_name('fieldSet:fieldSet_body:grid:addressSelection:domainSelection'))
    options = [item.text for item in dropdown.options]
    hostname = random.choice(options)
    dropdown.select_by_visible_text(hostname)
    driver.find_element_by_xpath('//button[@data-webdriver="button"]').click()

    return alias+'@'+hostname

def get_verification_code(username: str, password: str):
    # connect to host using SSL
    imap = imaplib.IMAP4_SSL('imap.mail.com', 993)

    ## login to server
    imap.login(username, password)

    _, messages = imap.select('INBOX')
    imap.sort('REVERSE DATE','UTF-8','ALL')

    num_messages = int(messages[0])
    if not num_messages:
        return None

    _, msg = imap.fetch(str(num_messages), '(RFC822)')
    body = email.message_from_bytes(msg[0][1]).get_payload()
    delete_last_message(imap)

    found_passcode = re.search('(?<=n is ).*?(?=<)', body)
    return found_passcode.group(0) if found_passcode else None

def delete_last_message(imap: imaplib.IMAP4_SSL):
    _, messages = imap.select('INBOX')
    imap.sort('REVERSE DATE','UTF-8','ALL')

    num_messages = int(messages[0])
    if not num_messages:
        return 

    _, msg = imap.fetch(str(num_messages), '(RFC822)')
    message_num = msg[0][0].split()[0]
    imap.store(message_num, '+FLAGS', '\\Deleted')
    imap.expunge()