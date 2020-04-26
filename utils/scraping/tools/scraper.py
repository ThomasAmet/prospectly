# Small df to test stuff
# data = {"Name": ["James", "Alice", "Phil", "James"],
# 		"Age": [24, 28, 40, 24],
# 		"Sex": ["Male", "Female", "Male", "Male"]}
# df = pd.DataFrame(data)
# print(df)
import os
import re
import time
import pandas as pd
import numpy as np
from collections import Counter
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

abspath = os.path.abspath(__file__)
dirname = os.path.dirname(abspath)
os.chdir(dirname)

input_path = os.path.join('..', 'input')
driver_path = os.path.join('drivers', 'chromedriver')

firstnames_df = pd.read_csv(os.path.join(input_path, 'nat2018.csv'), sep=';', header=0)

firstnames_list = firstnames_df.iloc[:3000, 0].values.tolist()
firstnames_list = list(map(lambda x: x.capitalize(), firstnames_list)) #map a capitlize function to initial list
firstnames_list.extend(['Abby', 'Arber'])


Options = Options

class Scraper:

    def __init__(self, driver_path, driver_options):
        self.driver = webdriver.Chrome(driver_path, options=driver_options)
        # self.driver = webdriver.Firefox('/Users/username/Applications/Firefox')
        self.firstnames_list = firstnames_list
        self.company_city = ''

    def init_lists(self):
        self.website_emails = []
        self.website_phones = []
        self.website_contacts_firstnames = []
        self.website_contacts_lastnames = []
        self.website_contacts_emails = []
        self.website_contacts_phones = []
        return 0

    def access_url(self, url):
        driver = self.driver
        driver.get(url)
        source = driver.page_source
        pretty_soup = BeautifulSoup(source, features="html.parser").prettify()
        return source, pretty_soup


    def access_in_new_tab(self, link):
        # Open the link in a new tab do some stuff
        driver = self.driver
        driver.execute_script("window.open('');")
        tabs = driver.window_handles # all_tabs
        driver.switch_to.window(tabs[-1])  # switch to last active tab
        driver.get(link)
        source = driver.page_source
        pretty_soup = BeautifulSoup(source, features="html.parser").prettify()
        return source, pretty_soup


    def close_current_tab(self):
        self.driver.implicitly_wait(1)
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])
        self.driver.close()
        self.driver.implicitly_wait(1)
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])


    def firstname_pattern(self, x):
        '''
            This pattern return a list of actual firstnames found on specific page (works on both test pages)
        '''
        # return re.compile('([\w-]*' + x + ')[<\s]') # Will allow names like Jean-Marie-Emmanuel (unlikely) but accept cities like Bussy-Saint-Antoine
        return re.compile('((?:[\w]*[-]){0,1}' + x + ')[<\s]')
        # return re.compile('[\s>]*((?:[\w]*[-]){0,1}' + x + ')[<\s]*')


    def fullname_pattern(self, x):
        '''
        This pattern get the full names from a first name
        :param x:
        :return: Matching string that contains a name x and:
            - which might be preceeded by another word separated by a dash (to handle names like Pierre-Marie if not in list of names)
            - which might be followed by a separation particule + a string containing only letters (to match for ex Paul de Sauvage)
            - that end with a string containing only letters followed by a any space (tab,space,newline etc.) or a closing tag
        '''
        # return re.compile("((?:[A-z]+?-)" + x + "(?:de |d'|le|l'|du|de la| )[A-z ]+)[<\s]") #old one, that works, to keep in case
        # return re.compile("(" + x + "(?:de|d'|d’|le|l'|l’|du|de la|Da| )*[A-z!_]+?)[<\s,$]")
        return re.compile("(" + x + "(?:de|d'|d’|le|l'|l’|du|de la|Da| )*(?!Gaulle)[A-z!_]{3}[a-z!_]*?)[<\s,$]")


    def email_pattern(self, firstname=None, after=True):
        if not firstname:
            email_pattern = '(?:mailto:)([\w.-]+?@[\w.-]+?\.[\w]+)'
            return re.compile(email_pattern)
        if after:
            return re.compile(firstname + '.*?([\w.-]+?@[\w.-]+?\.[\w]+)', re.S)
        return re.compile(r'\b([\w.-]+@[\w.-]+\.\w+)(?:(?![\w.-]+@[\w.-]+\.\w).)*?\b' + firstname + r'\b', re.S)


    def phone_pattern(self, firstname=None, after=True):
        """
                \+\d{2}[-.\s]?(?:\(0\)|0)*?[-.\s]?          # Dialing code +CC00(0) or +CC00 or +CC00 0
                00[-.\s]?\d{2}[-.\s]?(?:\(0\)|0)*?[-.\s]?   # Dialing code 0033 \(0)|0
                (?:\(0\)|0|)\d?[-.\s]?                      # First number (from 1 to 9) preceeded by a non mandatory 0 or (0)
                (?:\d{2}[-.\s]?){3,4})                      # End of the phone number (3 or 4 times 2 following digits separated or not by .- )
                (?:$|\D)                                    # Anything but a number or the end of string
        """
        # To be improved to make the 0 mandatory when +33 or 00 is missing. Ex it will match 234558899
        # return re.compile('((?:\+\d{2}|00[-.\s]?\d{2})?[-.\s]?(?:\(0\)|0|)\d?[-.\s]?(?:\d{2}[-.\s]?){3,4})')
        # This version should tka
        # phone_pattern = '((?:\+\d{2}[-.\s]?(?:\(0\)|0)*?[-.\s]?|00[-.\s]?\d{2}[-.\s]?(?:\(0\)|0)*?[-.\s]?|0)\d?[-.\s]?(?:\d{2}[-.\s]?){3,4})(?:$|\D)'
        # This version even take into consideration phone number in Luxembourg
        first_phone_pattern = '((?:\+\d{2}[-.\s]?(?:\(0\)|0)*[-.\s]?|00[-.\s]?\d{2}[-.\s]?(?:\(0\)|0)*[-.\s]?|0)\d?[-.\s]?\d{2,3}[-.\s]?(?:\d{2}[-.\s]?){2,3})(?:$|\D)'
        second_phone_pattern = '((?:\+\d{2}[-.\s]?(?:\(0\)|0)*?[-.\s]?|00[-.\s]?\d{2}[-.\s]?(?:\(0\)|0)*?[-.\s]?|0)\d?[-.\s]?\d{2,3}[-.\s]?(?:\d{2}[-.\s]?){2,3})(?:$|\D)'
        non_capturing_pattern = '(?:\+\d{2}[-.\s]?(?:\(0\)|0)*?[-.\s]?|00[-.\s]?\d{2}[-.\s]?(?:\(0\)|0)*?[-.\s]?|0)\d?[-.\s]?\d{2,3}[-.\s]?(?:\d{2}[-.\s]?){2,3}(?:$|\D)'

        if not firstname:
            return re.compile(first_phone_pattern)

        if after:
            return re.compile(firstname + '.*?' + first_phone_pattern)
        return re.compile('\b(' + non_capturing_pattern + ')(?:(?!' + non_capturing_pattern + ').)*?\b' + firstname + r'\b')


    def get_emails(self, source):
        p = self.email_pattern()
        emails = p.findall(source)
        return emails


    def get_phones(self, source):
        p = self.phone_pattern()
        phones = p.findall(source)
        return phones


    def get_lastnames_meth1(self):
        '''
        Retrieve lastname from firstname, if no lastname is found, we remove firstnames from the list
        Ex: print(get_family_names(actual_firstnames, actual_fullnames))
        '''
        firstnames = self.ordered_firstnames
        fullnames = self.ordered_fullnames
        # print('firstnames before get_lastnames_meth1: {}'.format(firstnames))
        # print('fullnames before get_lastnames_meth1: {}'.format(fullnames))

        if not len(firstnames) == len(fullnames):
            # if diff length btw fullnames and firstnames, remove firstnames that are not in fullnames
            for firstname in firstnames:
                if pd.isnull([re.search(firstname, fullname) for fullname in fullnames]).all():
                    firstnames.remove(firstname)
            # keep the first part of the fullname and assign as firstname
            if not len(firstnames) == len(fullnames):
                firstnames = [elt.split()[0] for elt in fullnames]

        # once both list are with the same length we retrieve the lastname and remove both leading and trailing spaces
        lastnames = [re.split(firstname, fullname)[1].strip() for firstname, fullname in zip(firstnames, fullnames)]

        return firstnames, lastnames



    def get_lastnames_meth2(self):
        '''
                For each unique class_name (usually_one):
                Retrieve text in siblings, child and parents, going to the next method if the previous one failed.
                The methods are sorted by decreasing order of the odds of yielding a result        '''

        firstnames = self.ordered_firstnames
        lastnames = []

        for firstname in firstnames:
            #  We first retrieve the class of the firstname
            class_name = self.retrieve_firstname_class(firstname)

            # If the class is nonem then we  remove the firstname from the list
            if not class_name:
                firstnames.remove(firstname)
                continue

            # Find the class of firstnames following siblings and access their text
            xpath = "//*[@class='{}']//following-sibling::*".format(class_name)
            after_siblings = self.driver.find_elements_by_xpath(xpath)
            lastnames.extend([sibling.text for sibling in after_siblings]) # last_name are return by order of appearance in the page

            if not lastnames:
                # Find the class of firstnames preceding siblings and access their text
                xpath = "//*[@class='{}']//preceding-sibling::*".format(class_name)
                before_siblings = self.driver.find_elements_by_xpath(xpath)
                lastnames.extend([sibling.text for sibling in before_siblings])

            if not lastnames:
                # Find the class of firstnames' children
                xpath = "//*[@class='{}']//child::*".format(class_name)
                children = self.driver.find_elements_by_xpath(xpath)
                lastnames.extend([child.text for child in children])

            if not lastnames:
                # Find the class of firstname's parent and access its text (might return the full name !! To be checked)
                # xpath = "//*[@class='{}']//parent::*".format(class_name)
                xpath = "//*[@class='{}']/..".format(class_name)
                parents = self.driver.find_elements_by_xpath(xpath)
                lastnames.extend([parent.text for parent in parents])

            if not lastnames:
                self.ordered_firstnames.remove(firstname)

        lastnames = [elt.strip() for elt in lastnames if elt]
        return firstnames, lastnames



    def get_contacts_names(self, source):
        '''
        Look for all the firstnames in a page then look for a fullname (firstname + lastname).
        Finally return a list of firstnames and lastnames associated
        :param source:
        :return: 2 lists: firstnames, lastnames
        '''

        # Retrieve the firstname whenever there is a match and return a list
        firstnames_found = [self.firstname_pattern(val).findall(source) for val in self.firstnames_list if bool(re.search(val, source))]
        # Sometimes there is a match but its not actually a real name ("Marc"h / "Max"imum) so we remove empty strings (
        firstnames_found = [elt[0].strip() for elt in firstnames_found if elt]

        # Retrieve the full names by matching the firstname and following last name (assuming they are next to each other)
        # The case where the last name preceeds the firstname is not taken into consideration and should be developed later
        if firstnames_found:
            self.ordered_firstnames = self.sort_firstnames(source, firstnames_found)
            print(self.ordered_firstnames)
            fullnames_found = [self.fullname_pattern(x).findall(source) for x in self.ordered_firstnames]
            self.ordered_fullnames = [elt[0] for elt in fullnames_found if elt]

            # Get the lastname from the fullname and also drop any firstnames that did not match a last name and return a list of firstnames and lastnaems
            if self.ordered_fullnames:
                self.page_contacts_firstnames, self.page_contacts_lastnames = self.get_lastnames_meth1()

            # If the previous method to find fullnames doesnt work: find the class of the firstname and look for the last name in siblings/children
            else:
                #  We first retrieve the class of the firstnames (firstnames without a class have been removed)
                # For each unique class_name (usually_one), look for siblings/children/parents
                self.page_contacts_firstnames, self.page_contacts_lastnames = self.get_lastnames_meth2(self.ordered_firstnames)

        else:
            self.page_contacts_firstnames = []
            self.page_contacts_lastnames = []
        
        return (self.page_contacts_firstnames, self.page_contacts_lastnames)



    def page_has_loaded(self):
        print("Checking if {} page is loaded.".format(self.driver.current_url))
        page_state = self.driver.execute_script('return document.readyState;')
        return page_state == 'complete'



    def parse_website(self, url, company_name=None, company_field=None, company_city=None):
        '''
        :param url: url link of the website to parse. The link should redirect to the home page of the website
        :return:  a dataframe of the contacts retrieved
        '''

        print('START parsing new website: {}'.format(url))
        # Init the list that will receive contacts and companys info
        self.init_lists()


        # Open the website page in a new tab and parse the website
        self.access_in_new_tab(url)

        # Initiate the company name and field of activity
        self.company_name = company_name
        self.company_field = company_field
        if company_city:
            self.company_city = company_city if not pd.isna(company_city) else ''


        # Look for any contact or team links and add them to pages
        self.pages = [url]

        # try:
        #     WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
        #     print("Page is ready!")
        #     self.pages.extend(self.get_contact_links()) if self.get_contact_links() else None
        # except TimeoutException:
        #     print("Loading took too much time!")

        if self.page_has_loaded():
            self.pages.extend(self.get_contact_links()) if self.get_contact_links() else None



        # For each page retrieve get all emails and phones found, and find contacts with associates phone or email
        for page in self.pages:
            try:
                self.parse_page(page)
            except:
                continue

        # Get the email with the highest occurence and set it as the company_email
        self.get_company_email_and_phone()

        # Create a contact dict to remove dupliactes in name and emails
        contact_dict = {
            'contact_firstname': self.website_contacts_firstnames,
            'contact_lastname': self.website_contacts_lastnames,
            'contact_email': self.website_contacts_emails,
            'contact_phone': self.website_contacts_phones
        }
        # Create a data frame from the dict and drop dupliactes
        contact_df = pd.DataFrame({key: pd.Series(value) for key, value in contact_dict.items()})
        contact_df = contact_df.drop_duplicates(subset=['contact_firstname', 'contact_lastname', 'contact_email'], keep='first')

        # Reassign the new lists of contacts' infos
        self.website_contacts_firstnames = contact_df['contact_firstname'].to_list()
        self.website_contacts_lastnames = contact_df['contact_lastname'].to_list()
        self.website_contacts_emails = contact_df['contact_email'].to_list()
        self.website_contacts_phones = contact_df['contact_phone'].to_list()
        print('Final firstnames:{}'.format(self.website_contacts_firstnames))

        # Get job_position and linkedin_url for each website's contact found
        print("Retrieving Contact's jobs positions and linkedin urls")
        self.get_linkedin_infos()


        # Creata a company dict
        website_dict = {
            'company_name': self.company_name,
            'company_address': [],
            'company_postalcode': [],
            'company_city': [],
            'company_phone': self.company_phone,
            'company_email': self.company_email,
            'company_website': [url],
            'contact_firstname': self.website_contacts_firstnames,
            'contact_lastname': self.website_contacts_lastnames,
            'contact_email': self.website_contacts_emails,
            'contact_phone': self.website_contacts_phones,
            'contact_position': self.website_contacts_position,
            'contact_linkedin': self.website_contacts_linkedin
        }
        # Create a data frame from the dict and clean it
        self.website_df = pd.DataFrame({key: pd.Series(value) for key, value in website_dict.items()})

        # Drop rows having no email, no phone, no linkedin
        self.website_df = self.website_df.loc[~(pd.isna(self.website_df.contact_email) & pd.isna(self.website_df.contact_phone) & pd.isna(self.website_df.contact_linkedin)), :]

        # Replace NA for company phone and company email (make sure to have at least one row)
        self.website_df[['company_phone', 'company_email', 'company_website']] = self.website_df[['company_phone', 'company_email', 'company_website']].fillna(method='ffill')

        # Assgin company name, phone and email
        if not self.website_df.empty:
            self.website_df[['company_name']] = self.company_name
            self.website_df[['company_email']] = self.company_email
            self.website_df[['company_phone']] = self.company_phone
        else:
            self.website_df.loc[0, 'company_name'] = self.company_name
            self.website_df.loc[0, 'company_email'] = self.company_email
            self.website_df.loc[0, 'company_phone'] = self.company_phone

        print('END: Parsing website')
        while len(self.driver.window_handles) > 2:
            self.close_current_tab()

        # print(self.website_df.iloc[:, -5:])
        return self.website_df



    def parse_page(self, page):
        '''
            A generic method for parsing a page
        '''

        source, pretty_soup = self.access_url(page)

        # Parse the page and return all the emails and phones found
        self.page_emails = self.get_emails(source)
        self.page_phones = self.get_phones(source)
        # Add them to websites all emails
        self.website_emails.extend(self.page_emails)
        self.website_phones.extend(self.page_phones)

        # Retrieve the contacts firstnames and lastnames
        print("Retrieving Contact's names")
        self.get_contacts_names(source)
        # Add them to website all firstnames and lastnames
        self.website_contacts_firstnames.extend(self.page_contacts_firstnames)
        self.website_contacts_lastnames.extend(self.page_contacts_lastnames)

        # Condition to avoid parsing info when there is no name:
        if self.page_contacts_firstnames:
            # Search for contact's emails and phones
            print("Retrieving Contact's emails and phones")
            self.get_contacts_emails_and_phones()
            self.website_contacts_emails.extend(self.page_contacts_emails)
            self.website_contacts_phones.extend(self.page_contacts_phones)

        return 0



    def get_company_email_and_phone(self):
        self.company_email = [list(Counter(self.website_emails).keys())[0]] if self.website_emails else None
        # Same as above but for the phones
        self.company_phone = [list(Counter(self.website_phones).keys())[0]] if self.website_phones else None

        return 0


    def get_contacts_emails_and_phones(self):
        '''
        Look for the closest email/phone after and before the firstname, then choose the info having the shortest distance from the name
        :return: a list containing 2 dict (one containing the infos found before the name, the other containing the infos found after)
        '''
        scraper = self
        source = scraper.driver.page_source
        # before = {'email_position': 'before'}
        # after = {'email_position': 'after'}

        # START EMAILS
        # Return two lists of match object for emails found after the firstnames and emails found before
        pattern = scraper.email_pattern
        emails_after = [pattern(firstname, True).search(source) for firstname in scraper.page_contacts_firstnames]
        emails_before = [pattern(firstname, False).search(source) for firstname in scraper.page_contacts_lastnames]

        # Measure the distance btw the name and each email match (for both email found before and after) and compute the average
        dist_after = [elt.span()[1]-elt.span()[0] for elt in emails_after if elt]
        avg_dist_after = np.average(dist_after) if dist_after else 1000
        dist_before = [elt.span()[1]-elt.span()[0] for elt in emails_before if elt]
        avg_dist_before = np.average(dist_before) if dist_before else 1000

        # Keep the emails with the lowest distance from the name
        if avg_dist_before >= avg_dist_after:
            scraper.page_contacts_emails = [elt.groups(1) if elt else None for elt in emails_after]
        else:
            scraper.page_contacts_emails = [elt.groups(1) if elt else None for elt in emails_before]
        # END EMAILS


        # START PHONES
        # A list of match object from regex. For each name in firstnames, look for any string that matches a phone pattern after or before the name
        pattern = scraper.phone_pattern
        phones_after = [pattern(firstname, True).search(source) for firstname in scraper.page_contacts_firstnames]
        phones_before = [pattern(firstname, False).search(source) for firstname in scraper.page_contacts_firstnames]

        # Measure distance
        dist_after = [elt.span()[1]-elt.span()[0] for elt in phones_after if elt]
        avg_dist_after = np.average(dist_after) if dist_after else 1000
        dist_before = [elt.span()[1]-elt.span()[0] for elt in phones_before if elt]
        avg_dist_before = np.average(dist_before) if dist_before else 1000

        # Kepp the phones with the lowest distance from the names
        if avg_dist_before >= avg_dist_after:
            scraper.page_contacts_phones = [elt.groups(1) if elt else None for elt in phones_after]
        else:
            scraper.page_contacts_phones = [elt.groups(1) if elt else None for elt in phones_before]

        return scraper.page_contacts_emails, scraper.page_contacts_phones



    def get_linkedin_infos(self):

        scraper = self
        firstnames = scraper.website_contacts_firstnames
        lastnames = scraper.website_contacts_lastnames

        # Open a new tab for google searches
        scraper.access_in_new_tab('https://www.google.fr')
        # scraper.access_in_new_tab('https://www.ecosia.org/?c=fr')

        try:
            # Google research to find linkedin url and position of company's contact
            if firstnames:
                results = [scraper.get_jobs_and_urls(firstname, lastname) for firstname, lastname in zip(firstnames, lastnames)]
                if not results[0]:
                    results = [scraper.get_jobs_and_urls(firstname, lastname, method2=True) for firstname, lastname in zip(firstnames, lastnames)]
                scraper.website_contacts_linkedin, scraper.website_contacts_position = list(zip(*results))[:2]
            else:
                results = scraper.get_jobs_and_urls()
                scraper.website_contacts_linkedin, scraper.website_contacts_position,  scraper.website_contacts_firstnames, scraper.website_contacts_lastnames = results
        except:
            print('Linkedin Error ! Change VPN')
            raise

        return 0


    def get_jobs_and_urls(self, firstname=None, lastname=None, method2=False):
        '''

        :param google_search:
        :return:
        '''
        scraper = self
        driver = scraper.driver

        # Define google research
        if firstname and lastname:
            if not method2:
                google_search = '"' + firstname + ' ' + lastname + '"' + ' ' + scraper.company_city + ' AND ' + scraper.company_field + ' site:linkedin.com'
            else:
                google_search = '"' + firstname + ' ' + lastname + '"' + ' AND ' + scraper.company_field + ' site:linkedin.com'
        else:
            google_search = '"' + scraper.company_name + '"' + ' ' + scraper.company_city + ' AND (PDG OR Gérant) OR (Manager OR Chef) OR (Directeur OR Responsable) site:linkedin.com'

        # Run the research
        search_input = driver.find_element_by_name("q")
        # Function to enter text 'slowly'
        # for c in google_search:
        #     endtime = time.time() + 0.02
        #     time.sleep(endtime - time.time())
        #     search_input.send_keys(c)
        search_input.send_keys(google_search)
        search_input.send_keys(Keys.RETURN)
        search_input = driver.find_element_by_name("q")
        search_input.clear()

        linkedin_links = driver.find_elements_by_class_name("r")
        temp_firstname = []
        temp_lastname = []
        temp_url = []
        temp_position = []

        for link in linkedin_links:
            link_url = link.find_element_by_css_selector('[href]').get_attribute('href')
            link_title = link.find_element_by_tag_name('h3').text
            # print(link_title)

            # Go to the next link should the link url contain 'job' or 'dir'
            if bool(re.search(r'jobs|dir', link_url)):
                continue

            # Extract the first name and the last name from the link title
            if len(link_title.split('-')[0].strip().split(' ')) == 2:
                title_firstname, title_lastname = link_title.split('-')[0].strip().split(' ')
            else:
                 continue

            # Save temporary name and temporary position
            temp_firstname.append(link_title.split('-')[0].strip().split(' ')[0])
            temp_lastname.append(link_title.split('-')[0].strip().split(' ')[1])
            temp_url.append(link_url)
            temp_position.append(link_title.split('-')[1].strip() if len(link_title.split('-')) < 3 else None)

            # Check that the names in the link tile matches the contact's name
            if firstname and lastname:
                if not firstname == title_firstname or not lastname == title_lastname:
                    continue

            # Extract the job position if there is one
            if len(link_title.split('-')) < 3:
                return (link_url, None, title_firstname, title_lastname)
            else:
                contact_position = link_title.split('-')[1].strip()
                return (link_url, contact_position, title_firstname, title_lastname)

        # Return a temporary contact tupple if nothing found in any link or None
        if not method2:
            return (None, None, None, None)
        else:
            return (temp_url[0], temp_position[0], temp_firstname[0], temp_lastname[0]) if temp_url else (None, None, None, None)




    def get_contact_links(self):
        '''
            :return: a list of contact links
        '''
        scraper = self
        driver = scraper.driver
        # Try to get a link that contains 'Contact' in its href attribute

        # results = driver.find_elements_by_css_selector("a[href*='contact']")
        # if len(results) > 0:
        #     contact_links = [result.get_attribute('href') for result in results]

        # If not contact link found from the first method, retrieve all the links in the page and match only the links having Contact in their text
        links = driver.find_elements_by_css_selector("a")
        # regex to match url containing keyword with a probability to redirect to a page with contact information


        links = [link.get_attribute('href') for link in links if link]
        unique_links = list(dict.fromkeys(links))
        unique_links = [link for link in unique_links if bool(re.search(r'http', str(link)))]
        pattern = re.compile('(?://).*/.*(?:contact|team|equipe).*', re.IGNORECASE) # we removed 'agence' from url as most of them contains that word
        contact_links = [elt for elt in unique_links if pattern.search(str(elt))]
        # If not results from the previous method take the link if a keyword is within the text description
        if not contact_links:
            links = driver.find_elements_by_css_selector("a")
            pattern = re.compile('(?://).*/.*(?:contact|agences?|team|equipe).*', re.IGNORECASE)
            contact_links = [result.get_attribute('href') for result in links if bool(pattern.search(result.text))]

        contact_links_list = list(dict.fromkeys(contact_links))
        return contact_links_list



    def get_team_links(self):
        '''
            :return: a list of links about the team
        '''
        driver = self.driver
        results = driver.find_elements_by_css_selector("a[href*='team'")
        if len(results) == 0:
            results = driver.find_elements_by_css_selector("a[href*='equipe")
        if len(results) > 0:
            team_links = [elt.get_attribute('href') for elt in results]
        else:
            results = driver.find_elements_by_css_selector("a")
            pattern = re.compile('.*(?:equipe|team).*', re.IGNORECASE)
            team_links = [result.get_attribute('href') for result in results if bool(pattern.search(result.text))]

        team_links_list = list(Counter(team_links).keys())
        return team_links_list


    def retrieve_firstname_class(self, first_name):
        """
        Retrieve the class of the element containing the firstname.
        Remove the firstname where no class is found
        """
        driver = self.driver

        # Find the class of element that contains the firstname using xpath (method 1)
        print('Looking for name:{}'.format(first_name))
        elt = driver.find_element_by_xpath("//*[contains(text(),'{}')]".format(first_name))
        name_class = elt.get_attribute('class')

        return name_class



    def sort_firstnames(self, source, actual_firstnames):
        # Attribute to each name the position of its first character then sort using merge_sort algorithm
        pos_list = []
        for name in actual_firstnames:
            p = re.compile(name)
            # the position of the starting char is retrieved using span method on re.search
            start_pos = p.search(source).span()[0]
            pos_list.append([name, start_pos])
        # Return a list of name as they appears in order in the website (if more than 1 elt)
        if len(pos_list) > 1:
            firstnames_sorted = [elt[0] for elt in self.merge_sort(pos_list)]
            return firstnames_sorted
        return [pos_list[0][0]] # return a list obect if only one result because the result will be 'extended' to a list later



    def merge_sort(self, arr):
        if len(arr) > 1:
            mid = len(arr) // 2  # Finding the mid of the array
            L = arr[:mid]  # Dividing the array elements
            R = arr[mid:]  # into 2 halves

            self.merge_sort(L)  # Sorting the first half
            self.merge_sort(R)  # Sorting the second half

            i = j = k = 0

            # Copy data to temp arrays L[] and R[]
            while i < len(L) and j < len(R):
                if L[i][1] < R[j][1]:  # working with list of list
                    arr[k] = L[i]
                    i += 1
                else:
                    arr[k] = R[j]
                    j += 1
                k += 1

            # Checking if any element was left
            while i < len(L):
                arr[k] = L[i]
                i += 1
                k += 1

            while j < len(R):
                arr[k] = R[j]
                j += 1
                k += 1
            return arr



