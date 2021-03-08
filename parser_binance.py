import requests
import json
from db import DB
from bs4 import BeautifulSoup


class Parser:
    def __init__(self):
        self.HOST = 'https://www.binance.com/'
        self.URL = 'https://www.binance.com/en/support/announcement/c-48?navId=48'
        # self.URL = 'http://binance-notify.ko4ki.ru/index.php'
        self.HEADERS = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 OPR/74.0.3911.160'
        }
        self.title = ''
        self.last_article = ''

        self.db = DB()

    def check_new_article(self):
        # Если в объекте не найден id последней записи, достаем его из базы
        if (self.last_article == None):
            self.last_article = self.db.get_last_article()[0][0]

        html = self.get_html(self.URL)
        articles = self.get_articles(html)

        # Обновляем значение последней записи
        if (articles[0]['code'] != self.last_article):
            self.last_article = articles[0]['code'];
            self.title = articles[0]['title'];
            self.db.update_last_article(self.last_article)
            return True

        return False

    def get_html(self, params=''):
        return requests.get(self.URL, headers=self.HEADERS, params=params)

    def get_articles(self, html):
        soup = BeautifulSoup(html.text, 'html.parser')
        tag_script = soup.find('script', id='__APP_DATA')
        data = json.loads(tag_script.contents[0])
        return data['routeProps']['b723']['navDataResource'][0]['articles']
