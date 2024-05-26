import re
from typing import Tuple

import requests
from bs4 import BeautifulSoup


class HtmlParser:
    def __init__(self, url: str, headers: dict, matching_words: Tuple[str]):

        self.url = url
        self.headers = headers
        self.matching_words = matching_words

    def get_page_html(self) -> str:

        return requests.get(self.url, headers=self.headers).text

    def soup_parser(self) -> BeautifulSoup:

        data = self.get_page_html()
        soup = BeautifulSoup(data, "html.parser")

        return soup

    def get_table(self):
        soup = self.soup_parser()
        tables = soup.find_all("table")
        return self.iterate_table(tables)

    def iterate_table(self, tables, result: list = []):
        for table in tables:
            thead = table.find("thead")
            if self.check_for_theads_match(thead, self.matching_words):
                tbody = table.find("tbody")
                if tbody:
                    result = self.get_table_meta_data(tbody, result)

        return result

    def get_table_meta_data(self, tbody, result: list):
        for tr in tbody.find_all("tr"):
            tds = tr.find_all("td")
            sub_result = []
            for td in tds:
                text = td.get_text()
                a_tag = None if td.find("a") is None else td.find("a").get("href")
                sub_result.append(td.get_text() if a_tag is None else a_tag)
            result.append(sub_result)

        return result

    def get_latest_file(self):

        # Since the tags are arranged by descending order of time by default
        # We are popping the upper-most result.
        result = self.get_table()
        return result.pop(0)[-1]

    def check_for_theads_match(self, theads, matching_words) -> bool:
        result = list()

        if not theads:
            raise ValueError("Empty Header tags.")

        for th in theads.find_all("th"):
            result.append(
                any(re.search(th.get_text(), element) for element in matching_words)
            )

        return any(result)
