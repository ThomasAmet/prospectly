import os
import re
import pandas as pd
from collections import Counter
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

abspath = os.path.abspath(__file__)
dirname = os.path.dirname(abspath)
os.chdir(dirname)

input_path = os.path.join('..', 'input')
firstnames_df = pd.read_csv(os.path.join(input_path, 'nat2018.csv'), sep=';', header=0)

firstnames_list = firstnames_df.iloc[:3000, 0].values.tolist()
firstnames_list = list(map(lambda x: x.capitalize(), firstnames_list)) #map a capitlize function to initial list
firstnames_list.append('Abby')


class Scraper:

    def __init__(self, driver_path, driver_options, url):
        self.driver = webdriver.Chrome(driver_path, options=driver_options)
        self.firstnames_list = firstnames_list
        self.all_emails = []
        self.all_phones = []
        self.contact_links = []
        self.team_links = []
        self.company_email = []
        self.company_phone = []
        self.company_site = []
        self.company_facebook = []
        self.company_instagram = []
        self.company_linkedin = []
        self.contacts_firstnames = []
        self.contacts_lasttnames = []
        self.contacts_emails = []
        self.contacts_phones = []
        self.contacts_linkedins = []
        self.temp_emails = []
        self.temps_phones = []



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


    def get_seq_page_number(self):
        # Set the number of page to go through
        max_page_number = int(self.driver.find_element_by_class_name('last').find_element_by_css_selector('a').get_attribute('data-page'))
        seq_pages = [i + 1 for i in range(int(max_page_number))]
        return seq_pages


    def firstname_pattern(x):
        '''
            This pattern return a list of actual firstnames found on specific page (works on both test pages)
        '''
        # return re.compile('([\w-]*' + x + ')[<\s]') # Will allow names like Jean-Marie-Emmanuel (unlikely) but accept cities like Bussy-Saint-Antoine
        return re.compile('((?:[\w]*[-]){0,1}' + x + ')[<\s]')


    def fullname_pattern(x):
        '''
        This pattern get the full names from a first name
        :param x:
        :return: Matching string that contains a name x and:
            - which might be preceeded by another word separated by a dash (to handle names like Pierre-Marie if not in list of names)
            - which might be followed by a separation particule + a string containing only letters (to match for ex Paul de Sauvage)
            - that end with a string containing only letters followed by a any space (tab,space,newline etc.) or a closing tag
        '''
        # return re.compile("((?:[A-z]+?-)" + x + "(?:de |d'|le|l'|du|de la| )[A-z ]+)[<\s]") #old one, that works, to keep in case
        return re.compile("(" + x + "(?:de|d'|le|l'|du|de la|Da| )*[A-z]+?)[<\s$]")



    def email_pattern(self):
        email_pattern = '[\w.-]+?@[\w.-]+?\.[\w]+'
        return re.compile(email_pattern)



    def phone_pattern(self, var, after=True):
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
        phone_pattern = '((?:\+\d{2}[-.\s]?(?:\(0\)|0)*?[-.\s]?|00[-.\s]?\d{2}[-.\s]?(?:\(0\)|0)*?[-.\s]?|0)\d?[-.\s]?(?:\d{2}[-.\s]?){3,4})(?:$|\D)'
        # This version even take into consideration phone number in Luxembourg
        phone_pattern = '((?:\+\d{2}[-.\s]?(?:\(0\)|0)*?[-.\s]?|00[-.\s]?\d{2}[-.\s]?(?:\(0\)|0)*?[-.\s]?|0)\d?[-.\s]?\d{2,3}[-.\s]?(?:\d{2}[-.\s]?){2,3})(?:$|\D)'
        non_capturing_pattern = '(?:\+\d{2}[-.\s]?(?:\(0\)|0)*?[-.\s]?|00[-.\s]?\d{2}[-.\s]?(?:\(0\)|0)*?[-.\s]?|0)\d?[-.\s]?\d{2,3}[-.\s]?(?:\d{2}[-.\s]?){2,3}(?:$|\D)'

        if not var:
            return re.compile(phone_pattern)
        else:
            if after:
                return re.compile(var + '.*?' + phone_pattern)
            else:

                return re.compile('\b(' + non_capturing_pattern + ')(?:(?!' + non_capturing_pattern + ').)*?\b' + var + r'\b')



    def get_lastnames_meth1(self, firstnames, fullnames):
        '''
        Retrieve lastname from firstname, if no lastname is found, we remove firstnames from the list
        Ex: print(get_family_names(actual_firstnames, actual_fullnames))
        '''
        if len(firstnames) == len(fullnames):
            lastnames = [re.split(firstname, fullname)[1] for firstname, fullname in zip(firstnames, fullnames)]
        else:
            # if diff length btw fullnames and firstnames, remove firstnames that are not in fullnames
            for fullname in fullnames:
                [firstnames.remove(firstname) for firstname in firstnames if  not bool(re.search(firstname, fullname))]
            # once both list are with the same length we retrieve the lastname
            lastnames = [re.split(firstname, fullname)[1] for firstname, fullname in zip(firstnames, fullnames)]

        return firstnames, lastnames



    def get_lastnames_meth2(self, firstnames_classes):
        '''
                For each unique class_name (usually_one):
                Retrieve text in siblings, child and parents, going to the next method if the previous one failed.
                The methods are sorted by decreasing order of the odds of yielding a result
        '''
        for class_name in firstnames_classes:
            # Find the class of firstnames following siblings and access their text
            xpath = "//*[@class='{}']//following-sibling::*".format(class_name)
            after_siblings = self.driver.find_elements_by_xpath(xpath)
            last_names = [sibling.text for sibling in
                          after_siblings]  # last_name are return by order of appearance in the page

            if not last_names:
                # Find the class of firstnames preceding siblings and access their text
                xpath = "//*[@class='{}']//preceding-sibling::*".format(class_name)
                before_siblings = self.driver.find_elements_by_xpath(xpath)
                last_names = [sibling.text for sibling in before_siblings]

            if not last_names:
                # Find the class of firstnames' children
                xpath = "//*[@class='{}']//child::*".format(class_name)
                children = self.driver.find_elements_by_xpath(xpath)
                last_names = [child.text for child in children]

            if not last_names:
                # Find the class of firstname's parent and access its text (might return the full name !! To be checked)
                # xpath = "//*[@class='{}']//parent::*".format(class_name)
                xpath = "//*[@class='{}']/..".format(class_name)
                parents = self.driver.find_elements_by_xpath(xpath)
                last_names = [parent.text for parent in parents]

        return last_names

    def parse_website(self, url):
        '''
        :param url: url link of the website to parse. The link should redirect to the home page of the website
        :return:  a dataframe of the contacts retrieved
        '''
        return
    def parse_page(self, source):
        '''
            A generic method for parsing a page
        '''

        return

    def parse_contacts_names(self, source):
        # Retrieve the firstname whenever there is a match
        firstnames_found = [self.firstname_pattern(val).findall(source) for val in self.firstnames_list if
                            bool(re.search(val, source))]
        # Sometimes there is a match but its not actually a real name ("Marc"h / "Max"imum) so we remove empty strings (
        actual_firstnames = [elt[0].strip() for elt in firstnames_found if elt]

        # Retrieve the full names by matching the firstname and following last name (assuming they are next to each other)
        # The case where the last name preceeds the firstname is not taken into consideration and should be developed later
        if actual_firstnames:
            ordered_firstnames = self.sort_firstnames(source, actual_firstnames)
            fullnames_found = [self.fullname_pattern(x).findall(source) for x in ordered_firstnames]
            ordered_fullnames = [elt[0] for elt in fullnames_found if elt]

            # Get the lastname from the fullname and also return firstnames without the names that did not match a last name
            if len(ordered_fullnames) > 0:
                ordered_firstnames, ordered_lastnames = self.get_lastnames_meth1(ordered_firstnames, ordered_fullnames)

            # If the previous method to find lastnames doesnt work: find the class of the firstname and look for siblings/children
            else:
                #  We first retrieve the class of the firstnames (firstnames without a class have beem removed)
                ordered_firstnames, firstnames_classes = self.retrieve_firstnames_classes(source, ordered_firstnames)

                # For each unique class_name (usually_one), look for siblings/children/parents
                ordered_lastnames = self.get_lastnames_meth2(firstnames_classes)

            return (ordered_firstnames, ordered_lastnames)

        else:
            return None, None


    def find_contact_links(self):
        '''
            :return: a list of contact links
        '''
        driver = self.driver
        # Try to get a link that contains 'Contact' in its href attribute
        results = driver.find_elements_by_css_selector("a[href*='contact']")
        if len(results) > 0:
            contact_links = [result.get_attribute('href') for result in results]

        # If not contact link found from the first method, retrieve all the links in the page and match only the links having Contact in their text
        else:
            results = driver.find_elements_by_css_selector("a")
            pattern = re.compile('.*contact.*', re.IGNORECASE)
            contact_links = [result.get_attribute('href') for result in results if
                             bool(pattern.search(result.text))]
        contact_links_list = list(Counter(contact_links).keys())
        return contact_links_list


    def find_team_links(self):
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


    def retrieve_firstnames_classes(self, source, ordered_firstnames):
        """
        Retrieve the class of the element containing the firstname.
        Remove the firstname from the firstnames list if no class is found
        """
        driver = self.driver
        classes_names = []
        # Find the class of element that contains the firstname using xpath (method 1)
        for name in ordered_firstnames:
            print('Looking for name:{}'.format(name))
            elt = driver.find_element_by_xpath("//*[contains(text(),'{}')]".format(name))
            name_class = elt.get_attribute('class')
            # Remove the firstnames without a class
            if not name_class:
                ordered_firstnames.remove(name)
            else:
                classes_names.append(name_class)

        firstnames_classes = list(Counter(classes_names).keys())
        return ordered_firstnames, firstnames_classes


    def sort_firstnames(self, source, actual_firstnames):
        # Attribute to each name the position of its first character then sort using merge_sort algorithm
        pos_list = []
        for name in actual_firstnames:
            p = re.compile(name)
            # the position of the starting char is retrieved using span method on re.search
            start_pos = p.search(source).span()[0]
            pos_list.append([name, start_pos])
        # Return a list of name as they appears in order in the website
        firstnames_sorted = [elt[0] for elt in self.merge_sort(pos_list)]
        return firstnames_sorted



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



