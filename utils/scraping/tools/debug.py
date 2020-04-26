import re

scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
source, pretty_soup = scraper.access_url(scraper.pages[0])
scraper.pages.extend(scraper.get_contact_links())

scraper.get_emails(source)
scraper.get_contacts_names(source)


def get_contacts_names(source):
    '''
    Look for all the firstnames in a page then look for a fullname (firstname + lastname).
    Finally return a list of firstnames and lastnames associated
    :param source:
    :return: 2 lists: firstnames, lastnames
    '''

    # Retrieve the firstname whenever there is a match and return a list
    firstnames_found = [scraper.firstname_pattern(val).findall(source) for val in scraper.firstnames_list if bool(re.search(val, source))]
    # Sometimes there is a match but its not actually a real name ("Marc"h / "Max"imum) so we remove empty strings (
    firstnames_found = [elt[0].strip() for elt in firstnames_found if elt]

    # Retrieve the full names by matching the firstname and following last name (assuming they are next to each other)
    # The case where the last name preceeds the firstname is not taken into consideration and should be developed later
    if firstnames_found:
        scraper.ordered_firstnames = scraper.sort_firstnames(source, firstnames_found)
        fullnames_found = [self.fullname_pattern(x).findall(source) for x in self.ordered_firstnames]
        self.ordered_fullnames = [elt[0] for elt in fullnames_found if elt]

        # Get the lastname from the fullname and also drop any firstnames that did not match a last name and return a list of firstnames and lastnaems
        if self.ordered_fullnames:
            self.page_contacts_firstnames, self.page_contacts_lastnames = self.get_lastnames_meth1()

        # If the previous method to find fullnames doesnt work: find the class of the firstname and look for the last name in siblings/children
        else:
            #  We first retrieve the class of the firstnames (firstnames without a class have been removed)
            # For each unique class_name (usually_one), look for siblings/children/parents
            self.page_contacts_firstnames, self.page_contacts_lastnames = self.get_lastnames_meth2(
                self.ordered_firstnames)

    else:
        self.page_contacts_firstnames = []
        self.page_contacts_lastnames = []

    return (self.page_contacts_firstnames, self.page_contacts_lastnames)




def sort_firstnames(self, source, firstnames_found):
    # Attribute to each name the position of its first character then sort using merge_sort algorithm
    pos_list = []
    for name in firstnames_found:
        print(name)
        p = re.compile(name)
        # the position of the starting char is retrieved using span method on re.search
        start_pos = p.search(source).span()[0]
        pos_list.append([name, start_pos])
    # Return a list of name as they appears in order in the website (if more than 1 elt)
    if len(pos_list) > 1:
        firstnames_sorted = [elt[0] for elt in self.merge_sort(pos_list)]
        return firstnames_sorted
    return [pos_list[0][0]]