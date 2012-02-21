#!/usr/bin/env python

"""
Module to provide a quick interface to getting law alumni from a particular
school and living in a given city.
"""

import re
import sys

import requests
from BeautifulSoup import BeautifulSoup


QUERY_URL = 'http://www.texasbar.com/AM/Template.cfm'
QUERY_STRING = '?Section=Find_a_Lawyer&Template=/CustomSource/' \
                'MemberDirectory/Result_form_client.cfm'


class DataError(Exception):
    """Raised when encountering a problem getting data from url"""
    pass


class Person(object):
    """person container"""

    def __init__(self, name, firm, websites):
        """init"""

        self.name = name
        self.firm = firm
        self.websites = websites

    def __str__(self):
        """str"""

        return unicode(self).encode('utf-8')

    def __unicode__(self):
        """unicode"""

        # Don't let any commas get in since we are printing as csv
        name = re.sub(',', '.', self.name)
        firm = re.sub(',', '.', self.firm)
        sites = re.sub(',', '.', ' '.join(self.websites))

        return '%s, %s, %s' % (name, firm, sites)

    def __repr__(self):
        """repr"""

        info = {}
        for name, val in self.__dict__.iteritems():
            if isinstance(val, str):
                info[name] = val.encode('ascii', 'ignore')
            else:
                info[name] = val

        return "Person('{name}', '{firm}', {websites})".format(**info)


def _get_number_of_pages(post_data, max_per_page):
    """Get the number of pages results will yield"""

    post_data['MaxNumber'] = max_per_page

    resp = requests.post(''.join([QUERY_URL, QUERY_STRING]), data=post_data)
    if resp.status_code != 200:
        raise DataError('Error getting html code: %s' % (resp.status_code))

    html_soup = BeautifulSoup(resp.content)
    pages = html_soup.findAll('span', {'class': 'pagenumber'})

    return int(list(pages)[-1].text)


def _get_html(page, post_data, max_per_page):
    """Get page of html results"""

    post_data['MaxNumber'] = max_per_page
    next_result_idx = max_per_page * (page - 1)

    if next_result_idx > 0:

        # Yes, their code uses page like this...
        post_data['ButtonName'] = 'Page'
        post_data['Page'] = next_result_idx + 1
        post_data['Next'] = next_result_idx + 1

    resp = requests.post(''.join([QUERY_URL, QUERY_STRING]), data=post_data)
    if resp.status_code != 200:
        raise DataError('Error getting html code: %s' % (resp.status_code))

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


def search(start_page=1, end_page=-1, max_per_page=25, verbose=False):
    """Search for attorneys and return list"""

    post_data = {'State': 'TX', 'Submitted': 1, 'PPlCityName': 'Houston',
                 'LawSchool': 6, 'ShowPrinter': 1}

    if end_page == -1:
        end_page = _get_number_of_pages(post_data, max_per_page)

    # Always get at least one page
    end_page += 1

    for page_num in xrange(start_page, end_page):
        people = []
        content = _get_html(page_num, post_data, max_per_page)

        if verbose:
            print '----- Page', page_num, 'of', end_page, '-----'

        html_soup = BeautifulSoup(content)

        for human in _get_people(html_soup):
            person = Person(_get_full_name(human), _get_website(human))
            people.append(person)

        yield people


if __name__ == "__main__":
    import argparse

    # FIXME: Add option for city name, law school, state

    parser = argparse.ArgumentParser(
                        description='Search texasbar.com for attorneys')
    parser.add_argument('--log', default=sys.stdout,
                        type=argparse.FileType('w'),
                        help='Optional file to write results')
    parser.add_argument('-v', default=False, action='store_true',
                        help='Verbose output of fetching results page by page')
    parser.add_argument('--start_page', default=1, type=int,
                        help='Starting page number for results')
    parser.add_argument('--end_page', default=-1, type=int,
                    help='Ending page number for results (-1 for all pages)')
    parser.add_argument('--max_per_page', default=25, type=int,
                        help='Max number of people per page of results')

    args = parser.parse_args()
    for result_page in search(args.start_page, args.end_page,
                              args.max_per_page, args.v):
        for attorney in result_page:
            try:
                args.log.write('%s\n' % (attorney))
            except UnicodeEncodeError, err:
                print 'Error %s' % (err)
                print 'Skipping %s' % repr(attorney)
