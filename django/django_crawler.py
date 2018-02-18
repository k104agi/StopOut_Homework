import re
import requests
from bs4 import BeautifulSoup
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()
from utils.models import Webtoon


class WebtoonCrawler:
    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id
        self.webtoon_name = None
        self.author = None
        self.description = None

    def get_webtoon_info(self):
        url_webtoon = 'https://comic.naver.com/webtoon/list.nhn?'
        params = {
            'titleId': self.webtoon_id,
        }
        response = requests.get(url_webtoon, params)
        source = response.text
        soup = BeautifulSoup(source, 'lxml')

        DIV_COMIC_INFO = soup.find('div', class_='comicinfo')

        DIV_COMIC_DETAIL = DIV_COMIC_INFO.find('div', class_='detail').prettify()

        PATTERN_FIND_WEBTOON_NAME = re.compile(r'<h2>\s+?\W\W(.*?)\s+?<span', re.S)
        webtoon_name = re.search(PATTERN_FIND_WEBTOON_NAME, DIV_COMIC_DETAIL).group(1)

        SPAN_WRT_NM = DIV_COMIC_INFO.find('span', class_='wrt_nm')

        author = SPAN_WRT_NM.get_text(strip=True)

        description = DIV_COMIC_INFO.find('p').get_text(" ")

        result = {
            'webtoon_id': self.webtoon_id,
            'webtoon_name': webtoon_name,
            'author': author,
            'description': description,
        }

        return result

    def get_episode_list(self):
        url_webtoon = 'https://comic.naver.com/webtoon/list.nhn?'
        params = {
            'titleId': self.webtoon_id,
        }
        response = requests.get(url_webtoon, params)
        source = response.text
        soup = BeautifulSoup(source, 'lxml')

        find_tr = soup.find_all('tr')[2:]

        result = list()

        for tr_element in find_tr:
            episode_title = tr_element.find('td', class_='title').find('a').get_text()
            rating = tr_element.find('div', class_='rating_type').strong.string
            created_date = tr_element.find('td', class_='num').get_text()
            result.append({
                'episode_title': episode_title,
                'rating': rating,
                'created_date': created_date,
            })

        return result


class WebtoonInfo:
    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id

    def webtoon_transfer(self):
        get_webtoon = WebtoonCrawler(self.webtoon_id)
        webtoon_info_dict = get_webtoon.get_webtoon_info()
        wt_instance = Webtoon(webtoon_id=webtoon_info_dict['webtoon_id'],
                              webtoon_name=webtoon_info_dict['webtoon_name'],
                              author=webtoon_info_dict['author'], description=webtoon_info_dict['description'])
        wt_instance.save()
        episode_list = get_webtoon.get_episode_list()

        for i in episode_list:
            wt_instance.episode_set.create(episode_title=i['episode_title'], rating=i['rating'],
                                           created_date=i['created_date']).save()
