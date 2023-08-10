import logging
from urllib.parse import urlparse

import pycookiecheat


class UrlUtils:


    @staticmethod
    def remove_path(url):
        parsed_url = urlparse(url)
        return f'{parsed_url.scheme}://{parsed_url.netloc}'


    @staticmethod
    def get_path(url):
        parsed_url = urlparse(url)
        return parsed_url.path


    @staticmethod
    def get_cookies(url):
        domain = UrlUtils.remove_path(url)
        logging.info(f"Getting Chrome Cookies for ${domain}")
        return pycookiecheat.chrome_cookies(domain)
