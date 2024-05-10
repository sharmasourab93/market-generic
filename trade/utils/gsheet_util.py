import os
from dataclasses import dataclass
from json import loads
from typing import TypedDict

import gspread

MISSING_GSHEET_CREDS = (
    "Google Sheet Credentials: GSHEET_CRED & GSHEET_KEY as Environment variables."
)


class GSheetCredType(TypedDict):
    GSHEET_KEY: str
    GSHEET_CRED: str


@dataclass
class GSheetCreds:
    GSHEET_KEY: str = os.getenv("GSHEET_KEY")
    GSHEET_CRED: str = os.getenv("GSHEET_CRED")


class GSpreadManager:
    def __init__(self, gsheet_creds: GSheetCredType = GSheetCreds()):
        self.credentials = loads(gsheet_creds.get("GSHEET_CRED"))
        self.sheet_key = gsheet_creds.get("GSHEET_KEY")

        if self.credentials is None or self.sheet_key is None:
            raise ValueError(MISSING_GSHEET_CREDS)

        self.service_account = gspread.service_account_from_dict(self.credentials)
        self.gsheet = self.service_account.open_by_key(sheet_key)
        self.worksheets = {i.title: i for i in self.gsheet.worksheets()}

    def update_index_analysis_from_dict(
        self, index_report: dict, analysis_date: str, sheet_key: str = "index"
    ):
        if self.worksheets[sheet_key].acell("B2").value != analysis_date:
            for key, value in index_report.items():
                for i, j in enumerate(value):
                    self.worksheets[key].insert_row(j, i + 2)
