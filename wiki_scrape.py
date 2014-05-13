import sys, os, sqlite3, re, urllib.request
from collections import Counter
import numpy as np
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt


global undesirables
undesirables = [{"element": "table", "attr": {'class': 'infobox'}},
                {"element": "table", "attr": {'class': 'vertical-navbox'}},
                {"element": "span", "attr": {'class': 'mw-editsection'}},
                {"element": "div", "attr": {'class': 'thumb'}},
                {"element": "sup", "attr": {'class': 'reference'}},
                {"element": "div", "attr": {'class': 'reflist'}},
                {"element": "table", "attr": {'class': 'nowraplinks'}},
                {"element": "table", "attr": {'class': 'ambox-Refimprove'}},
                {"element": "img", "attr": None}, {"element": "script", "attr": None},
                {"element": "table", "attr": {'class': 'mbox-small'}},
                {"element": "span", "attr": {"id": "coordinates"}},
                {"element": "table", "attr": {"class": "ambox-Orphan"}},
                {"element": "div", "attr": {"class": "mainarticle"}},
                {"element": None, "attr": {"id": "References"}}]

global common_words
common_words = ['a','able','about','across','after','all','almost','also',
                'am','among','an','and','any','are','as','at','be','because',
                'been','but','by','can','cannot','could','dear','did','do',
                'does','either','else','ever','every','for','from','get','got',
                'had','has','have','he','her','hers','him','his','how','however',
                'i','if','in','into','is','it','its','just','least','let','like',
                'likely','may','me','might','most','must','my','neither','no','nor',
                'not','of','off','often','on','only','or','other','our','out','own',
                'rather','said','say','says','she','should','since','so','some',
                'such','than','that','the','their','them','then','there','these',
                'they','this','to','too','us','wants','was','we','were','what',
                'when','where','which','while','who','whom','why','will','with',
                'would','yet','you','your']

#define database table and database dropping query
create_schema = "CREATE TABLE words_count \
                (id integer primary key autoincrement not null,word text,occurrence_count int)"
drop_schema = "DROP TABLE words_count"

#script execution flow
def main():
    url = str(input('Please enter Wiki web address you would like to scrape below (starting with http://)...\n-->'))
    isValidLink(url)
    checkConnectivity(url)
    global file_dir
    file_dir = str(input('Please enter directory path below where '
                         'database and html files will be stored e.g. '
                         'C:\\YourDirectory (if it does not exists it will be created)...\n-->'))
    createDir(file_dir)
    global db_file
    db_file = file_dir + '\\temp_db.db' #database file location
    doDbWork(db_file)
    remove_commons = str(input('Would you like to remove most commonly '
                               'used English words from the result set? (Y/N)...\n-->'))
    while remove_commons.lower() not in ('Y','y','N','n'):
        remove_commons = str(input('Please select either Y (yes) or N (no) as an option for this input.\n-->'))
    url_save = str(input('Would you like to save scraped HTML file for '
                         'reference in the nominated directory? (Y/N)...\n-->'))
    while url_save.lower() not in ('Y','y','N','n'):
        url_save = str(input('Please select either Y (yes) or N (no) as an option for this input.\n-->'))
    print ('Attempting to scrape {}...'.format(url))
    grabPage(url, url.split("/wiki/")[1].strip().replace("_", " "),db_file, url_save.lower(), remove_commons.lower())
    plotWords(url)

#check if the URL link submitted is a valid one
def isValidLink(url):
    if "/wiki/" in url and ":" in url and "http://"  in url and "wikibooks" not in url \
        and "#" not in url and "wikiquote" not in url and "wiktionary" not in url and "wikiversity" not in url \
        and "wikivoyage" not in url and "wikisource" not in url and "wikinews" not in url and "wikiversity" not in url \
        and "wikidata" not in url:
        print('Wiki link is a valid string...continuing...')
    else:
        print('This is not a valid Wiki URL address. Press any key to exit.')
        input()
        sys.exit(0)

#check if the website is responding to a 'http' call
def checkConnectivity(url):
    try:
        print('Connecting...')
        urllib.request.urlopen(url, timeout=5)
        print("Connection to '{}' succeeded".format(url))
    except:
        urllib.request.URLError
        print("Connection to '{}' DID NOT succeeded. You may want to check the following to resolve this issue:".format(url))
        print(  '1. Internet connection is enabled\n'
                '2. You entered a valid address\n'
                '3. The website is operational\n'
                '...exiting now.')
        input()
        sys.exit(0)

#create database and text file directory
def createDir(file_dir):
    if not os.path.exists(file_dir):
        try:
            print('Attempting to create directory in the path specified...')
            os.makedirs(file_dir)
            print('Directory created successfully...')
        except:
            IOError
            print("Directory COULD NOT be created in the location specified.")
            sys.exit(0)
    else:
        print('Directory specified already exists....moving on...')


#create database file and schema using the scripts above
def doDbWork(db_file):
    try:
        db_is_new = not os.path.exists(db_file)
        with sqlite3.connect(db_file) as conn:
            if db_is_new:
                print("Creating temp database schema on " + db_file + " database ...")
                conn.execute(create_schema)
            else:
                print("Database schema may already exist. Dropping database schema on " + db_file + "...")
                #os.remove(db_filename)
                conn.execute(drop_schema)
                print("Creating temporary database schema...")
                conn.execute(create_schema)
    except:
        print("Unexpected error:", sys.exc_info()[0])
    finally:
        conn.commit()
        conn.close()


# process URL page, exporting the HTML file into a directory nominated (optional)
# and inserting most commonly used words into a database file
def grabPage(url, name, db_file, url_save, remove_commons):
    try:
        opener = urllib.request.urlopen(url)
        page = opener.read()
        s = BeautifulSoup(page)
        s = s.find(id="mw-content-text")
        if hasattr(s, 'find_all'):
                for notWanted in undesirables:
                    removal = s.find_all(notWanted['element'], notWanted['attr'])
                    if len(removal) > 0:
                        for el in removal:
                            el.extract()
                also = s.find(id="See_also")
                if (also != None):
                    also.extract()
                    tail = also.find_all_next()
                    if (len(tail) > 0):
                        for element in tail:
                            element.extract()
        text = s.get_text(" ", strip=True)
        opener.close()
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        words = [word.lower() for word in text.split()]
        c = Counter(words)
        if remove_commons == 'y':
                for key in common_words:
                    if key in c:
                        del c[key]
        for word, count in c.most_common(40):
                cursor.execute("INSERT INTO words_count (word, occurrence_count)\
                              SELECT (?), (?)", (re.sub('[–{@#!;+=_,$<(^)>?.:%/&}''"''-]', '', word.lower()), count))
        #delete numerical characters, NULLs and empty spaces
        cursor.execute("DELETE FROM words_count WHERE word glob '[0-9]*' or word ='' or word IS NULL")
        #delete duplicate records where the same word is repeated more then once
        cursor.execute("DELETE  FROM words_count WHERE id NOT IN(\
                        SELECT  MIN(id) FROM  words_count GROUP BY word)")
        #delete records outside top 30
        cursor.execute("DELETE FROM words_count WHERE occurrence_count NOT IN(\
                        SELECT occurrence_count FROM words_count ORDER BY 1 DESC LIMIT 30)")
        if url_save == 'y':
            soup = BeautifulSoup(page, "html5lib", from_encoding="UTF-8")
            content = soup.find(id="mw-content-text")
            if hasattr(content, 'find_all'):
                for notWanted in undesirables:
                    removal = content.find_all(notWanted['element'], notWanted['attr'])
                    if len(removal) > 0:
                        for el in removal:
                            el.extract()
                also = content.find(id="See_also")
                if (also != None):
                    also.extract()
                    tail = also.find_all_next()
                    if (len(tail) > 0):
                        for element in tail:
                            element.extract()
                fileName = str(name)
                doctype = "<!DOCTYPE html>"
                head = "<head><meta charset=\"UTF-8\" /><title>" + fileName + "</title></head>"
                f = open(file_dir + "/" + fileName.replace('/', '_') + ".html", 'w', encoding='utf-8')
                f.write(
                    doctype + "<html lang=\"en\">" + head + "<body><h1>" + fileName + "</h1>" + str(content) + "</body></html>")
                f.close()
                print ('Scraped HTML file and database file have been saved in "{0}\\" directory '
                       'with a bar chart displayed in a separate window'.format(file_dir))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        conn.rollback()
    finally:
        conn.commit()
        conn.close()


def wordsOutput():
    try:
        arr = []
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT word, occurrence_count FROM words_count ORDER BY occurrence_count DESC')
        #column_names = [d[0] for d in cursor.description] # extract column names
        for row in cursor:
            arr.append(row)
        return arr
    except:
        print("Unexpected error:", sys.exc_info()[0])
    finally:
        conn.close()

#plot data onto the bar chart
def plotWords(url):
    data = wordsOutput()
    N = len(data)
    x = np.arange(1, N+1)
    y = [num for (s, num) in data]
    labels = [s for (s, num) in data]
    width = 0.7
    plt.bar(x, y, width, color="r")
    plt.ylabel('Frequency')
    plt.xlabel('Words')
    plt.title('Word Occurrence Frequency For '"'{}'"' Wiki Page'.format(url.split("/wiki/")[1].strip().replace("_", " ")))
    plt.xticks(x + width/2.0, labels)
    plt.xticks(rotation=45)
    plt.show()

#run from here!
if __name__ == '__main__':
    main()






