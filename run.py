import requests
from bs4 import BeautifulSoup
import pycookiecheat
from vimeo_downloader import Vimeo
import os
from urllib.parse import urljoin
from dataclasses import dataclass


@dataclass
class Video:
    video_url: str
    embedded_url: str
    parent_url: str
    title: str
    def get_filename(self):
        return self.parent_url.replace('/', '_') + '_' + self.title


root_url = ''
visited_urls = []
videos = []


def get_html(url, cookies):
    response = requests.get(url, cookies=cookies)
    return response.text if response.status_code == 200 else None


def find_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    a_tags = soup.find_all('a')
    hrefs = dict()
    for a_tag in a_tags:
        href = a_tag.get('href')
        if href is not None and href.startswith(root_url) and a_tag.string is not None:
            href = a_tag['href']
            hrefs[href] = a_tag.string
    return hrefs


def find_videos(html, url, previous_url_suffix):
    inner_videos = []
    soup = BeautifulSoup(html, 'html.parser')
    a_tags = soup.find_all('iframe')
    for a_tag in a_tags:
        h1_tag = a_tag.find_previous('h1')
        src = a_tag.get('src')
        inner_videos.append(Video(src, url, previous_url_suffix, h1_tag.string))
    return inner_videos


def populate_videos(url_suffix, previous_url_suffix, cookies):
    url = urljoin(root_url, url_suffix)
    if url not in visited_urls:
        print(f'URL: {url}')
        visited_urls.append(url)
        html = get_html(url, cookies)
        if html is not None:
            links = find_links(html)
            inner_videos = find_videos(html, url, previous_url_suffix)
            videos.extend(inner_videos)
            for link, title in links.items():
                populate_videos(link.lstrip(root_url), url_suffix, cookies)


def download_videos(cookies):
    for v in videos:
        file_name = v.get_filename()
        print(file_name)
        v = Vimeo(v.video_url, v.embedded_url)
        v.streams[0].download(download_directory='videos', filename=file_name)


cookies = pycookiecheat.chrome_cookies(root_url)
# populate_videos('/', None, cookies)
download_videos(cookies)