import csv
import logging
import os
from dataclasses import dataclass

from vimeo_downloader import Vimeo

from file_utils import FileUtils
from video import Video


@dataclass
class VideoDownloader:
    download_path: str


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


    def download_videos(self, csv_filepath):
        videos_by_section = self.__get_videos_by_section(csv_filepath)
        for section, videos in videos_by_section.items():
            output_path = FileUtils.create_dir_if_not_exists(self.download_path, section)
            for video in videos:
                    video_path = os.path.join(output_path, f'{video.title}.mp4')
                    if os.path.exists(video_path):
                        logging.debug(f'Video already exists {video_path}')
                    else:
                        logging.info(f'Downloading: {video_path}')
                        v = Vimeo(video.embedded_url, embedded_on=video.url)
                        v.streams[0].download(download_directory=output_path, filename=video.title)

