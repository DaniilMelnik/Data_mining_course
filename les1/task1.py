import json
import time
from pathlib import Path
import requests


"""
https://5ka.ru/special_offers/
- Извлеч все доступные данные о товарах
- Каждый товар положить в отдельный файл в формате JSON
"""


class Parse5ka:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    params = {
        "records_per_page": 20,
    }

    def __init__(self, star_url: str, save_path: Path):
        self.star_url = star_url
        self.save_path = save_path

    def _get_response(self, url, *args, **kwargs):
        while True:
            response = requests.get(url, *args, **kwargs)
            if response.status_code == 200:
                return response
            time.sleep(3)

    def run(self):
        for product in self._parse(self.star_url):
            file_path = self.save_path.joinpath(f"{product['id']}.json")
            self._save(product, file_path)

    def _parse(self, url: str):
        while url:
            time.sleep(0.1)
            response = self._get_response(url, headers=self.headers, params=self.params)
            data = response.json()
            url = data["next"]
            for product in data["results"]:
                yield product

    def _save(self, data: dict, file_path):
        file_path.write_text(json.dumps(data, ensure_ascii=False))


def get_save_path(dir_name):
    save_path = Path(__file__).parent.joinpath(dir_name)
    if not save_path.exists():
        save_path.mkdir()
    return save_path


if __name__ == "__main__":
    save_path = get_save_path("products")
    url = "https://5ka.ru/api/v2/special_offers/"
    parser = Parse5ka(url, save_path)
    parser.run()
