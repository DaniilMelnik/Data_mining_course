import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from insta_parse.spiders.instagram import InstagramSpider

if __name__ == "__main__":
    dotenv.load_dotenv("../.env")
    crawler_settings = Settings()
    crawler_settings.setmodule("insta_parse.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(
        InstagramSpider, login=os.getenv("INST_LOGIN_2"), password=os.getenv("INST_PSWORD_2")
    )
    crawler_process.start()
