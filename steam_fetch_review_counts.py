#!/usr/bin/env python

from BeautifulSoup import BeautifulSoup
from soupselect import select
import urllib
import re
import datetime
import sys

def get_count(element):
    count = element.string
    if not count:
        return None

    return re.sub(r'[(), ]', '', count)

def fetch_review_counts(appid):
    class FetchError(StandardError):
        pass

    url = 'http://store.steampowered.com/app/%i/' % appid
    request = urllib.urlopen(url)
    if request.code < 200 or request.code > 299:
        raise FetchError('Unable to fetch %s' % url, { 'appid': appid, 'status': request.code})

    soup = BeautifulSoup(request)

    positive_count = ''
    positive_count_elements = select(soup, '#ReviewsTab_positive .user_reviews_count')
    if len(positive_count_elements) > 0:
        positive_count = get_count(positive_count_elements[0])

    if not positive_count:
        print >>sys.stderr, "Warning: Unable to find positive user review count on page %s" % url

    negative_count = ''
    negative_count_elements = select(soup, '#ReviewsTab_negative .user_reviews_count')
    if len(negative_count_elements) > 0:
        negative_count = get_count(negative_count_elements[0])

    if not negative_count:
        print >>sys.stderr, "Warning: Unable to find negative user review count on page %s" % url

    return positive_count, negative_count

def write_review_counts(appid, positive_count, negative_count):
    with open('review_counts_%i.csv' % appid, 'a') as csv:
        if csv.tell() == 0:
            print >>csv, 'When,Positive reviews,Negative reviews'

        when = datetime.date.today()
        print >>csv, '%s,%s,%s' % (when.strftime('%F'), positive_count, negative_count)

def main(args):
    if not args:
        print >>sys.stderr, "Usage: %s <appid> [appid] [appid ...]" % sys.argv[0]
        return 1

    for appid in map(int, args):
        write_review_counts(appid, *fetch_review_counts(appid))

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
