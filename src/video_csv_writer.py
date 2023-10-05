import csv
import logging
from dataclasses import dataclass
from itertools import groupby

from html_cache import HtmlCache
from html_parser import HtmlParser
from url_utils import UrlUtils
from video import Video


@dataclass
class VideoCsvWriter:
    csv_path: str
    html_cache: HtmlCache
    excluded_urls: []

    __WEEKS_IN_A_YEAR = 52

    def __find_videos(self, starting_url):
        visited =set([starting_url])
        queue = [(starting_url, None)]
        videos = dict()
        domain = UrlUtils.remove_path(starting_url)
        while queue:
            url, parent_url = queue.pop(0)
            logging.info(f'Getting HTML for {url}')
            html = self.html_cache.get_html(url)
            if html is not None:
                html_parser = HtmlParser(self.excluded_urls, domain, html)
                if url != starting_url:
                    videos_and_titles = html_parser.find_video_urls_and_titles(videos.keys())
                    logging.debug(f'Found {len(videos_and_titles)} videos for {url}')
                    inner_videos = list(map(lambda x: (x[0], Video(x[1], url, x[0], parent_url)), videos_and_titles.items()))
                    videos.update(inner_videos)
                links = html_parser.find_urls()
                logging.debug(f'Found {len(links)} links for {url} with parent {parent_url}')
                for link in links:
                    if link not in visited:
                        visited.add(link)
                        queue.append((link, url))
        return videos.values()


    def __get_video_names(self, videos):
        videos_by_section_name = dict()
        for parent_url, parent_url_group in groupby(videos, lambda x: x.parent_url):
            parent_url_list = list(parent_url_group)
            section = parent_url.split('/')[-2 if parent_url[-1] == '/' else -1]
            url_groupby = list(groupby(parent_url_list, lambda x: x.url))
            logging.debug(f'Found {len(parent_url_list)} videos for parent url {parent_url}')
            for i, (url, url_group) in enumerate(groupby(parent_url_list, lambda x: x.url)):
                is_year = len(url_groupby) >= self.__WEEKS_IN_A_YEAR
                url_list = list(url_group)
                url_length = len(url_list)
                logging.debug(f'Found {url_length} videos for url {url}')
                year_int = int(i / self.__WEEKS_IN_A_YEAR) + 1
                year_part = f'Year {year_int} - ' if is_year else ''
                video_count = '' if len(parent_url_list) < 7 else f'{(i + 1) - ((year_int - 1) * self.__WEEKS_IN_A_YEAR)}. '
                for j, video in enumerate(url_list):
                    count_part = f' - part {j + 1}' if url_length > 1 else ''
                    name = f'{year_part}{video_count}{video.title}{count_part}'
                    logging.debug(f'Determined: {section} - {name} for {video.title}')
                    videos_by_section_name[(section, name)] = video
        return videos_by_section_name


    def __write_videos_to_csv(self, videos):
        logging.info(f'Writing {len(videos)} video rows to CSV')
        with open(self.csv_path, "w") as stream:
            csv_writer = csv.writer(stream)
            csv_writer.writerow(['section', 'name', 'embedded_url', 'parent_url', 'url', 'title'])
            for (section, name), video in videos.items():
                csv_writer.writerow([section, name, video.embedded_url, video.parent_url, video.url, video.title])


    def write_videos_to_csv(self, starting_url):
        videos = self.__find_videos(starting_url)
        titles = self.__get_video_names(videos)
        self.__write_videos_to_csv(titles)