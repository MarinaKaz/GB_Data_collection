from bs4 import BeautifulSoup
import requests
import time
import json

ENDPOINT_URL = 'https://hh.ru/search/vacancy'

params_hh = {
    'text': 'python',
    'page': 0,
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Accept": "*/*",
}

FILE = 'hh.json'

class HHScrapper:
    def __init__(self, url, vacancy, page, headers):
        self.url = url
        self.vacancy = vacancy
        self.page_number = page
        self.headers = headers
        self.params = self.create_params()
        self.dic_vacancy = []

    def create_params(self):
        params_hh['text'] = self.vacancy
        return params_hh

    def get_html_string(self):
        try:
            response = requests.get(self.url, params=self.params, headers=self.headers)
            response.raise_for_status()
            time.sleep(1)
        except Exception as error:
            print(error)
            time.sleep(1)
            return None
        return response.text

    @staticmethod
    def get_dom(html_string):
        return BeautifulSoup(html_string, "html.parser")

    @staticmethod
    def get_salary(salary):
        if salary:
            salary = salary.text.replace('\u202f', '')
            salary = salary.split(' ')
            if salary[0] == 'от':
                min_salary = salary[1]
                max_salary = None
                currency = salary[2]
            else:
                if salary[0] == 'до':
                    min_salary = None
                    max_salary = salary[1]
                    currency = salary[2]
                else:
                    min_salary = salary[0]
                    max_salary = salary[2]
                    currency = salary[3]
        else:
            min_salary = None
            max_salary = None
            currency = None
        return min_salary, max_salary, currency

    def get_info(self, soup):
        vacancy_elements = soup.find_all('div', class_='vacancy-serp-item__layout')
        for element in vacancy_elements:
            title = element.find('a', class_='bloko-link').text.strip()
            salary = element.find('span', class_='bloko-header-section-3')
            min_salary, max_salary, currency = self.get_salary(salary)
            link = element.find('a', class_='bloko-link').get('href')
            vacancy = dict(title=title, min_salary=min_salary, max_salary=max_salary, currency=currency, link=link, source='https://hh.ru/')
            self.dic_vacancy.append(vacancy)

    def build_dic(self):
        for page in range(0, self.page_number):
            self.params['page'] = page
            response = self.get_html_string()
            soup = self.get_dom(response)
            self.get_info(soup)
        return self.dic_vacancy

    @staticmethod
    def save_info(data, path):
        with open(path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
        vacancy = input("Enter vacancy: ")
        page_number = int(input("Enter the last page number: "))
        scrapper_hh = HHScrapper(ENDPOINT_URL, vacancy, page_number, HEADERS)
        info_vacancy = scrapper_hh.build_dic()
        scrapper_hh.save_info(info_vacancy, FILE)
