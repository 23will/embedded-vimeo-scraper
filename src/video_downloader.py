import csv
import logging
import os
from dataclasses import dataclass

from vimeo_downloader import Vimeo
from vimeo_local_downloader import EmbeddedVimeo
# from src.vimeo_downloader2 import Vimeo2

from file_utils import FileUtils
from video import Video


@dataclass
class VideoDownloader:
    download_path: str
    base_url: str = None


    def __get_videos_by_section(self, csv_filepath):
        with open(csv_filepath, "r") as stream:
            csv_reader = csv.reader(stream)
            next(csv_reader)
            videos_by_section = dict()
            for row in csv_reader:
                section, name, embedded_url, parent_url, url, _ = row
                video =Video(name, url, embedded_url, parent_url)
                if section in videos_by_section:
                    videos_by_section[section].append(video)
                else:
                    videos_by_section[section] = [video]
            return videos_by_section


    def download_video(self, embedded_url, url, title, output_path=''):
        path = self.download_path if output_path == '' else output_path
        video_path = os.path.join(path, f'{title}.mp4')
        if os.path.exists(video_path):
            logging.debug(f'Video already exists {video_path}')
        else:
            logging.info(f'Downloading: {video_path}')
            v = Vimeo(embedded_url, embedded_on=url)
            if v.streams:
                v.streams[0].download(download_directory=path, filename=title)
            else:
                logging.warn(f'No streams found for {title} - {url}, attempting alternative download')
                vl = EmbeddedVimeo()
                referrer = url if self.base_url is None else self.base_url
                vl.download(embedded_url, referrer, video_path)
                


    def download_videos(self, csv_filepath):
        videos_by_section = self.__get_videos_by_section(csv_filepath)
        for section, videos in videos_by_section.items():
            output_path = FileUtils.create_dir_if_not_exists(self.download_path, section)
            for video in videos:
                    self.download_video(video.embedded_url, video.url, video.title, output_path)
