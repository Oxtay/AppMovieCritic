import urllib2
from bs4 import BeautifulSoup as bs
import requests
import re
import os
import sys
import nltk


REVIEWERS = '/externalreviews'
IMDB_PAGE = 'http://www.imdb.com'
tmp_path  = '/title/tt0109830' # For Forrest Gump


def get_ciritic_list(movie_url):
# Extracts the list of external reviews from a movie's page on IMDB
	html 		= urllib2.urlopen( movie_url ).read()
	soup_movie 	= bs(html)
	div 		= soup_movie.find('div', {'id':'external_reviews_content'})
	external_urls = [IMDB_PAGE + a['href'] for a in div.find_all('a', href = True) if a]
	return external_urls

def get_review_in_url(review_url):
# Having a URL as the input, extracts the content of the review from that URL
	review_html 	= urllib2.urlopen( review_url ).read()
	soup_review 	= bs(review_html)
	texts 	= soup_review.find_all(text = True)

	# Time it to see which one of these are faster:
	# Solution 1 
	review_content = nltk.clean_html(texts)

	# Solution 2
	review_content = filter(visible, texts)

	# Exit here for debugging
	sys.exit(0)
	return review_content

def visible(element):
# Used in get_review_in_url fcn

    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

 
def get_review_sentiment(text):
# using nltk, it gives a measure for the sentiment of a movie review
	pass

def main():
	review_page_url = IMDB_PAGE + tmp_path + REVIEWERS
	get_ciritic_list(review_page_url)

if __name__ == '__main__':
	main()