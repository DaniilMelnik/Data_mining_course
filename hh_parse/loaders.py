from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join, Identity
from urllib.parse import urljoin
import re


def get_author_url(url, loader_context):
    return urljoin(loader_context.get("base_url"), url)


class hhLoader(ItemLoader):
    default_item_class = dict
    url_in = TakeFirst()
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_in = MapCompose(
        lambda line: map(lambda word: re.sub(r"[\xa0 ]", "", word, re.UNICODE), line.split())
    )
    salary_out = Join()
    description_out = Join("\n")
    key_skills_out = Identity()
    author_in = MapCompose(get_author_url)
    author_out = TakeFirst()


class AuthorLoader(ItemLoader):
    default_item_class = dict
    author_url_in = TakeFirst()
    author_url_out = TakeFirst()
    author_name_in = MapCompose(
        lambda line: map(lambda word: re.sub(r"[\xa0 ]", "", word, re.UNICODE), line.split())
    )
    author_name_out = Join()
    link_in = TakeFirst()
    link_out = TakeFirst()
    company_fields_out = Identity()
    description_out = Join("\n")
    other_vacancy_link_out = TakeFirst()
