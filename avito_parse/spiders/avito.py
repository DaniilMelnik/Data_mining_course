import scrapy
from ..loaders import AvitoLoader


class AvitoSpider(scrapy.Spider):
    name = "avito"
    allowed_domains = ["avito.ru"]
    start_urls = ["https://www.avito.ru/ekaterinburg/kvartiry/prodam"]

    _xpath_selectors = {
        "pagination": '//div[contains(@class, "pagination-root")]//'
        'span[contains(@class,"pagination-item")]/text()',
        "flats": '//div[contains(@class, "iva-item-titleStep")]/a/@href',
    }
    _xpath_data_selectors = {
        "title": '//h1[@class="title-info-title"]/span/text()',
        "price": '//div[@class="item-price"]//span[@class="js-item-price"]/text()',
        "address": '//div[@itemprop="address"]//span/text()',
        "feature_names": '//ul[@class="item-params-list"]/li/span/text()',
        "feature_data": '//ul[@class="item-params-list"]/li/span/parent::*/text()',
        "author": '//a[contains(@class, "seller-info-avatar-image")]/@href',
    }

    def _get_follow(self, response, selector_str, callback):
        for itm in response.xpath(selector_str):
            yield response.follow(itm, callback=callback)

    def _get_follow_from_post(self, response, selector_str, callback):
        pagination_list = response.xpath(selector_str).extract()
        max_el = max([int(el) for el in pagination_list if el.isdigit()])
        for el in range(1, max_el + 1):
            yield response.follow(url=f"{response.url}?p={el}", callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow_from_post(
            response, self._xpath_selectors["pagination"], self.parse_flats
        )

    def parse_flats(self, response):
        yield from self._get_follow(response, self._xpath_selectors["flats"], self.parse_flat)

    def parse_flat(self, response):
        loader = AvitoLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in self._xpath_data_selectors.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
