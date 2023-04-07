__all__ = [
    "DATE_VALUE",
    "FOLDER_DIRECTORY",
    "DATA_FILE_DIRECTORY",
    "EXCEL_FILE_NAME",
    "EXCEL_FILE_MATCH",
    "VALID_NUMERIC_MATCH",
    "NAN",
]

import os
import re
import numpy as np


FOLDER_DIRECTORY = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DATA_FILE_DIRECTORY = os.path.join(FOLDER_DIRECTORY, "data")
EXCEL_FILE_NAME = "Logans_Dam_Water_Quality_Programmer.xlsx"
DATE_VALUE = re.compile(r"\d{1,2}(\.\d{2}){2}")
EXCEL_FILE_MATCH = re.compile(r"^.+\.xl[a-z]{1,2}$")
VALID_NUMERIC_MATCH = re.compile(r"^\d+$")
NAN = np.nan

assert EXCEL_FILE_MATCH.match(EXCEL_FILE_NAME)

