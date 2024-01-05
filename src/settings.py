import os


HOME_DIR = os.path.join(os.path.expanduser('~'), 'video_scraper') 
DOWNLOAD_DIR = os.path.join(HOME_DIR, 'videos')
HTML_CACHE_DIR = os.path.join(HOME_DIR, 'html_cache')
LOG_FILENAME = 'log.txt'
CSV_DIR = os.path.join(HOME_DIR, 'csv')
CSV_FILENAME = 'videos.csv'
CSV_FILEPATH = os.path.join(CSV_DIR, CSV_FILENAME)
URL_EXCLUDE_LIST = [
    'membership'
    'subscribe',
    'subscription',
    'faq',
    'account',
    'orders',
    'privacy',
    'cookie',
    'contact-us',
    'terms',
    'cart',
    'login'
]