import csv 
import os
import requests

from video import Video
from bs4 import BeautifulSoup


class VideoCsvWriter:


    def __init__(self, csv_dir, html_cache_dir, cookies, root_url, url, filename, missing_urls_filename) -> None:
        self.__csv_dir = csv_dir
        self.__html_cache_dir = html_cache_dir
        self.__cookies = cookies
        self.__url = url
        self.__root_url = root_url
        self.__visited_urls = []
        self.__videos = []
        self.__filename = filename
        self.__missing_urls_filename = missing_urls_filename


    def __create_path_if_not_exists(self, dir):
        output_path = os.path.join(os.getcwd(), dir)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        return output_path


    def __get_html_cache_path(self, url):
        suffix = url.replace(self.__root_url, '')
        print(f'Stripping {self.__root_url} from {url} = {suffix}')
        html_filename = suffix.replace('/','_') + '.html'
        output_path = self.__create_path_if_not_exists(self.__html_cache_dir)
        return os.path.join(output_path, html_filename)


    def __get_html(self, url):
        html_cache_path = self.__get_html_cache_path(url)
        if os.path.exists(html_cache_path):
            with open(html_cache_path, 'r') as f:
                print ('Reading html from ' + html_cache_path)
                return f.read()
        else:
            response = requests.get(url, cookies=self.__cookies)
            html = response.text if response.status_code == 200 else None
            if html is not None:
                with open(html_cache_path, 'w') as f:
                    f.write(html)
            return html


    def __safe_decompose(self, tag):    
        if tag is not None:
            tag.decompose()


    def __find_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        #remove header and footer as they contain unnecessary links
        self.__safe_decompose(soup.footer)
        self.__safe_decompose(soup.header)

        a_tags = soup.find_all('a')
        hrefs = dict()
        for a_tag in a_tags:
            href = a_tag.get('href')
            if href is not None and href.startswith(self.__root_url) and href not in self.__visited_urls and a_tag.string is not None:
                href = a_tag['href']
                hrefs[href] = a_tag.string
        return hrefs


    def __find_videos(self, html, csv_writer, url, previous_url, title):
        inner_videos = []
        soup = BeautifulSoup(html, 'html.parser')
        a_tags = soup.find_all('iframe')
        for a_tag in a_tags:
            h1_tag = a_tag.find_previous('h1')
            src = a_tag.get('src')
            video = Video(h1_tag.string, url, src, title, previous_url)
            csv_writer.writerow(video)
            self.__stream.flush()
            print(f'Found video: ${video.title}')
            inner_videos.append(video)
        return inner_videos


    def __populate_videos(self, url, csv_writer, previous_url=None, title=None):
        if url not in self.__visited_urls:
            print(f'URL: {url}')
            self.__visited_urls.append(url)
            html = self.__get_html(url)
            if html is not None:
                inner_videos = self.__find_videos(html, csv_writer, url, previous_url, title)
                self.__videos.extend(inner_videos)
                links = self.__find_links(html)
                for link, title in links.items():
                    self.__populate_videos(link, csv_writer, url, title)


    def __get_urls_without_videos(self):
        video_urls = list(map(lambda v: v.url, self.__videos))        
        video_parent_urls = list(map(lambda v: v.parent_url, self.__videos))        
        return list(filter(lambda u: u not in video_urls and u not in video_parent_urls, self.__visited_urls))


    def ___write_missing_video_urls_csv(self):
        urls = self.__get_urls_without_videos()
        csv_dir = self.__create_path_if_not_exists(self.__csv_dir)
        csv_path = os.path.join(csv_dir, self.__missing_urls_filename)
        with open(csv_path, "w") as stream:
            writer = csv.writer(stream)
            for url in urls:
                writer.writerow([url])
    

    def write_videos_to_csv(self):
        csv_dir = self.__create_path_if_not_exists(self.__csv_dir)
        csv_path = os.path.join(csv_dir, self.__filename)
        with open(csv_path, "w") as stream:
            self.__stream = stream
            csv_writer = csv.writer(stream)
            self.__populate_videos(self.__url, csv_writer)
        self.___write_missing_video_urls_csv()