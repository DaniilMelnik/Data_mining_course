import scrapy
from urllib.parse import urlparse, urljoin

class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/krasnodar/kvartiry/prodam']

    _xpath_selectors = {
        "pagination": '//div[contains(@class, "pagination-root")]//'
                      'span[contains(@class,"pagination-item")]/text()',
    }
    _xpath_data_selectors = {
        "title": '//h1[@data-qa="vacancy-title"]/text()',
        "salary": '//div[@class="vacancy-title"]//span[@data-qa="bloko-header-2"]/text()',
        "description": '//div[@data-qa="vacancy-description"]//text()',
        "key_skills": '//div[@class="vacancy-description"]//div[@class="bloko-tag-list"]//text()',
        "author": '//a[@data-qa="vacancy-company-name"]/@href',
    }

    def _get_follow(self, response, selector_str, callback):
        pagination_list = response.xpath(selector_str).extract()
        max_el = max([int(el) for el in pagination_list if el.isdigit()])
        for el in range(1, max_el + 1):
            yield response.follow(url=f'{response.url}?p={el}', callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response, self._xpath_selectors["pagination"], self.parse_flats)

    def parse_flats(self, response):
        print(1)
