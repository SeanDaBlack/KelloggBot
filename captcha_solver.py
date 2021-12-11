# 100% credit to GitHub user @jimrushing for this code.
# All I've done is split it into its own class and merged it with my fork.

import speech_recognition
from pydub import AudioSegment
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time
import requests

audio_filename = 'captcha_audio'
recognizer = speech_recognition.Recognizer()

def audio_to_text(mp3_path):
    # convert wav to mp3                                                            
    sound = AudioSegment.from_mp3(mp3_path)
    sound.export(audio_filename+'.wav', format="wav")

    with speech_recognition.AudioFile(audio_filename+'.wav') as source:
        audio_text = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio_text)
            print('Converting audio transcripts into text ...')
            return(text)     
        except Exception as e:
            print(e)
            print('Sorry.. run again...')

def saveFile(content,filename):
    with open(filename, "wb") as handle:
        for data in content.iter_content():
            handle.write(data)

def solve_captcha(driver):
    googleClass = driver.find_elements_by_class_name('recapBorderAccessible')[0]
    time.sleep(2)
    outeriframe = googleClass.find_element_by_tag_name('iframe')
    time.sleep(1)
    outeriframe.click()
    time.sleep(2)
    allIframesLen = driver.find_elements_by_tag_name('iframe')
    time.sleep(1)
    audioBtnFound = False
    audioBtnIndex = -1
    for index in range(len(allIframesLen)):
        driver.switch_to.default_content()
        iframe = driver.find_elements_by_tag_name('iframe')[index]
        driver.switch_to.frame(iframe)
        driver.implicitly_wait(2)
        try:
            audioBtn = driver.find_element_by_id('recaptcha-audio-button') or driver.find_element_by_id('recaptcha-anchor')
            audioBtn.click()
            audioBtnFound = True
            audioBtnIndex = index
            break
        except Exception as e:
            pass
    if audioBtnFound:
        try:
            while True:
                href = driver.find_element_by_id('audio-source').get_attribute('src')
                response = requests.get(href, stream=True)
                saveFile(response,audio_filename+'.mp3')
                response = audio_to_text(audio_filename+'.mp3')
                print(response)
                driver.switch_to.default_content()
                iframe = driver.find_elements_by_tag_name('iframe')[audioBtnIndex]
                driver.switch_to.frame(iframe)
                inputbtn = driver.find_element_by_id('audio-response')
                inputbtn.send_keys(response)
                inputbtn.send_keys(Keys.ENTER)
                time.sleep(2)
                errorMsg = driver.find_elements_by_class_name('rc-audiochallenge-error-message')[0]
                if errorMsg.text == "" or errorMsg.value_of_css_property('display') == 'none':
                    print("reCaptcha defeated!")
                    break
        except Exception as e:
            print(e)
            print('Oops, something happened. Check above this message for errors or check the chrome window to see if captcha locked you out...')
    else:
        print('Button not found. Likely the captcha did not need solving.')