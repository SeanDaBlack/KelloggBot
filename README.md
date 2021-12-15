# KelloggBot
[Setup](#setup)\
[Usage](#usage)

Credit to SeanDaBlack for the basis of the script.

main.py is selenium python bot.
sc.js is a the base of the ios shortcut [COMING SOON]

# Prerequisites

You must have an account with [Mail.com](https://mail.com) for recieving verification emails. Your username and password are entered into the app as plaintext, but are never stored and only transmitted through SSL encryption. You should still use a burner account, not one you care about.

# Setup

On mac/pc:

`pip install -r requirements.txt`

This will install `webdriver-manager` to automatically download the correct chrome driver. If you are having issues opening having it open chrome, check https://github.com/SergeyPirogov/webdriver_manager.

Poppler must also be installed for pdf2image. Follow the instructions at https://pdf2image.readthedocs.io/en/latest/installation.html to install.

It needs to be found in your `PATH` variable.

`export PATH=$PATH:$(pwd)`

`python main.py` to run. It will loop until you kill the job. `ctrl + c` in your terminal to give the pro lifes a break (optional).

mac:

You might also get a trust issue with the downloaded driver being unverified. To fix that, run 

`xattr -d com.apple.quarantine chromedriver`

this just tells the OS it's safe to use this driver, and Selenium will start working. See https://timonweb.com/misc/fixing-error-chromedriver-cannot-be-opened-because-the-developer-cannot-be-verified-unable-to-launch-the-chrome-browser-on-mac-os/ for more info.

You will also need to install ffmpeg if it is not already installed: [Mac installation guide](https://superuser.com/a/624562) [Windows installation guide](https://www.wikihow.com/Install-FFmpeg-on-Windows)

# Usage
```
usage: A script to automate very legitimate applications to kellogg's production plants affected by union strikes
       python3 main.py [-h] [--debug] [--mailtm]

options:
  -h, --help  show this help message and exit
  --debug     Puts script in a 'debug' mode where the Chrome GUI is visible

Kellogg bad | Union good | Support strike funds
```
