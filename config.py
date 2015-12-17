from pymongo import MongoClient

template_directory = '_templates/'
article_target_directory = 'site/articles/'
list_target_directory = 'site/lists/'
main_target_directory = 'site/'

MONGO_DATABASE = 'tesla_test'
client = MongoClient('localhost', 27017)
db = client[MONGO_DATABASE]
articles_db = db.articles_db

categories = [u'stat',
              u'nucl-th',
              u'hep-ph',
              u'nucl-ex',
              u'q-bio',
              u'astro-ph',
              u'gr-qc',
              u'cond-mat',
              u'math-ph',
              u'hep-lat',
              u'quant-ph',
              u'cs',
              u'hep-ex',
              u'hep-th',
              u'nlin',
              u'physics',
              u'math']
