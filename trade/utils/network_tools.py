import csv
import os
from abc import ABC
from io import BytesIO
from typing import Optional
from urllib.parse import urlparse
from zipfile import ZipFile

import requests
from pandas import DataFrame, read_csv, read_excel
from requests import Session
from requests.exceptions import ConnectionError, InvalidURL, ReadTimeout

CHUNK_SIZE = 1024
INVALID_URL = "URL: {0}, Status Code:{1}"


class DownloadTools(ABC):
    def get_cookies(self, base_url: str, headers: dict, timeout: int = 5) -> dict:

        url = self.extract_domain(base_url)

        session = Session()
        try:
            request = session.get(url, headers=headers, timeout=timeout)

        except (ConnectionError, ReadTimeout) as msg:
            self.logger.debug(msg)
            return self.get_cookies(url, headers)

        return dict(request.cookies)

    def get_request_api(
        self, url: str, headers: dict, cookies: Optional[dict] = None, **kwargs
    ):

        cookies = self.get_cookies(url, headers)
        result = requests.get(url, headers=headers, cookies=cookies, **kwargs)

        if result.status_code == 200:
            return result

        elif result.status_code == 404:
            raise InvalidURL(INVALID_URL.format(url, result.status_code))

        return self.get_request_api(url, headers, cookies)

    def extract_domain(self, url: str) -> str:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        return "https://" + domain

    def download_data(self, url: str, headers: str) -> BytesIO:
        """
        For a given url and file name
        download data to the provided filename/path.
        """
        domain = self.extract_domain(url)
        cookies = self.get_cookies(domain, headers)
        response = self.get_request_api(url, headers, cookies)

        bytes_obj = BytesIO(response.content)

        self.logger.debug("Response received.")

        if self.is_zip(bytes_obj):
            bytes_obj = self.unzip(bytes_obj)

        result = self.read_from_buffer(bytes_obj)

        return result

    def unzip(self, source_buffer: BytesIO) -> bytes:
        """
        Extracts content of the zip file and
        returns a reference to the extracted CSV file.
        :param source_buffer: Path to the source Zip Bytes.
        :return: str
        """
        zip_file = ZipFile(source_buffer)
        file_name = zip_file.namelist()[0]
        csv_buffer = BytesIO(zip_file.read(file_name))
        zip_file.close()

        return csv_buffer

    def is_zip(self, byte_obj: BytesIO):
        zip_signature = b"PK\x03\x04"

        return byte_obj.getvalue().startswith(zip_signature)

    def is_xlsx(self, byte_obj: BytesIO) -> bool:
        xlsx_signature = b"PK\x03\x04"

        return byte_obj.startswith(xlsx_signature)

    def is_csv(self, byte_obj: BytesIO):
        try:
            content = byte_obj.getvalue().decode("utf-8")
            dialect = csv.Sniffer().sniff(content)
            # TODO: Handle _csv.Error here.
            return True

        except (UnicodeDecodeError, csv.Error):
            return False

    def read_csv(self, bytes_obj: BytesIO) -> DataFrame:
        return read_csv(bytes_obj)

    def read_xlsx(self, bytes_obj: BytesIO) -> DataFrame:
        return read_excel(bytes_obj)

    def read_from_buffer(self, bytes_obj: BytesIO):
        if self.is_csv(bytes_obj):
            return self.read_csv(bytes_obj)

        elif self.is_xlsx(bytes_obj):
            return self.read_xlsx(bytes_obj)

        else:
            # TODO: Handle this case if need arises.
            pass
