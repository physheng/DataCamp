from bs4 import BeautifulSoup
import urllib2,cookielib
import time     #important to wait
import json
import os,sys,getopt
import re   
import itertools

usage = "download data \nUsage: " + sys.argv[0]
usage += ''' <Required> [Options]
    <Rrequired:>
        -n The numbers of page that to be run,separated by ",".[For example, "-n 5(included),9(included)"] 
'''
usage += "Ex.: " + sys.argv[0] + " -n 5,9 "

if len(sys.argv) < 1 : sys.exit(usage)
run_page_num=''
optlist, alist = getopt.getopt(sys.argv[1:], 'h:n:')
for opt in optlist:
    if opt[0] == '-h': sys.exit(usage)
    elif opt[0] == '-n': run_page_num = opt[1]

if run_page_num=='':sys.exit(usage)
run_page_num_low=int(run_page_num.strip().split(",")[0].strip())
run_page_num_high=int(run_page_num.strip().split(",")[1].strip())

def open_page(site):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    req = urllib2.Request(site, headers=hdr)
    try:
        page = urllib2.urlopen(req)
        return BeautifulSoup(page, "html.parser")
    except urllib2.HTTPError, e:
        print e.fp.read()
        return None

def scrape_game_page(game, year, game_page_link):
    game_soup = open_page(game_page_link)
    if game_soup is not None:
        """
        Find all the names in the Credits part
        """
        #f = open(game+'.txt', w)
        try:
            credit_sidebar = game_soup.find('div', attrs = {'class': 'sideBarContent'})
            credit_tags = credit_sidebar.find_all('div', attrs = {'style':"padding: 0.5em 1em 1em 1em;"})
            names = []
            
            #print credit_tags
            for tag in credit_tags:
                for name in tag.find_all('a'):
                    # Find developer ID
                    developer_link = name['href'].encode("ascii")
                    developer_id = int(re.search(r'\d+',developer_link).group())
                    names.append(developer_id)
                    #names.append(name.string)
            #print names    
        except:
            names = []
        """
        Find Genre information
        """
        try:
            genre_tags = game_soup.find('div', attrs = {'id': "coreGameGenre"}).find('div', {'style':"font-size: 90%; padding-left: 1em; padding-bottom: 0.25em;"})
            genre = genre_tags.a.string.encode("ascii")
            #print genre
        except:
            genre = None
            """
            Find the average rating
            """
        try:
            rating_tags = game_soup.find_all('div', attrs = {'style':'font-size: 11pt; width: 2.75em; padding: 0.20em 0 0.50em 0; color: white; text-align: center; font-weight: bold'})
            rating = 0;        
            for rating_tag in rating_tags:
                rating += float(rating_tag.string)
                rating = rating/len(rating_tags)
        except:
            rating = None
    """
    Return a dictionary
    """
    game_info = {'game_name': game, 'year': year, 'Credits':names, 'Genre': genre, 'avg_rating': rating}
    return game_info

    
site = "http://www.mobygames.com/browse/games/list-games/"

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

req = urllib2.Request(site, headers=hdr)

try:
    page = urllib2.urlopen(req)
except urllib2.HTTPError, e:
    print e.fp.read()

soup = BeautifulSoup(page, "html.parser")

"""
find the number of pages
"""
num_string = soup.find('td', attrs = {'class' : 'mobHeaderPage'}).string
num_page = int(num_string.split()[4])

"""
construct the links for different pages
"""
page_0_link = "http://www.mobygames.com/browse/games/offset,0/so,0a/list-games/"
element_link = page_0_link.split('/')
page_links = []
for i in range(run_page_num_low,run_page_num_high):
    element_link[5] = 'offset,'+str(i*25)
    page_links.append('/'.join(element_link))
    #print 'url: ', '/'.join(element_link)

"""
On each page, search for the game
"""
print "Opening the file..."
target = open('gameWebsite.json', 'w')
network = open('gameNetwor.csv','w')
for link in page_links:
    print link
    page_soup = open_page(link)
    if page_soup is not None:
        game_tags = page_soup.find_all('tr', attrs = {'valign':'top'})
        for item in game_tags:
            game = item.td.a.string
            year = item.td.find_next_sibling().string
            game_page_link = 'http://www.mobygames.com'+item.td.a.get('href')
            #print game + '\t' + year + '\t' + game_page_link 
            game_info = scrape_game_page(game, year, game_page_link)
            #print type(game_info)
            
            # Create network nodes and edges for each game
            # If there is one person in the credit list, node is connect to itself
            # Other wise, create people pairs
            if len(game_info['Credits']) == 1:
                network.write("%s, %s, %s\n" %(game_info['Credits'][0], game_info['Credits'][0], game_info['year']) )
            elif len(game_info['Credits']) > 1:
                developer_pair = list(itertools.combinations(game_info['Credits'],2))
                for i in range(len(developer_pair)):
                    network.write("%s, %s, %s\n" %(developer_pair[i][0], developer_pair[i][1], game_info['year']) )
            else:
                #print game_info['game_name'], " has ","No developer"
                pass

            #print game_info            
            target.write(json.dumps(game_info))
            target.write('\n')
    else:
         print "can't open the link: ", link
    time.sleep(0.5)
target.close()
network.close()