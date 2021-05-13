# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from .settings import BOT_NAME
from pymongo import MongoClient


class AvitoParsePipeline:
    def process_item(self, item, spider):
        return item


class MergeFeaturesPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        adapter["feature_data"] = [el for el in adapter["feature_data"] if el != " "]
        adapter["features"] = {
            k: v for k, v in zip(adapter["feature_names"], adapter["feature_data"])
        }
        del adapter["feature_names"]
        del adapter["feature_data"]
        return item


class MongoPipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client[BOT_NAME]

    def process_item(self, item, spider):
        self.db[spider.name].insert_one(item)
        return item
