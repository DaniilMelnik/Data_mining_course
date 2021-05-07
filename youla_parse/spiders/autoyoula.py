import scrapy


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

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
        pass
        # data = {
        #     "url": response.url,
        #     "title": response.css(".AdvertCard_advertTitle__1S1Ak::text").extract_first(),
        # }
        # print(1)
