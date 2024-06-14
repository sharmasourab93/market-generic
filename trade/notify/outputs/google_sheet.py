import json
import os

import gspread

from trade.notify.outputs.output_generics import OutputGenerics

CREDS_NOT_SET = "Credentials and Credetial key for Google Sheet notset."


class GoogleSheetBot(OutputGenerics):

    @classmethod
    def communicate_data(
        cls,
        index_report: dict,
        analysis_date: str,
        sheet_key: str,
        credentials: str = os.getenv("GSHEET_CRED", None),
        cred_key: str = os.getenv("GSHEET_KEY", None),
    ):

        gsheet_obj = cls(credentials, sheet_key)

        if credentials and cred_key:
            raise ValueError(CREDS_NOT_SET)

        match sheet_key:
            case "index":
                gsheet_obj.update_index_analysis_from_dict(index_report, analysis_date)
            case _:
                raise ValueError(f"Invalid Key selection. - {sheet_key}")

    def __init__(self, credentials: str, cred_key: str):
        self.credentials = json.loads(credentials)
        self.sheet_key = cred_key
        self.service_account = gspread.service_account_from_dict(self.credentials)
        self.gsheet = self.service_account.open_by_key(cred_key)
        self.worksheets = {i.title: i for i in self.gsheet.worksheets()}

    def update_index_analysis_from_dict(self, index_report: dict, analysis_date: str):
        if self.worksheets[sheet_key].acell("B2").value != analysis_date:
            for key, value in index_report.items():
                for i, j in enumerate(value):
                    self.worksheets[key].insert_row(j, i + 2)
