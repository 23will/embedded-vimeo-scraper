import logging
import asyncio

from dataclasses import dataclass
from itertools import groupby

from html_cache import HtmlCache
from html_parser import HtmlParser
from url_utils import UrlUtils
from video import Video


@dataclass
class Videofinder:
    html_cache: HtmlCache
    excluded_urls: []

    __WEEKS_IN_A_YEAR = 52

    async def __find_videos_and_links(self, url, domain, parent_url, visited_urls):
        logging.info(f"Getting HTML for {url}")
        html = self.html_cache.get_html(url)
        videos = []
        exception_url_parts = ["duplicate1", "duplicate2"]
        if html is not None:
            html_parser = HtmlParser(self.excluded_urls, domain, html)
            video_url_and_titles = html_parser.find_video_urls_and_titles()
            logging.debug(f"Found {len(video_url_and_titles)} videos for {url}")
            for video_url, title in video_url_and_titles.items():
                if video_url not in visited_urls or any(
                    s in video_url for s in exception_url_parts
                ):
                    logging.info(f"Video found {video_url}")
                    videos.append(Video(title, url, video_url, parent_url))
                    visited_urls.add(video_url)
                else:
                    logging.warn(f"Video already found {video_url}")
            links = html_parser.find_urls(visited_urls)
            logging.debug(
                f"Found {len(links)} links for {url} with parent {parent_url}"
            )
        return videos, links

    async def __find_videos(self, starting_url):
        visited_urls = set([starting_url])
        domain = UrlUtils.remove_path(starting_url)
        queue = [(starting_url, None)]
        total_videos = []
        while queue:
            url, parent_url = queue.pop(0)
            videos, links = await self.__find_videos_and_links(
                url, domain, parent_url, visited_urls
            )
            total_videos.extend(videos)
            for link in links:
                if link not in visited_urls:
                    visited_urls.add(link)
                    queue.append((link, url))
        return total_videos

    def __get_video_names(self, videos):
        videos_by_section_name = dict()
        for parent_url, parent_url_group in groupby(videos, lambda x: x.parent_url):
            parent_url_list = list(parent_url_group)
            section = parent_url.split("/")[-2 if parent_url[-1] == "/" else -1]
            url_groupby = list(groupby(parent_url_list, lambda x: x.url))
            logging.debug(
                f"Found {len(parent_url_list)} videos for parent url {parent_url}"
            )
            for i, (url, url_group) in enumerate(
                groupby(parent_url_list, lambda x: x.url)
            ):
                is_year = len(url_groupby) >= self.__WEEKS_IN_A_YEAR
                url_list = list(url_group)
                url_length = len(url_list)
                logging.debug(f"Found {url_length} videos for url {url}")
                year_int = int(i / self.__WEEKS_IN_A_YEAR) + 1
                year_part = f"Year {year_int} - " if is_year else ""
                video_count = (
                    ""
                    if len(parent_url_list) < 7
                    else f"{(i + 1) - ((year_int - 1) * self.__WEEKS_IN_A_YEAR)}. "
                )
                for j, video in enumerate(url_list):
                    count_part = f" - part {j + 1}" if url_length > 1 else ""
                    name = f"{year_part}{video_count}{video.title}{count_part}"
                    logging.debug(f"Determined: {section} - {name} for {video.title}")
                    videos_by_section_name[(section, name)] = video
        return videos_by_section_name

    async def find_videos(self, starting_url):
        videos = await self.__find_videos(starting_url)
        return self.__get_video_names(videos)
