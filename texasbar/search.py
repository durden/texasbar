#!/usr/bin/env python

"""
Module to provide a quick interface to getting law alumni from a particular
school and living in a given city.
"""

import re
import sys

import requests
from BeautifulSoup import BeautifulSoup


class Person(object):
    """person container"""

    def __init__(self, name, websites):
        """init"""

        self.name = name
        self.websites = websites

    def __str__(self):
        """str"""

        sites = ''
        for site in self.websites:
            if site is not None:
                sites = ' '.join([site])

        return '%s, %s' % (self.name, sites)


def _get_number_of_pages(url, query_string, data):
    """Get the number of pages results will yield"""

    resp = requests.post(''.join([url, query_string]), data=data)
    if resp.status_code != 200:
        print 'Error getting html code: %s' % (resp.status_code)
        return 0

    html_soup = BeautifulSoup(resp.content)
    pages = html_soup.findAll('span', {'class': 'pagenumber'})

    return int(list(pages)[-1].text)


def _get_html():
    """Get html results page by page"""

    max_per_page = 25

    url = 'http://www.texasbar.com/AM/Template.cfm'
    query_string = '?Section=Find_a_Lawyer&Template=/CustomSource/MemberDirectory/Result_form_client.cfm'
    data = {'State': 'TX', 'Submitted': 1, 'PPlCityName': 'Houston',
            'LawSchool': 6, 'ShowPrinter': 1, 'MaxNumber': max_per_page}

    max_page = _get_number_of_pages(url, query_string, data) + 1

    for page in xrange(1, max_page):

        print 'Getting page', page, 'of', max_page

        next_result_idx = max_per_page * (page - 1)
        if next_result_idx > 0:
            # Yes, their code uses page like this...
            data['ButtonName'] = 'Page'
            data['Page'] = next_result_idx + 1
            data['Next'] = next_result_idx + 1

        resp = requests.post(''.join([url, query_string]), data=data)
        if resp.status_code != 200:
            print 'Error getting html code: %s' % (resp.status_code)
            return

        yield resp.content


def _get_people(html):
    """Get a list of people from given html"""

    return html.findAll('div', {'class': 'search-result'})


def _get_full_name(person):
    """Get full name as a string from given person"""

    # For whatever weird reason some of the html can have multiple given names
    # etc. for a single person..

    first_names = person.findAll('span', {'class': 'given-name'})
    first_names = ' '.join([name.text for name in first_names])

    middle_names = person.findAll('span', {'class': 'additional-name'})
    middle_names = ' '.join([name.text for name in middle_names])

    last_names = person.findAll('span', {'class': 'family-name'})
    last_names = ' '.join([name.text for name in last_names])

    full_name = ' '.join([first_names, middle_names, last_names])

    # Remove any duplicate spaces
    return re.sub(' +', ' ', full_name)


def _get_website(person):
    """Get website from person"""

    sites = []
    links = person.findAll('a', target="_blank")

    for link in links:
        href = link.attrs[0][1]

        if href.startswith('http:'):
            sites.append(href)

    return sites


def search(output):
    """Search for attorneys and write to output stream"""

    for page in _get_html():
        html_soup = BeautifulSoup(page)

        people = []
        for human in _get_people(html_soup):
            person = Person(_get_full_name(human), _get_website(human))
            people.append(person)

        for human in people:
            output.write('%s\n' % (human))


if __name__ == "__main__":
    import argparse

    # FIXME: Add option for city name, law school, state

    parser = argparse.ArgumentParser(
                        description='Search texasbar.com for attorneys')
    parser.add_argument('--log', default=sys.stdout,
                        type=argparse.FileType('w'),
                        help='Optional file to write results')
    args = parser.parse_args()

    search(args.log)
