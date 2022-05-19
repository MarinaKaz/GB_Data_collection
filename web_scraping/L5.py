import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

DRIVER_PATH = "../selenium_drivers/chromedriver.exe"
URL = "https://vk.com/tokyofashion"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Accept": "*/*",
}

HOST = "localhost"
PORT = 27017
DB = "vk"
COLLECTION = "tokyofashion"

class ScrapperVK:
    def __init__(self, line):
        self.post = []
        self.str_input = line
        self.driver, self.actions = self.get_driver()

    @staticmethod
    def get_driver():
        options = Options()
        options.add_argument("start-maximized")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(URL)
        actions = ActionChains(driver)
        return driver, actions

    def close_popup(self):
        time.sleep(2)
        bottom_page = self.driver.find_element_by_id("page_search_posts")
        self.actions.move_to_element(bottom_page).perform()
        close = self.driver.find_element_by_class_name("UnauthActionBox__close")
        close.click()

    def find_posts(self):
        cursor = self.driver.find_element_by_id("wall_tabs")
        self.actions.move_to_element(cursor).perform()
        time.sleep(3)
        button_search = self.driver.find_element_by_css_selector("a.ui_tab_search")
        button_search.click()
        time.sleep(3)
        search_wall = self.driver.find_element_by_class_name("ui_search_field")
        search_wall.clear()
        search_wall.send_keys(self.str_input)
        search_wall.send_keys(Keys.ENTER)
        for i in range(3):
            time.sleep(3)
            last_post = self.driver.find_elements_by_class_name("post--withPostBottomAction")
            if not last_post:
                break
            self.actions.move_to_element(last_post[-1]).perform()

        html = self.driver.page_source
        self.driver.quit()
        return html

    @staticmethod
    def extract_posts(html):
        soup = BeautifulSoup(html, "html.parser")
        posts = soup.find_all('div', class_='post--withPostBottomAction')
        for post in posts:
            date = post.find('span', class_='rel_date').text.replace('\xa0', ' ')
            content = post.find('div', class_='wall_post_text').text
            link = 'https://vk.com' + post.find('a', class_='post_link').get('href')
            likes = post.find('div', class_='PostButtonReactions__title').text
            shares = post.find('div', class_='_share').get('data-count')
            views = post.find('div', class_='like_views--inActionPanel')
            if views:
                views = views.find('span', class_='_views').text
            else:
                views = None
            with MongoClient(HOST, PORT) as client:
                db = client[DB]
                collection = db[COLLECTION]
                collection.update_one(
                    {
                        'link': link,
                    },
                    {
                        "$set": {
                            'date': date,
                            'content': content,
                            'likes': likes,
                            'shares': shares,
                            'views': views,
                        }
                    },
                    upsert=True,
                )

    def collect(self):
        self.close_popup()
        html = self.find_posts()
        self.extract_posts(html)

if __name__ == "__main__":
    try:
        str_input = input("Enter line for search: ")
        result_vk = ScrapperVK(str_input)
        result_vk.collect()
    except Exception as e:
        print(e)
