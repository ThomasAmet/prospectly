import os
import re
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from collections import Counter

from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
# from selenium.common.exceptions import ElementClickInterceptedException
# from selenium.common.exceptions import ElementNotInteractableException

# from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
# from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
# from selenium.common.exceptions import TimeoutException

# import inspect
import time
# import logging


# import bin.all_utils as utils

# This takes the filename of your script, converts it to an absolute path, then extracts the directory of that path, then changes into that directory.
abspath = os.path.abspath(__file__)
dir_name = os.path.dirname(abspath)
os.chdir(dir_name)

# Set the path to access the google chrome driver and some
driver_path = os.path.join('..', 'drivers', 'chromedriver')
WINDOW_SIZE = "1920,1080"

# Set the webdriver settings
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument("--incognito")
chrome_options.add_argument('--no-sandbox')

# chrome_options.add_argument('--no-startup-window')
# chrome_options.add_argument("--disable-notifications")
# chrome_options.add_argument("--disable-infobars")
# chrome_options.add_argument("start-maximized")
# # chrome_options.add_argument('--headless')
# # chrome_options.add_argument('--load-extension={}'.format(unpacked_extension_path))

driver = webdriver.Chrome(driver_path, options=chrome_options)

# 'bordeaux', 'lille', 'strasbourg', 'lyon', 'marseille', 'paris', 'nice', 'brest', 'le-havre', 'lorient', 'toulouse', 'perpignan', 'limoges', 'avignon', 'caen', 'tours', 'reims', 'nantes', 'montpellier', 'angers', 'dijon', 'grenoble', 'nimes',
cities_to_search = [ 'ajaccio', 'bastia']

# main_url = 'https://www.masalledesport.com/salle-de-sport,a,bordeaux?page=1'
# main_url = 'https://www.masalledesport.com/salle-de-sport,a,lille?page=1'

for city in cities_to_search:

    main_url = 'https://www.masalledesport.com/salle-de-sport,a,'+city+'?page=1'

    driver.get(main_url)


    # Set the number of page to go through
    try:
        page_number = int(driver.find_element_by_class_name('last').find_element_by_css_selector('a').get_attribute('data-page'))
    except:
        try:
            page_number = int(driver.find_element_by_class_name('pagination-nav').find_elements_by_css_selector('li')[-1].text)
        except:
            page_number = 1
    seq_pages = [i+1 for i in range(int(page_number))]
    # Manual hack to parse a specifc amount of page
    # seq_pages = np.arange(1, 2)


    # Create an empty dataframe that will receive club information from new pages after each iteration
    club_infos = pd.DataFrame()
    club_emails = pd.DataFrame()

    for p in seq_pages:
        print(p)
        # parse url to add the page_number desired
        url = main_url[:-1] + str(p)

        # Access the page and get the source code
        driver.get(url)
        # Get source code
        source = driver.page_source

        list_elements = driver.find_elements_by_xpath("//script[@type='application/ld+json']")
        list_infos_dict = [x.get_attribute('innerHTML') for x in list_elements] # get a list of dict for each club displayed on that page

        # Define empty list to get  club infos
        club_names = []
        club_addresses = []
        club_postals = []
        club_cities = []
        club_mainEmails = []
        club_bccEmails = []
        club_phones = []
        contacts_firstname_list = []
        contacts_lastname_list = []
        contacts_position_list = []
        contacts_linkedin_list = []


        for elt in list_infos_dict:
            # elt = list_infos_dict[0]
            result = [re.findall("(" + val + " .+?)<", source, re.IGNORECASE) for val in firstnames_list if
                      bool(re.search(val, source))]  # (?:) is a
            # .+? is reluctant and consumes/finds as few characters as it can VS .+ is greedy and consumes/finds as many characters as it can
            name = re.findall(r'"name".{1}(.+?\"),\"', elt)[0].strip().split('"')[1]
            if name == 'Studio Myosine':
                continue
            club_names.append(name.title())
            print('club: {}'.format(name))

            address = re.findall(r'"streetAddress".{1}(.+?\"),\"', elt)[0].strip()
            address = re.sub('"', '', address)
            club_addresses.append(address)

            # find the closest email to address or name in the source code
            email1 = re.findall(r'' + re.escape(address) + '.*?([\w\.-]+@[^\dx.jpg][^\dx.png][\w\.-]+)', source)
            email2 = re.findall(r'' + re.escape(name) + '.*?([\w\.-]+@[^\dx.jpg][^\dx.png][\w\.-]+)', source)
            email3 = re.findall(r'' + re.escape(address) + '.*?(?:\"to\":\"|\\\\n)([\w\.-]+@[\w\.-]+)', source)
            email4 = re.findall(r'' + re.escape(name) + '.*?(?:\"to\":\"|\\\\n)([\w\.-]+@[\w\.-]+)', source)

            emails = []
            emails.extend(email1)
            emails.extend(email2)
            emails.extend(email3)
            emails.extend(email4)

            try:
                first_digits = re.findall(r'\d+[\/-]', address)[0]
                street = re.sub(r'' + re.escape(first_digits), '', address).strip()
                email5 = re.findall(r'' + re.escape(street) + '.*?([\w\.-]+@[^\dx.jpg][^\dx.png][\w\.-]+)', source)
                email6 = re.findall(r'' + re.escape(street) + '.*?(?:\"to\":\"|\\\\n)([\w\.-]+@[\w\.-]+)', source)

                emails.extend(email5)
                emails.extend(email6)

            except IndexError:
                pass


            if not emails:
                email = ''
            else:
                max_occur = max(Counter(emails).values())
                occur_list = list(Counter(emails).values())
                index_occur_max = [i for i,x in enumerate(occur_list) if x == max_occur] # Get indices having the maximum occurence
                index_occur_max = max(index_occur_max)
                email = list(Counter(emails))[index_occur_max]

            club_mainEmails.append(email)


            # Find the URL for the club page and explore information coming from it in a new window
            sub_urls = re.findall('(https:.+?\d+)', elt)
            sub_url = [url for url in sub_urls if bool(re.findall(r'masalledesport',url)) ][0] # find a suburl containing 'masalledesport
            driver.execute_script("window.open('');")
            windows = driver.window_handles

            try:
                driver.switch_to.window(windows[1])
                driver.get(sub_url)
                sub_source = driver.page_source

                # Get the city and postal from the full address displayed on the top of the page
                club_location = driver.find_element_by_class_name('place-main-address').text
                club_location = club_location.split(',')[-1].strip(' ').split(' ')  # split by comma, remove trailing spaces and split again

                # First way from the main address
                club_postal = club_location[0]
                # Second way from the postalCode balise
                # club_postal = re.findall(r'"postalCode".{1}(.+?\"),\"', elt)[0].strip().split('"')[1]
                club_postals.append(club_postal)

                # First way from the main address
                club_city = club_location[1]
                # Second way of try
                # club_city = re.findall(r'"addressLocality".{1}(.+?\"),\"', elt)[0].strip().split('"')[1]
                club_cities.append(club_city)

                # Get email directly from the club webpage rather than taking it from the 'information card' in the main page
                # Easier way to get the email adress from the club but seems less accurate than the logic used above
                # email_contact = re.findall(r'([\w\.-]+@[^\dx.jpg][^\dx.png][\w\.-]+)', sub_source)[0]

                # Logic to get the phone number
                # Click on the phone button to unlock the phone number display
                try:
                    driver.find_element_by_xpath("//button[@class='button-phone undefined']").click()
                    time.sleep(1)
                    try:
                        # Get the phone number displayed if exists
                        phone = driver.find_element_by_xpath("//a[@class='button button-phone-displayed undefined']").text
                     except NoSuchElementException:
                        pass
                    try:
                        # If not available take the first number available in the source code (rough guess thats gonna be the correct one)
                        phones = re.findall(r'.{30}(\d{2}[\s\.]\d{2}[\s\.]\d{2}[\s\.]\d{2}[\s\.]\d{2})', sub_source)
                        if len(phones) > 3:
                            phone = phones[0]
                    except IndexError:
                        phone = ''
                except NoSuchElementException:
                    phone = ''
            except TimeoutException:
               phone = ''

            club_phones.append(phone)

            # The goal is to remove the city from the club_name to search google for the contact in a company
            full_address = driver.find_element_by_class_name("place-main-address").text
            driver.execute_script("window.open('https://www.google.fr');")
            # to switch to the most recently opened tab.
            driver.switch_to.window(driver.window_handles[-1])
            search_input = driver.find_element_by_name("q")
            # Remove the last word in the
            search_string =  full_address + " fitness"
            search_input.send_keys(search_string)
            search_input.send_keys(Keys.RETURN)


            # Look for the city name in the business name in google and remove it as long as the text located after(we dont remove it from the club_name directly from the website as there might be other location info that we want to get rid of (they are usually displayed after the city name in google)
            try:
                business_name = driver.find_element_by_css_selector("div[class^='kno-ecr-pt'] span").text
                business_name = re.search(r'^(.*) ' + club_city + '*', business_name).groups()[0]
            except:
                try:
                    search_input = driver.find_element_by_name("q")
                    search_input.clear()
                    search_string = name + ' ' + full_address
                    search_input.send_keys(search_string)
                    search_input.send_keys(Keys.RETURN)

                    business_name = re.search(r'^(.*) ' + club_city + '*', business_name).groups()[0]
                # If no google business result, then use club_name
                except:
                    business_name = name

            # Search in google for any contact using the business name and special research
            search_input = driver.find_element_by_name("q")
            search_input.clear()
            google_search = business_name + ' AND ' + club_city + ' AND (PDG OR Gérant) OR (Manager OR Chef) OR (Directeur OR Responsable) site:linkedin.com/'
            search_input.send_keys(google_search)
            search_input.send_keys(Keys.RETURN)

            # Extract the fist name the last name and the position from LinkedIn first result (if exists)
            try:
                # Take the next result as long as there the result redirect to a job opporutnity
                i = 0
                redirect_link = driver.find_elements_by_class_name("r")[i].find_element_by_css_selector('[href]').get_attribute('href')
                while bool(re.search(r'jobs', redirect_link)):
                    i += 1
                    redirect_link = driver.find_elements_by_class_name("r")[i].find_element_by_css_selector('[href]').get_attribute('href')
                first_result = driver.find_elements_by_class_name("r")[i].text
                club_contact_firstname = first_result.split("-")[0].strip().split()[0].title()
                club_contact_lastname = ''.join(first_result.split("-")[0].strip().split()[1:]).title()
                club_contact_position = first_result.split("-")[1].strip().title()
                club_contact_linkedin = redirect_link
            except:
                club_contact_firstname = ''
                club_contact_lastname = ''
                club_contact_position = ''
                club_contact_linkedin = ''

            contacts_firstname_list.append(club_contact_firstname)
            contacts_lastname_list.append(club_contact_lastname)
            contacts_position_list.append(club_contact_position)
            contacts_linkedin_list.append(club_contact_linkedin)

            print('firstnames_list: {}'.format(contacts_firstname_list))
            # Close the 2 tabs and select the initial tab
            driver.close()
            driver.switch_to.window(windows[-1])
            driver.close()
            driver.switch_to.window(windows[0])
            # end of the loop

        # Get secondary email if available
        # Get the main emails first then check if second email (bcc) is available. If so, creates a second list with only bcc email
        email_having_bcc = re.findall(r'\"to\":\"([\w\.-]+@[\w\.-]+)\",\"bcc', source)  # email having a bcc email, ending with 'bcc'
        # club_bcc_emails = re.findall(r'\"bcc\":(\"[\w\.-]+@[\w\.-]+\")', source)  # bcc email, starting with 'bcc'
        club_bcc_emails = re.findall(r'\"bcc\":(\".+?),\"', source)  # bcc email, starting with 'bcc'
        club_bcc_emails = [re.sub('"', '', email) for email in club_bcc_emails]

        # Create a dict of paired main email and bcc email
        replacement_dict = dict(zip(email_having_bcc, club_bcc_emails))
        # club_second_emails = [replacement_dict.get(elt, elt) for elt in club_main_emails] # keep the value if not in dict
        # club_second_emails = [replacement_dict.get(elt) for elt in club_main_emails] # replace by empty string if list elt is not in dict
        club_bccEmails = [replacement_dict.get(elt) if elt in replacement_dict else '' for elt in club_mainEmails]  # replace by empty string if list elt is not in dict

         # Get all phone number in the source source page
         # re.findall(r'(.{300}\d{2}[\s\.]\d{2}[\s\.]\d{2}[\s\.]\d{2}[\s\.]\d{2})', source)


        club_infos_temp = pd.DataFrame({
        'Club_Name': club_names,
        'Club_Address': club_addresses,
        'Club_Postal': [re.sub('"', '', postal) for postal in club_postals],
        'Club_City': [re.sub('"', '', city) for city in club_cities],
        'Club_Phone': club_phones,
        'Club_Email_Main': club_mainEmails,
        'Club_Email_Bcc': club_bccEmails,
        'Club_Contact_FirstName': contacts_firstname_list,
        'Club_Contact_LastName': contacts_lastname_list,
        'Club_Contact_Position': contacts_position_list,
        'Club_Contact_Linkedin': contacts_linkedin_list,
        })


        # club_emails_temp = pd.DataFrame({
        # 'Club_Email_Main': club_main_emails,
        # 'Club_Email_Bcc': club_second_emails
        # })

        club_infos = club_infos.append(club_infos_temp, ignore_index=True)


    # Save files created
    output_dir = os.path.join(os.path.dirname(dir_name), 'output')
    # output_name = str(pd.datetime.today())[:10]+'_'+club_infos.Club_City[0]+'_fitness.csv'
    output_name = str(pd.datetime.today())[:10] + '_' + city + '_fitness.csv'
    output_path = os.path.join(output_dir, output_name)
    club_infos.to_csv(output_path, sep=';', index=False, encoding='utf-8')



# Remove accent method
# import unicodedata
# s1 = unicode(s,'utf-8')
# >>> s2 = unicodedata.normalize('NFD', s1).encode('ascii', 'ignore')

