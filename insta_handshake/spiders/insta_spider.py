import scrapy
import json
from urllib.parse import urlencode
from ..items import InstaFollow


class InstaSpider(scrapy.Spider):
    name = "insta_spider"
    allowed_domains = ["instagram.com", "i.instagram.com"]
    start_urls = ["https://www.instagram.com/accounts/login/"]
    _login_url = "https://www.instagram.com/accounts/login/ajax/"
    _follow_url = "https://www.instagram.com/graphql/query/"

    def __init__(self, login, password, users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.users = users

    def parse(self, response, *args, **kwargs):
        print(1)
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                url=self._login_url,
                method="POST",
                callback=self.parse,
                formdata={"username": self.login, "enc_password": self.password},
                headers={"x-csrftoken": js_data["config"]["csrf_token"]},
            )
        except AttributeError:
            if response.json()["authenticated"]:
                for user in self.users:
                    yield response.follow(
                        url=f"https://www.instagram.com/{user}/", callback=self.user_parse
                    )
            else:
                raise Exception(f"{response.url} mot supported")

    def user_parse(self, response):
        print(1)
        js_data = self.js_data_extract(response)
        user_id = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["id"]
        follow = InstFollow(user_id)
        yield response.follow(
            f"{self._follow_url}?{urlencode(follow.paginate_params())}",
            callback=self._api_follow_parse,
            cb_kwargs={"user_id": user_id},
        )

    def _api_follow_parse(self, response, user_id):
        data = response.json()
        inst_follow = InstFollow(user_id, data["data"]["user"])
        yield from inst_follow.get_post_items()
        yield response.follow(
            f"{self._follow_url}?{urlencode(inst_follow.paginate_params())}",
            callback=self._api_follow_parse,
            cb_kwargs={"user_id": user_id},
        )

    def js_data_extract(self, response):
        script = response.xpath(
            '//script[contains(text(), "window._sharedData =")]/text()'
        ).extract_first()
        json_data = json.loads(script.replace("window._sharedData = ", "")[:-1])
        return json_data


class InstFollow:
    query_hash = "3dec7e2c57367ef3da3d987d89f9dbc8"

    def __init__(self, user_id, user_data=None):
        self.user_id = user_id
        self.user_data = user_data

    def paginate_params(self):
        url_query = {
            "query_hash": self.query_hash,
            "variables": json.dumps(
                {
                    "id": self.user_id,
                    "include_reel": True,
                    "fetch_mutual": False,
                    "first": 12,
                    "after": self.user_data["edge_follow"]["page_info"]["end_cursor"]
                    if self.user_data
                    else None,
                }
            ),
        }
        return url_query

    def get_post_items(self):
        for edge in self.user_data["edge_follow"]["edges"]:
            yield InstaFollow(user_id=edge["node"]["id"], user_name=edge["node"]["full_name"])
