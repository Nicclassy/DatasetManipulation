__all__ = [
    "VALID_FILENAME",
    "VALID_EXCEL_SHEET_NAME",
    "VALID_DECISION",
    "WORKBOOK_DIRECTORY",
]

import re
import os

from dataset.constants import FOLDER_DIRECTORY

# Numbers, letters, hyphens, underscores and spaces permitted
VALID_FILENAME = re.compile(r"^[\w\- ]+(?<!\.)$")
# Properties of a valid Excel sheet name:
# • No longer than 31 characters
# • None of these characters: : \  /  ?  *  [  or  ]
# • The name is not blank (hence the 1 in the quantifier)
VALID_EXCEL_SHEET_NAME = re.compile(r"[^]\[\\/?*]{1,31}")
VALID_DECISION = re.compile(r"^[yn].*", flags=re.IGNORECASE)

WORKBOOK_DIRECTORY = os.path.join(FOLDER_DIRECTORY, "workbooks")


