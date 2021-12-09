# AbBOT
Credit to SeanDaBlack for the basisof the script.

req.py is selenium python bot.
sc.js is a the base of the ios shortcut

# Setup

On mac:

`pip install -r requirements.txt`

You will probably need to go get the chrome driver to make selenium work, as they are version-specific. The one in the repo might not do it for you. Find your chrome version by going to **Chrome** >> **About Google Chrome**. 

This will open a tab that shows you your verison. Visit https://sites.google.com/chromium.org/driver/downloads and download the driver for your version.

folder. Extract the downloaded zip file. Move the extracted chromedriver binary to this project folder

`mv ~/Downloads/chromedriver .`

It needs to be found in your `PATH` variable.

`export PATH=$PATH:$(pwd)`

You might also get a trust issue with the downloaded driver being unverified. To fix that, run 

`xattr -d com.apple.quarantine chromedriver`

this just tells the OS it's safe to use this driver, and Selenium will start working. See https://timonweb.com/misc/fixing-error-chromedriver-cannot-be-opened-because-the-developer-cannot-be-verified-unable-to-launch-the-chrome-browser-on-mac-os/ for more info.


`python req.py` to run. It will loop until you kill the job. `ctrl + c` in your terminal to give the pro lifes a break (optional).
