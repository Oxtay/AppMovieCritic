from BeautifulSoup import BeautifulSoup as bs
import requests
import re
import os


REVIEWERS = '/externalreviews'
IMDB_PAGE = 'http://www.imdb.com'
tmp_path = '/title/tt0109830' # For Forrest Gump

def get_ciritic_list():
	review_page_addrs = IMDB_PAGE + tmp_path + REVIEWERS