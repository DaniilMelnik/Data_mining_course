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
