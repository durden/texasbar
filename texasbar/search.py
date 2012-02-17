#!/usr/bin/env python

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


def _get_html():
    """"""
    url = 'http://www.texasbar.com/AM/Template.cfm'
    query_string='?Section=Find_a_Lawyer&Template=/CustomSource/MemberDirectory/Result_form_client.cfm'

    data={'State': 'TX', 'Submitted': 1, 'PPlCityName': 'Houston', 'LawSchool': 6,
          'ShowPrinter': 1}

    resp = requests.post(''.join([url, query_string]), data=data)
    if resp.status_code != 200:
        print 'Error getting html code: %s' % (resp.status_code)
        return None

    return resp.content


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

    people = []
    html_soup = BeautifulSoup(_get_html())

    for human in _get_people(html_soup):
        person = Person(_get_full_name(human), _get_website(human))
        people.append(person)

    for human in people:
        output.write('%s\n' % (human))


# To go to a new page pass additional arguments:
#   Next: len(names) + 1
#   Prev: len(names) + 1
#   MaxNumber: 25
#   Page: 0 -- bug in their code!

# FIXME: Need BeautifulSoup to parse this super ugly HTML
# FIXME: Make sure script recognizes the number of result pages and fetches
# all of them
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
