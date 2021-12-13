XPATHS_1 = {
    'resume': '//*[@id="49:_file"]',
    'addy': '//*[@name="address"]',
    'city': '//*[@name="city"]',
    'zip': '//*[@name="zip"]',
    'job': '//*[@name="currentTitle"]',
    'salary': '//*[@name="expectedSalaryRange"]',
    'country': '//*[@name="country"]'
}

XPATHS_2 = {
    'email': '//*[@id="fbclc_userName"]',
    'email-retype': '//*[@id="fbclc_emailConf"]',
    'pass': '//*[@id="fbclc_pwd"]',
    'pass-retype': '//*[@id="fbclc_pwdConf"]',
    'first_name': '//*[@id="fbclc_fName"]',
    'last_name': '//*[@id="fbclc_lName"]',
    'pn': '//*[@id="fbclc_phoneNumber"]',
}

APPLY_NOW_BUTTON_1 = '//*[@id="content"]/div/div[2]/div/div[1]/div[1]/div/div/button'
APPLY_NOW_BUTTON_2 = '//*[@id="applyOption-top-manual"]'
CREATE_AN_ACCOUNT_BUTTON = '//*[@id="page_content"]/div[2]/div/div/div[2]/div/div/div[2]/a'
READ_ACCEPT_DATA_PRIVACY_STATEMENT_ANCHORTAG = '//*[@id="dataPrivacyId"]'
ACCEPT_BUTTON = '//*[@id="dlgButton_20:"]'
CREATE_ACCOUNT_BUTTON = '//*[@id="fbclc_createAccountButton"]'
PROFILE_INFORMATION_DROPDOWN = '//*[@id="109:topBar"]'
CANDIDATE_SPECIFIC_INFORMATION_DROPDOWN = '//*[@id="260:topBar"]'
UPLOAD_A_RESUME_BUTTON = '//*[@id="48:_attach"]/div[6]'
MIXER_QUESTION_1_LABEL = '//label[text()="350 LBS"]'
MIXER_QUESTION_2_LABEL = '//label[text()="800 LBS"]'
LONG_PERIODS_QUESTION_LABEL = '//label[text()="Yes"]'
APPLY_BUTTON = '//span[text()="Apply"]'

# Education Info (using 'select' instead of * for dropdown items)
DEGREE_COMPLETION_LABEL = '//select[@name="VFLD4"]'
DEGREE_MAJOR_LABEL =  '//select[@name="VFLD2"]'
DEGREE_TYPE_LABEL =  '//select[@name="VFLD3"]'
