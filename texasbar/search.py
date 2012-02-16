#!/usr/bin/env python

import sys

import requests
from BeautifulSoup import BeautifulSoup


def get_html():
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


def search(output):
    """Search for attorneys and write to output stream"""

    html = get_html()
    soup = BeautifulSoup(html)

    output.write(soup.prettify())
    output.close()


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
