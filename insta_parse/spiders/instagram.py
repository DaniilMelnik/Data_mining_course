import scrapy
import json
from urllib.parse import urlencode
from ..loaders import InstagramLoader
import datetime


class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["instagram.com", "i.instagram.com"]
    start_urls = ["https://www.instagram.com/accounts/login/"]
    _login_url = "https://www.instagram.com/accounts/login/ajax/"
    _tags_url = "/explore/tags/"
    _pagination_url = "https://i.instagram.com/api/v1/tags/{0}/sections/"
    tags = ["python", "html"]

    def __init__(self, login, password, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password

    def parse(self, response, *args, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                url=self._login_url,
                method="POST",
                callback=self.parse,
                formdata={"username": self.login, "enc_password": self.password,},
                headers={"x-csrftoken": js_data["config"]["csrf_token"]},
            )
        except AttributeError:
            if response.json()["authenticated"]:
                for tag in self.tags:
                    yield response.follow(
                        url=f"{self._tags_url}{tag}/",
                        callback=self.page_tag_parse,
                        cb_kwargs={"tag": tag},
                    )
            else:
                raise Exception(f"{response.url} mot supported")

    def page_tag_parse(self, response, tag):
        post_codes = []
        try:
            js_data = self.js_data_extract(response)

        except AttributeError:
            js_data = response.json()
            for i in js_data["sections"]:
                for j in i["layout_content"]["medias"]:
                    for k in j.values():
                        post_codes.append(k["code"])
        else:

            def append_code(items):
                for item in items["layout_content"]["medias"]:
                    post_codes.append(item["media"]["code"])

            for i in js_data["entry_data"]["TagPage"]:
                for j in i["data"]["top"]["sections"]:
                    append_code(j)
                for j in i["data"]["recent"]["sections"]:
                    append_code(j)

        for post_code in post_codes:
            yield scrapy.Request(
                url=f"https://www.instagram.com/p/{post_code}/",
                callback=self.post_parse,
                cb_kwargs={"tag": tag},
            )

        yield from self.paginate(response, tag)

    def paginate(self, response, tag):
        js_data = self.js_data_extract(response)
        formdata = {
            "include_persistent": "0",
            "max_id": str(js_data["entry_data"]["TagPage"][0]["data"]["recent"]["next_max_id"]),
            "page": str(js_data["entry_data"]["TagPage"][0]["data"]["recent"]["next_page"]),
            "surface": "grid",
            "tab": "recent",
        }

        next_media_ids = js_data["entry_data"]["TagPage"][0]["data"]["recent"]["next_media_ids"]
        if next_media_ids:
            formdata.update({"next_media_ids": list(map(str, next_media_ids))})

        yield scrapy.FormRequest(
            url=self._pagination_url.format(tag),
            method="POST",
            callback=self.page_tag_parse,
            cb_kwargs={"tag": tag},
            formdata=formdata,
            headers={
                "x-csrftoken": js_data["config"]["csrf_token"],
                "x-ig-app-id": "936619743392459",
            },
        )

    def post_parse(self, response, tag):
        additional_js_data = self.additional_data_extract(response)
        image_url = additional_js_data["graphql"]["shortcode_media"]["display_resources"][0]["src"]
        loader = InstagramLoader(response=response)
        data = {
            "tag": tag,
            "url": response.url,
            "photos": [image_url],
            "date_parse": datetime.datetime.utcnow(),
        }
        for key, val in data.items():
            loader.add_value(key, val)
        yield loader.load_item()

    def js_data_extract(self, response):
        script = response.xpath(
            '//script[contains(text(), "window._sharedData =")]/text()'
        ).extract_first()
        json_data = json.loads(script.replace("window._sharedData = ", "")[:-1])
        return json_data

    def additional_data_extract(self, response):
        script = response.xpath(
            '//script[contains(text(), "window.__additionalDataLoaded(")]/text()'
        ).extract_first()
        json_data = json.loads(
            script.replace(
                f'window.__additionalDataLoaded(\'/p/{response.url.rsplit("/", maxsplit=2)[1]}/\',',
                "",
            )[:-2]
        )
        return json_data
