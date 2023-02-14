import pycookiecheat
from video_url_grabber import VideoCsvWriter, extract_root_url
from video_downloader import VideoDownloader


#TODO logging, cli, linting, settings file

CSV_DIR = 'csv'
DOWNLOAD_DIR = 'videos'
HTML_CACHE_DIR = 'html_cache'
CSV_FILENAME = 'videos.csv'
MISSING_URLS_CSV_FILENAME = 'missing_urls.csv'
URL = 'https://someurl.com/stuff/'


root_url = URL.split('.com')[0] + '.com'

#requires you to have logged in on chrome as it all works with cookies
cookies = pycookiecheat.chrome_cookies(root_url)


#Recursively looks through html for url links and embedded video links and writes to a CSV in /csv path, caches the html for performance in /html_cache path
#This CSV contains urls that don't contain any video links as a sanity check
video_grabber = VideoCsvWriter(CSV_DIR, HTML_CACHE_DIR, cookies, root_url, URL, CSV_FILENAME, MISSING_URLS_CSV_FILENAME)
video_grabber.write_videos_to_csv()

video_downloader = VideoDownloader(CSV_DIR, DOWNLOAD_DIR, CSV_FILENAME, root_url)
#dryrun returns list of filenames that can be downloaded given the videos parent url contains someefilter
video_downloader.dryrun('somefilter')
#video_downloader.download_videos('sound')

