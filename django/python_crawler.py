import os
import re
import requests

from bs4 import BeautifulSoup

# 절대경로로 나타냄
PATH_MODULE = os.path.abspath(__file__)
# 루트 디렉토리 설정
ROOT_DIR = os.path.dirname(PATH_MODULE)
# 데이터 저장 디렉토리 설정
DATA_DIR = os.path.join(ROOT_DIR, 'data')


class Webtoon:
    """
    하나의 에피소드에 대한 정보를 갖도록 함
    """

    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id
        self.webtoon_name = None
        self.author = None
        self.description = None

    def get_webtoon_info(self, refresh_html=False):
        os.makedirs(DATA_DIR, exist_ok=True)
        FILE_PATH = os.path.join(DATA_DIR, f'webtoon_{self.webtoon_id}.html')

        try:
            file_mode = 'wt' if refresh_html else 'xt'
            with open(FILE_PATH, file_mode, encoding='utf8') as f:
                url_webtoon = 'https://comic.naver.com/webtoon/list.nhn?'
                params = {
                    'titleId': self.webtoon_id,
                }

                response = requests.get(url_webtoon, params)
                source = response.text
                f.write(source)
        except FileExistsError:
            print(f'"{FILE_PATH}" file already exists!')

        source = open(FILE_PATH, 'rt', encoding='utf8').read()
        soup = BeautifulSoup(source, 'lxml')

        result = []

        DIV_COMIC_INFO = soup.find('div', class_='comicinfo')
        DIV_COMIC_DETAIL = DIV_COMIC_INFO.find('div', class_='detail').prettify()

        PATTERN_FIND_WEBTOON_NAME = re.compile(r'<h2>\s+?\W\W(.*?)\s+?<span', re.S)
        webtoon_name = re.search(PATTERN_FIND_WEBTOON_NAME, DIV_COMIC_DETAIL).group(1)

        SPAN_WRT_NM = DIV_COMIC_INFO.find('span', class_='wrt_nm')

        author = SPAN_WRT_NM.get_text(strip=True)

        description = DIV_COMIC_INFO.find('p').get_text(" ")

        result.append({
            'webtoon name': webtoon_name,
            'author': author,
            'description': description,
        })

        print(f'웹툰 이름 : {webtoon_name} | 작가 : {author} | 설명 : {description}')
        return result

    def get_episode_list(self):
        result = list()

        FILE_PATH = os.path.join(DATA_DIR, f'webtoon_{self.webtoon_id}.html')

        source = open(FILE_PATH, 'rt', encoding='utf8').read()

        soup = BeautifulSoup(source, 'lxml')

        find_tr = soup.find_all('tr')[2:]

        for tr_element in find_tr:
            episode_title = tr_element.find('td', class_='title').find('a').get_text()
            episode_rank = tr_element.find('div', class_='rating_type').strong.string
            episode_date = tr_element.find('td', class_='num').get_text()

            result.append([
                episode_title,
                episode_rank,
                episode_date,
            ])
            print(f'제목 : {episode_title} | 별점 : {episode_rank}| 날짜 : {episode_date}')

        return result


a = Webtoon(703835)
a.get_webtoon_info()
a.get_episode_list()
