import csv
import os
from video import Video

from vimeo_downloader import Vimeo

class VideoDownloader:


    def __init__(self, csv_dir, download_dir, filename, root_url) -> None:
        self.__download_dir = download_dir
        self.__root_url = root_url
        with open(os.path.join(csv_dir, filename), "r") as stream:
            csv_reader = csv.reader(stream)
            self.__videos = [Video(*i) for i in csv_reader]


    def dryrun(self, filter_contains = None):
        count = 0
        for v in self.__videos:
            if filter_contains is None or filter_contains in v.parent_url:
                filename = v.get_filename()
                print(filename)
                count = count + 1
        print(f'Total: {count}')
        

    def get_video_sizes(self, filter_contains = None):
        video_sizes = []
        for v in self.__videos:
            if filter_contains is None or filter_contains in v.parent_url:
                print(str(v))
                vimeo = Vimeo(v.embedded_url, embedded_on=v.url)
                if len(vimeo.streams) > 0:
                    print((v.title, vimeo.streams[0].filesize))
                    video_sizes.append((v.title, vimeo.streams[0].filesize))
                else:       
                    print(f'No streams found for {v.title}')


    def download_videos(self, filter_contains = None):
        output_path = os.path.join(os.getcwd(), self.__download_dir)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for v in self.__videos:
            if filter_contains is None or filter_contains in v.parent_url:
                filename = v.get_filename()
                v = Vimeo(v.embedded_url, embedded_on=v.url)
                v.streams[0].download(download_directory=self.__download_dir, filename=filename)

