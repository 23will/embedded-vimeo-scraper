from bs4 import BeautifulSoup

class HtmlParser:
      

    def __init__(self, excluded_urls, url, raw_html):
        self.__soup = BeautifulSoup(raw_html, 'html.parser')
        self.__excluded_urls = excluded_urls
        self.__url = url


    def find_urls(self, visited_urls):
        a_tags = self.__soup.find_all('a')
        hrefs = []
        for a_tag in a_tags:
            href = a_tag.get('href')
            if href is not None and href not in visited_urls and not list(filter(lambda x: x in href, self.__excluded_urls)) and href.startswith(self.__url):
                print('HREF: ' + href)
                hrefs.append(href)
        return hrefs


    def find_video_urls_and_titles(self):
        link_and_titles = dict()
        iframes = self.__soup.find_all('iframe')
        for a_tag in iframes:
            h1_tag = a_tag.find_previous('h1')
            src = a_tag.get('src')
            if src is not None and src and 'vimeo' in src:
                tag_string = None if h1_tag is None else h1_tag.string
                link_and_titles[src] = None if tag_string is None else tag_string.strip()
        return link_and_titles
