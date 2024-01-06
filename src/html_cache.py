import logging
import os
from dataclasses import dataclass
from url_utils import UrlUtils
from file_utils import FileUtils
import requests


@dataclass
class HtmlCache:
    html_cache_dir: str
    cookies: dict

    def __get_html_cache_path(self, url):
        path = UrlUtils.get_path(url)
        html_filename = path.replace("/", "_") + ".html"
        output_path = FileUtils.create_dir_if_not_exists(self.html_cache_dir)
        return os.path.join(output_path, html_filename)

    def get_html(self, url):
        html_cache_path = self.__get_html_cache_path(url)
        if os.path.exists(html_cache_path):
            with open(html_cache_path, "r") as f:
                logging.debug(f"Reading HTML from cache {html_cache_path}")
                return f.read()
        else:
            logging.debug(f"Retrieving HTML from {url}")
            response = requests.get(url, cookies=self.cookies)
            html = response.text if response.status_code == 200 else None
            if html is not None:
                with open(html_cache_path, "w") as f:
                    f.write(html)
            return html
