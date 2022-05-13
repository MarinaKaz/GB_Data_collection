import requests
from lxml.html import fromstring
from datetime import datetime
from pymongo import MongoClient

URL = "https://yandex.ru/news/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Accept": "*/*",
}
ITEMS_XPATH = '//section[1]//div[contains(@class, "mg-grid__col")]'
HREF_XPATH = './/h2[contains(@class, "mg-card__title")]/a/@href'
TITLE_XPATH = './/h2[contains(@class, "mg-card__title")]/a/text()'
SOURCE_XPATH = './/span[contains(@class, "mg-card-source__source")]//a/text()'
TIME_XPATH = './/span[contains(@class, "mg-card-source__time")]/text()'
HOST = "localhost"
PORT = 27017
DB = "web_news"
COLLECTION = "news"

class News:
    def __init__(self):
        self.news_list = []

    @staticmethod
    def get_dom():
        r = requests.get(URL, headers=HEADERS)
        dom = fromstring(r.text)
        return dom

    @staticmethod
    def get_datetime(time):
        date_time = f'{str(datetime.now().date())} {time}'
        return datetime.strptime(date_time, '%Y-%m-%d %H:%M')

    def get_info(self, items):
        for item in items:
            info = {}
            info["href"] = item.xpath(HREF_XPATH)[0]
            info["title"] = item.xpath(TITLE_XPATH)[0].replace('\xa0', ' ')
            info["source"] = item.xpath(SOURCE_XPATH)[0]
            info["time"] = self.get_datetime(item.xpath(TIME_XPATH)[0])
            self.news_list.append(info)
            with MongoClient(HOST, PORT) as client:
                db = client[DB]
                collection = db[COLLECTION]
                collection.update_one(
                    {
                        'title': info['title'],
                    },
                    {
                        "$set": {
                            'href': info['href'],
                            'source': info["source"],
                            'time': info["time"]
                        }
                    },
                    upsert=True,
                )

    @staticmethod
    def read_db():
        with MongoClient(HOST, PORT) as client:
            db = client[DB]
            collection = db[COLLECTION]
            return list(collection.find())

    def collect(self):
        dom = self.get_dom()
        el = dom.xpath(ITEMS_XPATH)
        self.get_info(el)

if __name__ == "__main__":
        news = News()
        news.collect()