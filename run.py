# encoding: utf8
import feedparser
import pystache
from bs4 import BeautifulSoup
from helpers import *
import time


while True:
    for cat in categories:
        entries = get_feed_data(cat)
        parse_feed_data(entries, cat)
        generate_category_list(cat)
        generate_main_list()
        time.sleep(20)