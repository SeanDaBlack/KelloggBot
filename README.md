# KelloggBot
Credit to SeanDaBlack for the basis of the script.

main.py is selenium python bot.
sc.js is a the base of the ios shortcut [COMING SOON]

# Setup

On mac/pc:

`pip install -r requirements.txt`

Poppler must also be installed for pdf2image. Follow the instructions at https://pdf2image.readthedocs.io/en/latest/installation.html to install.

This will install `webdriver-manager` to automatically download the correct chrome driver. If you are having issues opening having it open chrome, check https://github.com/SergeyPirogov/webdriver_manager.

`mv ~/Downloads/chromedriver .`

It needs to be found in your `PATH` variable.

`export PATH=$PATH:$(pwd)`

`python main.py` to run. It will loop until you kill the job. `ctrl + c` in your terminal to give the pro lifes a break (optional).

mac:

You might also get a trust issue with the downloaded driver being unverified. To fix that, run 

`xattr -d com.apple.quarantine chromedriver`

this just tells the OS it's safe to use this driver, and Selenium will start working. See https://timonweb.com/misc/fixing-error-chromedriver-cannot-be-opened-because-the-developer-cannot-be-verified-unable-to-launch-the-chrome-browser-on-mac-os/ for more info.

You will also need to install ffmpeg if it is not already installed: [Mac installation guide](https://superuser.com/a/624562) [Windows installation guide](https://www.wikihow.com/Install-FFmpeg-on-Windows)