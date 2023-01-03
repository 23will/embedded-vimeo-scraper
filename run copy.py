import requests
from bs4 import BeautifulSoup
import pycookiecheat
import os
from urllib.parse import urljoin

root_url = ''
use_html_cache = True


def check_response_is_ok(response, action):
    if(response.status_code != 200):
        raise RuntimeError(f'Failed {action}, {str(response.status_code)}: {str(response.text)}')


def get_html_cache_path(url_suffix):
    output_path = os.path.join(os.getcwd(), 'html_cache', url_suffix)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    return os.path.join(output_path, 'index.html') 


def get_video_cache_path(url_suffix):
    output_path = os.path.join(os.getcwd(), 'videos', url_suffix)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    return output_path


def write_html(path, html):
    with open(path, 'w') as f:
       f.write(html)


def read_root_html(path):
    print(f'Reading html from {path}')
    with open(path, 'r') as f:
        return f.read()


def get_cookies():
     return pycookiecheat.chrome_cookies(root_url)


def get_html(url, cookies):
    response = requests.get(url, cookies=cookies)
    check_response_is_ok(response, 'get html')
    return response.text


def get_html_from_cache(html_cache_path, url_suffix, use_cache):
    if os.path.exists(html_cache_path) and use_cache:
        return read_root_html(html_cache_path)
    else:
        cookies = get_cookies()
        print('getting root html')
        html = get_html(urljoin(root_url,url_suffix), cookies)
        write_html(html_cache_path, html)
        return html


def find_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    a_tags = soup.find_all('a')
    hrefs = dict()
    for a_tag in a_tags:
        href = a_tag.get('href')
        if href is not None and href.startswith(root_url) and a_tag.string is not None:
            href = a_tag['href']
            # print(a_tag.string)
            # print(href)
            hrefs[href] = a_tag.string
    return hrefs

def download_videos(url_suffix):
    html_cache_path = get_html_cache_path(url_suffix)
    html = get_html_from_cache(html_cache_path, use_html_cache)
    links = find_links(html)
    for link, title in links.items():
        print(f'{title}: {link}')
        get_html(link.lstrip(root_url))

download_videos('')
#pass url and get links and videos
#recurse

# def get_root_html(output_path, root_html_path):
    
    # url = root_url + ''

    # response = requests.get(url, cookies=cookies)

    # html = response.text

    # if not os.path.exists(output_path):
    #     os.makedirs(output_path)


    # return html







# html = get_root_html(output_path, root_html_path) if not os.path.exists(root_html_path) else read_root_html(root_html_path)


# def login():
#     url = root_url + '/my-account/'
#     payload = {
#         'username': 'sjwwill@gmail.com',
#         'password': 'ISpring12Lotu',
#         'login': 'Log in'
#     }
#     response = requests.post(url, data=payload)
#     check_response_is_ok(response, 'log in')
#     cookie = response.cookies.get('')
    
#     return cookie

