import scrapy
from ..loaders import hhLoader, AuthorLoader
from urllib.parse import urlparse


class HhSpider(scrapy.Spider):
    name = "hh"
    allowed_domains = ["hh.ru"]
    start_urls = ["https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113"]
    _xpath_selectors = {
        "pagination": '//div[@data-qa="pager-block"]' '//a[@class="bloko-button"]/@href',
        "vacancies": '//div[@class="vacancy-serp"]//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
        "vacancy_author": '//a[@data-qa="vacancy-company-name"]/@href',
        "company_vacancy": '//a[@data-qa="employer-page__employer-vacancies-link"]/@href',
    }
    _xpath_data_selectors = {
        "title": '//h1[@data-qa="vacancy-title"]/text()',
        "salary": '//div[@class="vacancy-title"]//span[@data-qa="bloko-header-2"]/text()',
        "description": '//div[@data-qa="vacancy-description"]//text()',
        "key_skills": '//div[@class="vacancy-description"]//div[@class="bloko-tag-list"]//text()',
        "author": '//a[@data-qa="vacancy-company-name"]/@href',
    }

    _xpath_author_data_selectors = {
        "author_name": '//div[@class="company-header"]//span[@class="company-header-title-name"]/text()',
        "link": '//div[@class="employer-sidebar"]//a[@class="g-user-content"]/@href',
        "company_fields": '//div[contains(text(), "Сферы деятельности")]/parent::*//p/text()',
        "description": '//div[@class="company-description"]//p/text()',
        "other_vacancy_link": '//a[@data-qa="employer-page__employer-vacancies-link"]/@href',
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
        url = response.url
        loader = hhLoader(response=response)
        loader.add_value("url", url)
        loader.context["base_url"] = self.get_base_url(url)
        for key, xpath in self._xpath_data_selectors.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()

        yield from self._get_follow(
            response, self._xpath_selectors["vacancy_author"], self.vacancy_author_parse
        )

    def vacancy_author_parse(self, response):
        loader = AuthorLoader(response=response)
        loader.add_value("author_url", response.url)
        for key, xpath in self._xpath_author_data_selectors.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()

        yield from self._get_follow(
            response, self._xpath_selectors["company_vacancy"], self.vacancy_parse
        )

    @staticmethod
    def get_base_url(url):
        url_parse_result = urlparse(url)
        return f"{url_parse_result.scheme}://{url_parse_result.netloc}"
