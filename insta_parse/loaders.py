from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join, Identity


class InstagramLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
