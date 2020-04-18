# Societe name
# Adresse
# Phone number

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# This takes the filename of your script, converts it to an absolute path, then extracts the directory of that path, then changes into that directory.
abspath = os.path.abspath(__file__)
dirname = os.path.dirname(abspath)
os.chdir(dirname)

input_path = os.path.join('..', 'input')
driver_path = os.path.join('..', 'drivers', 'chromedriver')
driver_options = Options()
driver_options.add_argument('--incognito')
driver = webdriver.Chrome(driver_path, options=driver_options)

url = 'http://www.immobilieres-agences.fr/'
subcat_list =