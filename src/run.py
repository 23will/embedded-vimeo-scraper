import argparse
import logging
import logging.config
import asyncio
import settings
from file_utils import FileUtils
from html_cache import HtmlCache
from url_utils import UrlUtils
from video_csv_writer import VideoCsvWriter
from video_downloader import VideoDownloader
from video_finder import Videofinder


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILENAME),
        logging.StreamHandler()
    ]
)

async def run(url, skip_write_csv, skip_download_videos):
    #requires you to have logged in on chrome as the html retrieval and video download is done with cookies
    cookies = UrlUtils.get_cookies(url)

    #Stores the html locally, useful for debugging
    html_cache = HtmlCache(settings.HTML_CACHE_DIR, cookies)

    FileUtils.create_dir_if_not_exists(settings.CSV_DIR)
    
    if skip_write_csv is None or not skip_write_csv:
        #Recursively (breadth first) searches HTML for urls and embedded videos and writes a CSV 
        video_finder = Videofinder(html_cache, settings.URL_EXCLUDE_LIST)
        videos = await video_finder.find_videos(url)
        video_csv_writer = VideoCsvWriter(settings.CSV_FILEPATH)
        video_csv_writer.write_videos_to_csv(videos)

    FileUtils.create_dir_if_not_exists(settings.DOWNLOAD_DIR)

    if skip_download_videos is None or not skip_download_videos:
        #Consumes previous CSV and dowloads the videos, does some magic around the title and numbering
        video_downloader = VideoDownloader(settings.DOWNLOAD_DIR)
        video_downloader.download_videos(settings.CSV_FILEPATH)


parser = argparse.ArgumentParser(description="Recursive HTML vimeo scraper")
parser.add_argument("--url", type=str, help="The starting URL from which to scrape the videos")
parser.add_argument("--skip-csv-writing", action="store_true", help="Skip CSV writing (default: False)")
parser.add_argument("--skip-video-download", action="store_true", help="Skip downloading of videos (default: False)")

args = parser.parse_args()

asyncio.run(run(args.url, args.skip_csv_writing, args.skip_video_download))

