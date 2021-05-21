import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from insta_handshake.spiders.insta_spider import InstaSpider

if __name__ == "__main__":
    users = ["magnus_carlsen", "arianagrande"]
    dotenv.load_dotenv(".env")
    crawler_settings = Settings()
    crawler_settings.setmodule("insta_handshake.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(
        InstaSpider,
        login=os.getenv("INST_LOGIN_2"),
        password=os.getenv("INST_PSWORD_2"),
        users=users,
    )
    crawler_process.start()
