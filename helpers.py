import re
import datetime
import feedparser
from bs4 import BeautifulSoup
from config import *
import os
import pystache
import codecs
from shutil import copyfile

renderer = pystache.Renderer()


def get_category(string):
    """Extracts the category from the string"""
    try:
        match = re.search('\((arXiv.*?)\)', string).group(0)
        category = re.search('\[(.*?)\]', match).group(1)
    except Exception, e:
        print "There was an error getting the category from the title."
        return "EMPTY"
    else:
        return str(category)


def clean_title(string):
    """Cleans the title and removes stuff"""
    try:
        match = re.search('\((arXiv.*?)\)', string).group(0)
    except Exception, e:
        print "There was an error cleaning the title"
        return "EMPTY"
    else:
        return string[0: len(string) - len(match)]


def timestamp():
    """Makes a timestamp for the current day"""
    try:
        today = datetime.datetime.now()
        _stamp = '{}{}{}'.format(today.year, today.month, today.day)
    except Exception, e:
        print "Error while creating the timestamp"
        return "EMPTY"
    else:
        return _stamp


def beautify(description):
    """Beautifies the description part by inserting some breaks here and there"""
    return description
    # try:
    #     pat = re.compile(r'([A-Z][^\.!?]*[\.!?])', re.M)
    #     sentences = pat.findall(description)
    #     beautiful = ' '.join(l + '<br/>' * (n % 3 == 2) for n, l in enumerate(sentences))
    # except Exception, e:
    #     print "There was en error beautifying shit"
    #     return "EMPTY"
    # else:
    #     return beautiful


def add_article(article):
    """Add article to main database"""
    try:
        articles_db.insert(article)
    except Exception, e:
        print "Problem inserting shit"
    else:
        print "Article inserted"


def does_exist(article):
    """Check if an article exists in the database"""
    try:
        if articles_db.find({'id': article['id']}).count() > 0:
            return True
        else:
            return False
    except Exception, e:
        print "Problem checking shit"
        return True


def get_feed_data(category):
    """Gets all the entries from a category feed"""
    try:
        d = feedparser.parse('http://export.arxiv.org/rss/{}'.format(category))
        pass
    except Exception, e:
        print "Problem getting feed"
        return []
    else:
        return d.entries


def parse_feed_data(entries, category):
    """Parses the feed entries"""
    try:
        if len(entries) > 1:
            for entry in entries:
                new_article = dict()
                new_article['category'] = category
                new_article['date'] = timestamp()
                new_article['processed'] = False
                new_article['title'] = clean_title(entry.title.encode('utf-8'))
                new_article['link'] = entry.link
                new_article['id'] = entry.link.split('/')[-1].replace('.', '-')
                new_article['link_pdf'] = entry.link.replace('/abs/', '/pdf/')
                new_article['description'] = beautify(entry.description)
                new_article['authors'] = BeautifulSoup(entry.authors[0]['name'], 'html.parser').text
                if not does_exist(new_article):
                    print "Adding new article!"
                    add_article(new_article)
                    generate_article(new_article)
        else:
            return []
        pass
    except Exception, e:
        print "Problem parsing feed data"
        return []
    else:
        print "Feed parsed and database updated."


def generate_article(article):
    """Generates the HTML for an article"""
    try:
        file_title = article['id'] + '.html'
        file_destination = os.path.join(article_target_directory, article['category'], timestamp())
        file_path = os.path.join(file_destination, file_title)
        if not os.path.exists(file_destination):
            os.makedirs(file_destination)
        with codecs.open(file_path, 'w', 'utf-8') as the_file:
            the_file.write(renderer.render_path('{}article.mustache'.format(template_directory), article))
    except Exception, e:
        print "Couldn't generate article, fuck."
        print e
    else:
        print "Article generated, man!"
        pass


def generate_category_list(category):
    """Generates the list for the category"""
    try:
        articles = articles_db.find({'date': timestamp(), 'category': category})
        items = list()
        list_title = 'list_{}_{}.html'.format(timestamp(), category)
        list_destination = os.path.join(list_target_directory, timestamp())
        list_path = os.path.join(list_destination, list_title)
        if not os.path.exists(list_destination):
            os.makedirs(list_destination)

        if articles.count() > 0:
            for article in articles:
                article_path = os.path.join(article_target_directory, article['category'], timestamp(),
                                            article['id'] + '.html')
                article['article_link'] = os.path.join('..', '..', '..', article_path)
                items.append(renderer.render_path('{}entry.mustache'.format(template_directory), article))

            items_insert = {'items': '\n'.join(items)}
            with codecs.open(list_path, 'w', 'utf-8') as the_list:
                the_list.write(renderer.render_path('{}list.mustache'.format(template_directory), items_insert))

        else:
            print "Nothing to do."
    except Exception, e:
        print "Couldnt generate stupid list"
    else:
        print "Sweet!"


def generate_main_list():
    """Generates the main list with the last five days entries"""
    try:
        todays_lists = os.listdir(os.path.join('site/lists/{}'.format(timestamp())))
        items = list()
        for list_item in todays_lists:
            if '.html' in list_item:
                main_list_el = dict()
                main_list_el['list_title'] = list_item.replace('.html', '').split('_')[1]
                main_list_el['list_category'] = list_item.replace('.html', '').split('_')[2]
                main_list_el['list_link'] = os.path.join('lists/{}'.format(timestamp()), list_item)
                items.append(renderer.render_path('{}main_list_entry.mustache'.format(template_directory), main_list_el))

        main_items_insert = {'main_list_items': '\n'.join(items)}
        with codecs.open('site/list.html', 'w', 'utf-8') as the_list:
                the_list.write(renderer.render_path('{}main_list.mustache'.format(template_directory), main_items_insert))
    except Exception, e:
        print "There was a problem generating the main list!"
    else:
        print "Double fucking sweet!"


def archive_previous_list():
    """Move the previous list to the archive folder"""
    try:
        previous_list = os.path.join('site', 'list.html')
        destination = os.path.join(archive_directory, 'list{}.html'.format(timestamp()))
        copyfile(previous_list, destination)
    except Exception, e:
        print "Couldnt archive stupid list!"
    else:
        print "List was archived, starting out fresh"


def process_archived_list():
    """Change all the links and paths for the archived list"""
    try:
        with open(os.path.join(archive_directory, 'list{}.html'.format(timestamp()))) as list_to_process:
            soup = BeautifulSoup(list_to_process, 'html.parser')
            css_path = soup.find('link', {'href': 'css/tufte.css'})
            css_path['href'] = css_path['href'].replace('css/tufte.css', '../css/tufte.css')
            links = soup.find_all('a')
            for link in links:
                if 'lists/' in link['href']:
                    link['href'] = '../{}'.format(link['href'])
            with open(os.path.join(archive_directory, 'list{}.html'.format(timestamp())), 'w') as processed:
                processed.write(str(soup))
    except Exception, e:
        print "Shit happens processing stuff"
        print e
    else:
        print "yay"
