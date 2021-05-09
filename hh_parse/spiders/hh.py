import scrapy
from ..loaders import hhLoader


class HhSpider(scrapy.Spider):
    name = "hh"
    allowed_domains = ["hh.ru"]
    start_urls = ["https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113"]
    _xpath_selectors = {
        "pagination": '//div[@data-qa="pager-block"]' '//a[@class="bloko-button"]/@href',
        "vacancies": '//div[@class="vacancy-serp"]//'
        'a[@data-qa="vacancy-serp__vacancy-title"]/@href',
    }
    _xpath_data_selectors = {
        "title": '//h1[@data-qa="vacancy-title"]/text()',
        "price": "//div[@data-target='advert-price']/text()",
        "photos": "//div[contains(@class, 'PhotoGallery_block')]//figure/picture/img/@src",
        "characteristics": "//div[contains(@class, 'AdvertCard_specs')]"
        "/div/div[contains(@class, 'AdvertSpecs_row')]",
        "description": "//div[@data-target='advert-info-descriptionFull']/text()",
        "author": '//body/script[contains(text(), "window.transitState = decodeURIComponent")]',
    }

    def _get_follow(self, response, selector_str, callback):
        for itm in response.xpath(selector_str):
            yield response.follow(itm, callback=callback)

    def parse(self, response, *args, **kwargs):

        yield from self._get_follow(response, self._xpath_selectors["pagination"], self.parse)

        yield from self._get_follow(
            response, self._xpath_selectors["vacancies"], self.vacancy_parse
        )

    def vacancy_parse(self, response):
        loader = hhLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in self._xpath_data_selectors.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
