# Good sources for css
# https://chercher.tech/python/css-selector-selenium-python
# https://saucelabs.com/resources/articles/selenium-tips-css-selectors
# https://www.geeksforgeeks.org/extracting-email-addresses-using-regular-expressions-python/
# https://www.geeksforgeeks.org/regular-expressions-python-set-1-search-match-find/


import os
import re
import pandas as pd
import numpy as np
from collections import Counter
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# This takes the filename of your script, converts it to an absolute path, then extracts the directory of that path, then changes into that directory.
abspath = os.path.abspath(__file__)
dirname = os.path.dirname(abspath)
os.chdir(dirname)

input_path = os.path.join('..', 'input')
driver_path = os.path.join('..', 'drivers', 'chromedriver')
driver_options = Options()
driver_options.add_argument('--incognito')
driver = webdriver.Chrome(driver_path, options=driver_options)

firstnames_df = pd.read_csv(os.path.join(input_path, 'nat2018.csv'), sep=';', header=0)
firstnames_list = firstnames_df.iloc[:3000, 0].values.tolist()
firstnames_list = list(map(lambda x: x.capitalize(), firstnames_list)) #map a capitlize function to initial list
firstnames_list.append('Abby')


url = 'http://www.immobilieres-agences.fr/'
sub_url = 'https://www.actibel.be/contact/'
sub_url = 'https://www.confiance.lu/equipe/'
sub_url = 'https://boissy-saint-leger.coteparticuliers.com/'
driver.get(sub_url)

#######################################
# IMPORTED IN SCRAPER
#######################################
def merge_sort(arr):
    '''
    :param arr: an array of firstnames for example
    :return:
    '''
    if len(arr) > 1:
        mid = len(arr) // 2  # Finding the mid of the array
        L = arr[:mid]  # Dividing the array elements
        R = arr[mid:]  # into 2 halves

        merge_sort(L)  # Sorting the first half
        merge_sort(R)  # Sorting the second half

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

#######################################
# IMPORTED IN SCRAPER
#######################################
def get_in_new_tab(link):
    # Open the link in a new tab do some stuff
    driver.execute_script("window.open('');")
    tabs = driver.window_handles  # all_tabs
    driver.switch_to.window(tabs[-1])  # switch to last active tab
    driver.get(link)
    soup = BeautifulSoup(driver.page_source, features="html.parser")

    return (driver.page_source, soup)

# driver.execute_script("window.open('https://www.google.fr');")

#######################################
# IMPORTED IN SCRAPER
#######################################
def get_contact_links():
    '''
    :return: a list of contact links
    '''
    # Try to get a link that contains 'Contact' in its href attribute
    results = driver.find_elements_by_css_selector("a[href*='contact']")
    if len(results) > 0:
        contact_links = [result.get_attribute('href') for result in results]

    # If not contact link found from the first method, retrieve all the links in the page and match only the links having Contact in their text
    else:
        results = driver.find_elements_by_css_selector("a")
        pattern = re.compile('.*contact.*', re.IGNORECASE)
        contact_links = [result.get_attribute('href') for result in results if bool(pattern.search(result.text))]

    return list(Counter(contact_links).keys())


#######################################
# IMPORTED IN SCRAPER
#######################################
def get_team_links():
    results = driver.find_elements_by_css_selector("a[href*='team'")
    if len(results) == 0:
        results = driver.find_elements_by_css_selector("a[href*='equipe")
    if len(results) > 0:
        team_links = [elt.get_attribute('href') for elt in results]
    else:
        results = driver.find_elements_by_css_selector("a")
        pattern = re.compile('.*(?:equipe|team).*', re.IGNORECASE)
        team_links = [result.get_attribute('href') for result in results if bool(pattern.search(result.text))]

    return list(Counter(team_links).keys())


# Parse the home page for infos
source = driver.page_source
soup = BeautifulSoup(source, features="html.parser")
# Parse all the contact pages found to retrieve infos
if len(contact_links) > 0:
    for link in contact_links:
        try:
            source, soup = get_in_new_tab(link.get_attribute('href'))
        except:
            print('No href attributes')


    #######################################
    # IMPORTED IN SCRAPER
    #######################################
    def firstname_pattern(x):
        '''
            his pattern return a list of actual firstnames found on specific page (works on both test pages)
        '''
    # return re.compile('([\w-]*' + x + ')[<\s]') # Will allow names like Jean-Marie-Emmanuel (unlikely) but accept cities like Bussy-Saint-Antoine
        return re.compile('((?:[\w]*[-]){0,1}' + x + ')[<\s]')


    #######################################
    # IMPORTED IN SCRAPER
    #######################################
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


    def get_family_names(firstnames, fullnames):
        '''
        Ex: print(get_family_names(actual_firstnames, actual_fullnames))
        '''
        lastnames = [re.split(firstname, fullname)[1] for firstname, fullname in zip(firstnames, fullnames)]
        return lastnames



    # Retrieve the full firstname whenever there is a match
    firstnames_found = [firstname_pattern(val).findall(source) for val in firstnames_list if bool(re.search(val, source))]
    # Sometimes there is a match but its not actually a real name ("Marc"h / "Max"imum) so we remove empty strings (
    actual_firstnames = [elt[0] for elt in firstnames_found if elt]
    if actual_firstnames:
        ordered_firstnames = sort_firstnames(actual_firstnames, source)

    print(ordered_firstnames)


    # Retrieve the full names by matching the firstname and following last name
    fullnames_found = [fullname_pattern(x).findall(source) for x in actual_firstnames]
    actual_fullnames = [elt[0] for elt in fullnames_found if elt]
    print(actual_fullnames)



    # Another method for finding the last name if the previous one doesnt work: find the class of the firstname and look for siblings/children
    firstnames_classes = []
    # Find the class of element that contains the firstname using xpath (method 1)
    for name in actual_firstnames:
        print('Looking for name:{}'.format(name))
        elt = driver.find_element_by_xpath("//*[contains(text(),'{}')]".format(name))
        name_class = elt.get_attribute('class')
        firstnames_classes.append(name_class)

    # Find the class of element that contains the firstname using regex (method 2) in case method 1 fails
    if len(firstnames_classes) == 0:
        for name in actual_firstnames:
            # If a match is found, store the class in a list to retrieve
            if bool(re.search(r'class="(.+)".*' + name, source)):
                name_class = re.search(r'class="(.+)".*' + name, source).groups()[0]
                firstnames_classes.append(name_class)

    # For each unique class_name (usually_one):
    # Retrieve text in siblings, child and parents, going to the next method if the previous failed, sorted by chance of yielding a result
    for class_name, occurence in Counter(firstnames_class).items():

        # Find the class of firstnames following siblings and access their text
        xpath = "//*[@class='{}']//following-sibling::*".format(class_name)
        after_siblings = driver.find_elements_by_xpath(xpath)
        last_name = [sibling.text for sibling in after_siblings] # last_name are return by order of appearance in the page


        # Find the class of firstnames preceding siblings and access their text
        xpath = "//*[@class='{}']//preceding-sibling::*".format(class_name)
        pre_siblings = driver.find_elements_by_xpath(xpath)
        for sibling in pre_siblings:
            print(sibling.text)

        # Find the class of firstnames' children
        xpath = "//*[@class='{}']//child::*".format(class_name)
        children = driver.find_elements_by_xpath(xpath)
        for child in children:
            print(child.text)

        # Find the class of firstname's parent and access its text (might return the full name)
        # xpath = "//*[@class='{}']//parent::*".format(class_name)
        xpath = "//*[@class='{}']/..".format(class_name)
        parents = driver.find_elements_by_xpath(xpath)
        for parent in parents:
            print(parent.text)

    # Method to avoid as it depends on the person who coded the page
    # Find all element having a class that contains 'name'
    all = driver.find_elements_by_css_selector("*[class*='name']")
    for elt in all:
        print(elt.get_attribute('class'))


    # Phone numbers
    def phone_pattern(var, after=True):
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
                return re.compile(name + '.*?' + phone_pattern)
            else:

                return re.compile('\b(' + non_capturing_pattern + ')(?:(?!' + non_capturing_pattern + ').)*?\b' + name + r'\b')


    def email_pattern():
        email_pattern = '[\w.-]+?@[\w.-]+?\.[\w]+'
        return re.compile(email_pattern)


    def get_surrounding_infos(actual_firstnames, searching_emails=True):
        # Look for the closest email/phone after and before the firstname, then choose the info having the shortest distance with the name
        before = {'email_position': 'before'}
        after = {'email_position': 'after'}
        for name in actual_firstnames:

            # full name followed by the email (after)
            # name_email = re.search(name + '.*?([A-z0-9_.-]+?@[A-z0-9_.-]+?\.[A-z]+)', source)
            if searching_emails:
                infos = re.search(name + '.*?([\w.-]+?@[\w.-]+?\.[\w]+)', source)
            else:
                infos = phone_pattern(var=name, after=True).search(source)
            if infos:
                after[name] = {}
                after[name]['email'] = infos.group(1)
                after[name]['distance'] = infos.span()[1] - infos.span()[0] # nb of char btw start and end of the match
                print('Email after "{}" firstname: {}'.format(name, infos.group(1)))

            # email/phone followed by full name, (before)
            if searching_emails:
                infos = re.search(r'\b([\w.-]+@[\w.-]+\.\w+)(?:(?![\w.-]+@[\w.-]+\.\w).)*?\b' + name + r'\b', source, re.S)
            else:
                infos = phone_pattern(var=name, after=False).search(source, re.S)
            if infos:
                before[name] = {}
                before[name]['email'] = infos.group(1)
                before[name]['distance'] = infos.span()[1] - infos.span()[0] # nb of char btw start and end of the match
                print('Email before "{}" keyword: {}'.format(name, infos.group(1)))

        # store and return the results of the 2 dict in a list
        associated_emails = [before, after]
        return associated_emails


    def associate_surrounding_infos(surrounding_infos, actual_firstnames):
        if len(surrounding_infos[0]) == len(surrounding_infos[1]):
            avg_dist_before = np.average([surrounding_infos[0].get(name).get('distance') for name in actual_firstnames])
            avg_dist_after = np.average([surrounding_infos[1].get(name).get('distance') for name in actual_firstnames])
            if avg_dist_before > avg_dist_after:
                # get emails or phone from after
                return surrounding_infos[1]
            else:
                # get emails or phone from before
                return surrounding_infos[0]
        else:
            if len(surrounding_infos[0]) > len(surrounding_infos[1]):
                # get emails or phone from before
                return surrounding_infos[0]
            else:
                # get emails or phone from after
                return surrounding_infos[1]




    # TEST
    source = "John Doe is part of our team and here is his email: johndoe@something.com. James Henry is also part of our team and here his email: jameshenry@something.com. Jane Doe is the team manager and you can contact her at that address: janedoe@something.com"

    for name in ['John', 'James', 'Jane']:
        # full name followed by the email
        name_email = re.search(name + '.*?([\w.-]+?@[\w.-]+?\.[\w]+)', source)
        if name_email:
            print('Email after "{}" keyword: {}'.format(name, name_email.group(1)))
        # email followed by full name
        email_name = re.search(r'\b([\w.-]+@[\w.-]+\.\w+)(?:(?![\w.-]+@[\w.-]+\.\w).)*?\b' + name + r'\b', source, re.S)
        if email_name:
            print('Email before "{}" keyword: {}'.format(name, email_name.group(1)))


    def sort_firstnames(actual_firstnames, source):
        # Attribute to each name the position of its first character then sort using merge_sort algorithm
        pos_list = []
        for name in actual_firstnames:
            p = re.compile(name)
            # the position of the starting char is retrieved using span method on re.search
            start_pos = p.search(source).span()[0]
            pos_list.append([name, start_pos])
        # Return a list of name as they appears in order in the website
        firstnames_sorted = [elt[0] for elt in merge_sort(pos_list)]
        return firstnames_sorted

    # TEST PHONE
    print(phone_pattern().findall('+352 32 81 73 1'))


    # TEST EMAILS
    # method 1
    print(re.findall(r'mailto:([A-z0-9_.-]+?@[A-z0-9_.-]+?\.[A-z]+)', soup.prettify()))
    # method 2
    print(re.findall('[A-z0-9_.-]+?@[A-z0-9_.-]+?\.[A-z]+', soup.prettify()))
    # method 3 (equivalent as above)
    print(re.findall('[\w.-]+?@[\w.-]+?\.[a-z]+', soup.prettify()))
    # method 4: find elt with class email and get the text attribute
    tests = driver.find_elements_by_css_selector("[class*='email']")
    [test.text for test in tests if bool(re.match(r'.+@.+', test.text))]

    # On home page look for any email and any phone and all contacts_link
    # If one unique email, assume that is the contact email if not unique email
    # Else count occurence and assume that the highest occurence is the contact email
        # If same number of occurence for each email then look for phone number
            # If unique, we assume that it is the contact phone
            # Else we count occurence in phone number and assume the highest occurence is the contact_phone
    #  and we consider the email which is the closest to the phone number as contact email (dev function to do that)

    # and store them respectively in company_phone and company_emails
    # if number of unique emails is greater than number of names found check if any emails match home page and remove it from the list
    # check also counter of eamils and assume the one with highest occurence is to be removed
    # if still there is a bigger number of emails (same if number is less):
    # we find the closest email before each name and compute the amount of character between name and email
    # do the same but looking for email after each names
    # it is safe to assume that whatever method yield the shortest amount of character between the name and the email is the correct one.
    # check against linkedin to find a profile
    # If not matches found with name regex ... check the div that contains the first name and get the text of previous div or next div and check if one of them starts with capital
    # Test the whole thing on 20 pages and look how much we miss


# To get the parents parent, call find(:xpath, '../..').


# source = driver.page_source
# # Beautiful soup example
# soup = BeautifulSoup(source, features="html.parser")
# # Get all links
# hrefs = soup.find_all('a', {'class':'liencat'})
# for href in hrefs:
#     print(href.get('href'))


