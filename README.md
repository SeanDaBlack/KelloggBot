# KelloggBot
Credit to SeanDaBlack for the basis of the script.

req.py is selenium python bot.
sc.js is a the base of the ios shortcut [COMING SOON]

# Setup

On mac/pc:

`pip install -r requirements.txt`

This will install `webdriver-manager` to automatically download the correct chrome driver. If you are having issues opening having it open chrome, check https://github.com/SergeyPirogov/webdriver_manager.

# Run

`python req.py` to run. It will loop until you kill the job. `ctrl + c` in your terminal to give the pro lifes a break (optional).

# Chrome drivers on MacOS

You might also get a trust issue with the downloaded driver being unverified. To fix that, run 

`xattr -d com.apple.quarantine chromedriver`

this just tells the OS it's safe to use this driver, and Selenium will start working. See https://timonweb.com/misc/fixing-error-chromedriver-cannot-be-opened-because-the-developer-cannot-be-verified-unable-to-launch-the-chrome-browser-on-mac-os/ for more info.
