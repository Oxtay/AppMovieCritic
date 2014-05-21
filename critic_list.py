import urllib2
from bs4 import BeautifulSoup as bs
import requests
import re
import os
import sys


REVIEWERS = '/externalreviews'
IMDB_PAGE = 'http://www.imdb.com'
tmp_path = '/title/tt0109830' # For Forrest Gump

def get_ciritic_list(movie_url):
	# Extracts the list of external reviews from a movie's page on IMDB
	
	html = urllib2.urlopen( movie_url ).read()
	soup = bs(html)
	div = soup.find('div', {'id':'external_reviews_content'})
	external_urls = [IMDB_PAGE + a['href'] for a in div.find_all('a', href = True) if a]
	for row in external_urls:
		print 'URL:', row
	print len(external_urls)
	sys.exit(0)

def go_to_url(url_list):
	pass

def main():
	review_page_url = IMDB_PAGE + tmp_path + REVIEWERS
	get_ciritic_list(review_page_url)

if __name__ == '__main__':
	main()