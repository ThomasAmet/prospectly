import os
import re
import glob
from functools import partial
import pandas as pd
from utils_scraper import Scraper, Options
from selenium.webdriver.chrome.options import Options
# from bs4 import BeautifulSoup

# This takes the filename of your script, converts it to an absolute path, then extracts the directory of that path, then changes into that directory.
abspath = os.path.abspath(__file__)
dirname = os.path.dirname(abspath)
# os.chdir(dirname)
output_dir = os.path.join('scraping', 'output', 'real_estate')


###############################################################
#
# FUNCTION TO GET ALL AGENCIES DETAILS FROM REPOSITORY WEBSITE
#
###############################################################

driver_path = os.path.join('..', 'drivers', 'chromedriver')

options = Options()
options.add_argument('--incognito')
options.add_argument("--headless")
options.add_argument("--no-sandbox")
# options.add_argument("--log-level=3")
# options.add_argument("--disable-logging")

scraper = Scraper(driver_path=driver_path, driver_options=options)

# Script to parse
url = 'http://www.immobilieres-agences.fr/'
scraper.access_url(url)

# Get all categories link
categories = scraper.driver.find_elements_by_xpath('//a[@class="liencat"]')

# Go through all categories except FNAIM
for k in range(0, len(categories)):
    cat = categories[k]
    cat_name = cat.get_attribute('text')
    print(cat_name)
    if cat_name == ' FNAIM':
        continue

    # Declare a dataframe to store information form every agency in that category
    agencies_df = pd.DataFrame()

    # Open the category page in a new tab
    pages = []
    scraper.access_in_new_tab(cat.get_attribute('href'))

    # Find pagination links and add them to the pages list
    # scraper.driver.find_elements_by_xpath("//p[@class='gestion']//a")
    pages.extend([elt.get_attribute('href') for elt in scraper.driver.find_elements_by_xpath("//p[@class='gestion']//a")])

    # Create a pattern to match the differents parts of the full address and use * operator to unzip the tupples
    address_pattern = re.compile(r'^(.+)[\s](\d+)[\s]([\D]+)$')

    # Go through each category's page, get
    for j in range(0, len(pages)):
        print(pages[j])
        scraper.access_url(pages[j])

        # Get names, webiste, fulladdress and phone number for each agency displayed on that page (would have been better to loop over each agency but it doesnt work)
        agency_cards = scraper.driver.find_elements_by_class_name('elt_website')

        # Go through all agencies displayed in that page
        for agency_card in agency_cards:
            title_elt = agency_card.find_elements_by_xpath(".//*[@id='lien_1']")
            agency_name = title_elt[0].text if title_elt else None
            agency_website = title_elt[0].get_attribute('href') if title_elt else None

            full_address_elt = agency_card.find_elements_by_xpath(".//span[@itemprop='streetAddress'][1]")
            full_address = address_pattern.search(full_address_elt[0].text) if full_address_elt else None
            agency_address, agency_postalcode, agency_city = full_address.groups() if full_address else (None, None, None)

            phone_elt = agency_card.find_elements_by_xpath(".//span[@itemprop='telephone']")
            agency_phone = phone_elt[0].text.split('\nFacebook :')[0] if phone_elt else None

            facebook_elt = agency_card.find_elements_by_xpath(".//a[contains(@href,'facebook')]")
            agency_facebook = facebook_elt[0].get_attribute('href') if facebook_elt else None

            agency_dict = {
                'company_name': agency_name,
                'company_address': agency_address,
                'company_postalcode': agency_postalcode,
                'company_city': agency_city,
                'company_phone': agency_phone,
                'company_email': [],
                'company_website': agency_website,
                'company_facebook': agency_facebook,
                'contact_firstname': [],
                'contact_lastname': [],
                'contact_email': [],
                'contact_phone': [],
                'contact_position': [],
                'contact_linkedin': [],
            }

            # Create a data frame from the dict and clean it
            agency_df = pd.DataFrame({key: pd.Series(value) for key, value in agency_dict.items()})
            # Append the agency df to the agencies
            agencies_df = agencies_df.append(agency_df, ignore_index=True)


    # Save agencies dataframe by categories and by page in csv format
    file_name = str(pd.datetime.today())[:10] + '_' + cat_name + '_base_df_immobilier.csv'
    output_path = os.path.join(output_dir, file_name)
    agencies_df.to_csv(output_path, sep=';', index=False, encoding='utf-8')

    # Close the 'category' tab once we've been through all the pages
    scraper.close_current_tab()

############
#
# END SCRIPT
#
############



#######################################
#
# FUNCTION TO MERGE ALL THE DATASETS
# THAT WE CREATE FROM THE PREVIOUS STEP
#
#######################################

filename_pattern = "*.csv"
files_path = os.path.join(output_dir, filename_pattern)
all_agencies = pd.concat(map(partial(pd.read_csv, sep=';', encoding='utf-8', header=0), glob.glob(files_path)))
all_agencies['country'] = all_agencies.country.fillna('France')
all_agencies = all_agencies.reset_index(drop=True)

############
#
# END SCRIPT
#
############

###########################################################
#
# FUNCTION TO GO THROUGH ALL WEBSITE AND SCRAP CONTACT INFO
#
############################################################

agency_names = all_agencies['company_name'].to_list()
agency_websites = all_agencies['company_website'].to_list()
agency_cities = all_agencies['company_city'].to_list()
company_field = '(IMMOBILIER OR "REAL ESTATE")'

# Comment to avoid resetting df when running the code again
agencies_df = pd.DataFrame()

# Load existing file if necessary
# file_name = '2020-04-26_all_agency897_immobilier.csv'
# output_path = os.path.join(output_dir, 'results', file_name)
# df = pd.read_csv(output_path, sep=';', encoding='utf-8')
# agencies_df = df.append(agencies_df)


options = Options()
options.add_argument('--incognito')
options.add_argument("--headless")
options.add_argument("--no-sandbox")
driver_path = os.path.join('scraping', 'drivers', 'chromedriver')
scraper = Scraper(driver_path=driver_path, driver_options=options)


# Start loop
exceptions = [27, 42, 70, 93, 100, 101, 102, 110, 127, 164, 196, 349, 355, 424, 443, 455, 561, 565, 566, 582, 583, 584, 611, 621, 647, 674, 685, 689, 690, 739, 805, 898, 899, 934, 938, 952, 996, 997, 1023, 1042]

k = 1049
agency_range = range(k, len(agency_names))

for k in agency_range:
    print(k)
    print(agency_websites[k])
    agency_df = scraper.parse_website(url=agency_websites[k], company_name=agency_names[k], company_field=company_field, company_city=agency_cities[k])
    agencies_df = agencies_df.append(agency_df, ignore_index=True)

# End loop
# scraper.driver.switch_to.window(scraper.driver.window_handles[-1])




# Merge companys details we got from the main website and infos collected with the scraper and save
left = agencies_df.drop(agencies_df.columns[1:4], axis=1)

right = all_agencies.drop(all_agencies.columns[-7:-1], axis=1)
right = right.drop(right.columns[2], axis=1)

result = pd.merge(left, right, on=['company_name', 'company_website'])

file_name = str(pd.datetime.today())[:10] + '_all_agency951_final_immobilier.csv'
output_path = os.path.join(output_dir, 'results', file_name)
result.to_csv(output_path, sep=';', index=False, encoding='utf-8')




# Remove duplicates
# file_name = str(pd.datetime.today())[:10] + '_all_immo_937.tsv'
# file_path = os.path.join(output_dir, 'results', file_name)
# df = pd.read_csv(file_path, encoding='utf-8', sep='\t', header=0)
#
# df = df.sort_values(by=['contact_firstname', 'contact_lastname', 'contact_email', 'company_name', 'company_address'])
#
# df = df.drop_duplicates(subset=['company_name', 'company_address', 'contact_firstname', 'contact_lastname'], keep='first')
#
# file_name = str(pd.datetime.today())[:10] + '_all_immo_937.csv'
# file_path = os.path.join(output_dir, 'results', file_name)
# df.to_csv(file_path, encoding='utf-8', sep=';', index=False)