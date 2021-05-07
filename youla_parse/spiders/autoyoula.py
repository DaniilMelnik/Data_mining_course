import scrapy
from pymongo import MongoClient
import re

class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.collection = MongoClient()['youla_parse']['auto_youla']

    def _get_follow(self, response, selector_str, callback):
        for el in response.css(selector_str):
            url = el.attrib["href"]
            yield response.follow(url, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response,
            ".TransportMainFilters_brandsList__2tIkv " ".ColumnItemList_item__32nYI a.blackLink",
            self.brand_parse,
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response, ".Paginator_block__2XAPy .Paginator_button__u1e7D", self.brand_parse
        )

        yield from self._get_follow(
            response,
            "article.SerpSnippet_snippet__3O1t2 "
            "a.SerpSnippet_name__3F7Yu.SerpSnippet_titleText__1Ex8A.blackLink",
            self.car_parse,
        )

    def car_parse(self, response):
        author_id = re.findall(r'(?<=youlaId%22%2C%22).+?(?=%22%2C%22)',
                               response.xpath('/html/body/script[9]/text()').extract()[0])[1]
        data = {
            "url": response.url,
            "title": response.css(".AdvertCard_advertTitle__1S1Ak::text").extract_first(),
            'photos': [el.attrib['src'] for el in response.css('.PhotoGallery_block__1ejQ1 '
                                                               '.PhotoGallery_photoImage__2mHGn')],
            'features': {
                name: data
                for name, data in zip(response.css('.AdvertCard_specs__2FEHc '
                                                   '.AdvertSpecs_row__ljPcX '
                                                   '.AdvertSpecs_label__2JHnS::text').extract(),
                                      response.css('.AdvertCard_specs__2FEHc '
                                                   '.AdvertSpecs_data__xK2Qx::text, '
                                                   '.AdvertCard_specs__2FEHc '
                                                   '.blackLink::text').extract())
            },
            'description': response.css('.AdvertCard_description__2bVlR '
                                        '.AdvertCard_descriptionInner__KnuRi::text').extract(),
            'author': f'https://youla.ru/user/{author_id}'

        }
        self.collection.insert_one(data)
