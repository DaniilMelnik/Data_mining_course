from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join, Identity
import re


class AvitoLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()

    title_in = MapCompose(
        lambda line: map(lambda word: re.sub(r"[\xa0 ]", "", word, re.UNICODE), line.split())
    )
    title_out = Join()

    price_in = MapCompose(lambda price: float(price.replace(" ", "")))
    price_out = TakeFirst()

    address_in = Identity()
    address_out = Join()

    feature_names_in = Identity()
    feature_names_out = Identity()
    feature_data_in = Identity()
    feature_data_out = Identity()

    author_out = TakeFirst()

    # title_out = TakeFirst()
    # salary_in = MapCompose(
    #     lambda line: map(lambda word: re.sub(r"[\xa0 ]", "", word, re.UNICODE), line.split())
    # )
    # salary_out = Join()
    # description_out = Join("\n")
    # key_skills_out = Identity()
    # author_in = MapCompose(get_author_url)
    # author_out = TakeFirst()
