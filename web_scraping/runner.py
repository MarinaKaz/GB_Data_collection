import sys

from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.sjru import SJruSpider
from jobparser import settings

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)


    process = CrawlerProcess(settings=crawler_settings)

    job_kwargs = {"query": "data"}
    process.crawl(HhruSpider, **job_kwargs)
    process.crawl(SJruSpider, **job_kwargs)
    if "twisted.internet.reactor" in sys.modules: del sys.modules["twisted.internet.reactor"]
    process.start()
