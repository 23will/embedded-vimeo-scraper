from video_downloader import VideoDownloader

import argparse
import settings


parser = argparse.ArgumentParser(description="Vimeo downloader")
parser.add_argument("--embedded_url", type=str, help="The vimeo url")
parser.add_argument("--url", type=str, help="The url of the page that the video is on")
parser.add_argument(
    "--title", type=str, help="Essentially the filename minus the extension"
)

args = parser.parse_args()

video_downloader = VideoDownloader(settings.DOWNLOAD_DIR)
video_downloader.download_video(args.embedded_url, args.url, args.title)
