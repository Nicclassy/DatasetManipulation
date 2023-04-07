__all__ = [
    "_column_number_to_letter",
    "_flatten",
    "_get_array_dtype",
    "_date_string_to_datetime",
    "_datetime_to_date_string",
    "_replace_nones",
    "_remove_nans",
    "_replace_nans",
    "_format_slice",
    "_get_cell_values",
    "_has_border_type",
    "_bound_worksheet_data_region",
    "_generate_structure_string",
]

import os
import warnings
from datetime import datetime
from typing import Any, List, Tuple
from operator import attrgetter

from openpyxl.cell.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from dataset.constants import DATE_VALUE, NAN
from dataset.config import array_print_columns, max_array_print_rows, dataset_print_columns, indentation_character


def _column_number_to_letter(number: int) -> str:
    return chr(64 + number)


def _column_letter_to_number(letter: str) -> int:
    return ord(letter) - 64


def _flatten(lst: list):
    if not lst:
        return lst
    if isinstance(lst[0], (list, tuple)):
        return _flatten(lst[0]) + _flatten(lst[1:])
    return lst[:1] + _flatten(lst[1:])


def _get_array_dtype(array: Any) -> type:
    dtypes = tuple(set(map(type, _remove_nans(array))))
    return dtypes[0]


def _date_string_to_datetime(number_value: str) -> datetime:
    assert DATE_VALUE.match(number_value), repr(number_value)
    return datetime.strptime(number_value.zfill(8), "%d.%m.%y")


def _datetime_to_date_string(datetime_obj: datetime) -> str:
    return datetime_obj.strftime("%d.%m.%y")


def _replace_nones(value: Any, replacement_value: Any = NAN) -> Any:
    return replacement_value if value is None else value


def _remove_nans(array: Any) -> Any:
    return type(array)([item for item in array if item is not NAN])


def _replace_nans(array: Any, value: Any) -> Any:
    return type(array)([item if item is not NAN else value for item in array])


def _format_slice(min_column_characters: int, ellipsis_space_length: int, iterable_length: int) -> Tuple[int, int, int]:
    # Format the character spacing and quantity horizontally (does not modify them veritcally)
    try:
        columns = os.get_terminal_size().columns
    except OSError:
        warnings.warn("It is recommended to run this program on a terminal-based console "
                      "(that is not simulated, PyCharm has a simulated terminal) so that "
                      "the Dataset outputs correctly when converted to a string.\n")
        print()
        columns = dataset_print_columns.value
    finally:
        columns -= ellipsis_space_length
        max_column_fits = columns // min_column_characters
        column_characters = min_column_characters
        # Maximise space taken up by the output
        while (column_characters + 1) * max_column_fits <= columns:
            column_characters += 1
        max_column_fits = columns // column_characters
        characters_per_side, remainder = divmod(max_column_fits, 2)
        return column_characters, characters_per_side + remainder, iterable_length - characters_per_side - 1


def _get_cell_values(cell_range: List[Cell]) -> List[Any]:
    return list(map(attrgetter("value"), cell_range))


def _has_border_type(cell: Cell, border_type: str) -> bool:
    return getattr(cell.border, border_type).style


def _bound_worksheet_data_region(worksheet: Worksheet) -> Tuple[int, int, int]:
    # 1. Find last data row

    # The "a" column always has data as it is used to distinguish entries
    row = 1
    border_count = 0
    while border_count < 2:
        cell = worksheet["A" + str(row)]
        if _has_border_type(cell, "bottom"):
            if border_count == 0:
                index_row = row
            elif border_count == 1:
                last_data_row = row
            border_count += 1
        row += 1

    # 2. Find last data column
    col = 1
    while 1:
        cell = worksheet[_column_number_to_letter(col) + str(last_data_row)]
        if not _has_border_type(cell, "bottom"):
            last_data_column = col - 1
            break
        col += 1

    return index_row, last_data_row, last_data_column


def _generate_structure_string(structures: List[Any], column_headings: List[str],
                               index_column: bool = False, cut_data: bool = True) -> str:
    # Make copies because these variables are passed in by reference (i.e. inplace operations affect variables in outer scopes)
    data = structures[:]
    headings = column_headings[:]
    if index_column:
        data.insert(0, range(len(data[0])))
        headings.insert(0, "Index")

    # writing it this way so that PyCharm does not state that this variable may be undefined
    indent_char = indentation_character.value

    assert len(data) == len(headings), "This isn't going to work..."
    data_length = len(data)
    column_length = len(data[0])

    try:
        columns = os.get_terminal_size().columns // 5
    except OSError:
        columns = array_print_columns.value

    string_format = f"{{:{indent_char}{columns}}}" * data_length
    output = string_format.format(*headings)

    max_print_rows = max_array_print_rows.value
    cutoff = column_length
    if cut_data and cutoff > max_print_rows + 1:
        indices = list(range(max_print_rows // 2 - 1)) \
                  + list(range(column_length - max_print_rows // 2 - 2, column_length - 1))
    else:
        indices = range(column_length)

    for index in indices:
        if cut_data and cutoff and index == column_length - max_print_rows // 2 - 2:
            output += "\n" + string_format.format(*(["..."] * data_length))
        else:
            values = list(str(structure[index]) for structure in data)
            output += "\n" + string_format.format(*values)
    return output
