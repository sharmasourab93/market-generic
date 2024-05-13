import json
from abc import ABC
from pathlib import Path
from typing import Dict, List, TypedDict, Union

from trade.utils import operations

ACCEPTED_SUFFIXES = (".json", ".yml")
FILE_NOT_FOUND = "File Not found."
INVALID_FILE = "Invalid Config file provided."
MARKET_SUB_TYPE = Union[List[str], Dict[str, str]]
MARKET_TYPE = Dict[str, Union[List[str], MARKET_SUB_TYPE]]
EXTRACT_MAP_TYPE = Dict[str, Union[str, Union[List[str], Dict[str, str]]]]


class APIConfig(ABC):

    def __init__(self, config: Union[MARKET_TYPE, Path]):
        if isinstance(config, str):
            config = Path(config)

        if not config.exists():
            raise FileNotFoundError(FILE_NOT_FOUND)

        if config.suffix.lower() not in ACCEPTED_SUFFIXES:
            raise ValueError(INVALID_FILE)

        self._config = config
        self._data_map = self._method_map_to_suffix(self._config)

        for iterator in self._extract_all_keys(self._data_map):
            for key, value in iterator.items():
                setattr(self, key, value)

    def _extract_all_keys(self, data) -> EXTRACT_MAP_TYPE:
        capitalized_keys = list()
        for key, value in data.items():
            if key.isupper():

                if isinstance(value, dict) and key.isupper():
                    capitalized_keys.extend(self._extract_all_keys(value))

                elif isinstance(value, list) and key.isupper():
                    for item in value:
                        if isinstance(item, dict):
                            capitalized_keys.extend(self._extract_all_keys(value))

                if key.isupper() or not operations.containing_sub_string("date", key):
                    modified_key = key.replace("-", "_").lower()
                    capitalized_keys.append({modified_key: value})

        return capitalized_keys

    def _read_json(self, file: str, mode: str = "r") -> MARKET_TYPE:

        with open(file, mode) as file:
            data = json.load(file)

        return data

    def _read_yml(self, file: str, mode: str = "r") -> MARKET_TYPE:
        with open(file, mode) as file:
            data = yaml.safe_load(file)

        return data

    def _method_map_to_suffix(self, config: str) -> MARKET_TYPE:
        if config.suffix.lower() == ".json":
            return self._read_json(config)
        else:
            return self._read_yml(config)
