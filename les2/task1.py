import time
import typing

import requests
from urllib.parse import urljoin
from pymongo import MongoClient
import bs4
import datetime


class GbBlogParse:
    def __init__(self, start_url, collection):
        self.time = time.time()
        self.start_url = start_url
        self.collection = collection
        self.done_urls = set()
        self.tasks = []
        start_task = self.get_task(self.start_url, self.parse_feed)
        self.tasks.append(start_task)
        self.done_urls.add(self.start_url)

    def _get_response(self, url, *args, **kwargs):
        if self.time + 0.9 < time.time():
            time.sleep(0.5)
        response = requests.get(url, *args, **kwargs)
        self.time = time.time()
        print(url)
        return response

    def _get_soup(self, url, *args, **kwargs):
        soup = bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")
        return soup

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        if url in self.done_urls:
            return lambda *_, **__: None
        self.done_urls.add(url)
        return task

    def task_creator(self, url, tags_list, callback):
        links = set(
            urljoin(url, itm.attrs.get("href")) for itm in tags_list if itm.attrs.get("href")
        )
        for link in links:
            task = self.get_task(link, callback)
            self.tasks.append(task)

    def parse_feed(self, url, soup):
        ul_pagination = soup.find("ul", attrs={"class": "gb__pagination"})
        self.task_creator(url, ul_pagination.find_all("a"), self.parse_feed)
        post_wrapper = soup.find("div", attrs={"class": "post-items-wrapper"})
        self.task_creator(
            url, post_wrapper.find_all("a", attrs={"class": "post-item__title"}), self.parse_post
        )

    def parse_post(self, url, soup):
        title_tag = soup.find("h1", attrs={"class": "blogpost-title"})
        data = {
            "url": url,
            "title": title_tag.text,
        }
        return data

    def run(self):
        for task in self.tasks:
            task_result = task()
            if isinstance(task_result, dict):
                self.save(task_result)

    def save(self, data):
        self.collection.insert_one(data)


class GbBNewsParse(GbBlogParse):
    def __init__(self, start_url, collection):
        super().__init__(start_url, collection)

    def parse_post(self, url, soup):
        title_tag = soup.find("h1", attrs={"class": "blogpost-title"})
        post_img = soup.find("article", attrs={"class": "col-sm-6"}).find("img")
        publish_date = soup.find("time", attrs={"class": "text-md text-muted m-r-md"})
        author = soup.find("div", attrs={"class": "row m-t"}).find(
            "div", attrs={"itemprop": "author"}
        )

        post_id = soup.find("comments").attrs.get("commentable-id")
        comments = requests.get(
            urljoin(
                url, f"/api/v2/comments?commentable_type=Post&commentable_id={post_id}&order=desc"
            )
        ).json()
        data = {
            "url": url,
            "title": title_tag.text,
            "post_image": post_img["src"],
            "date": datetime.datetime.fromisoformat(publish_date["datetime"]),
            "author": author.text,
            "author_url": urljoin(url, author.parent["href"]),
            "comments": self.parse_comment(comments),
        }
        return data

    def parse_comment(self, comments):
        comment_list = {
            f"comment_{i}": {
                "author_name": comment["comment"]["user"]["full_name"],
                "body": comment["comment"]["body"],
                "children": self.parse_comment(comment["comment"]["children"]),
            }
            for i, comment in enumerate(comments)
        }
        return comment_list


if __name__ == "__main__":
    collection = MongoClient()["gb_parse_20_04"]["gb_blog"]
    # parser = GbBlogParse("https://gb.ru/posts", collection)
    parser = GbBNewsParse("https://gb.ru/posts", collection)
    parser.run()
