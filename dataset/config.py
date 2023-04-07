__all__ = [
    "Configurable",
    "max_array_print_rows",
    "array_print_columns",
    "dataset_print_columns",
    "indentation_character",
    "dataset_configurables",
]

from typing import Any, Optional


class Configurable:

    def __init__(self, name: str, value: Any, validation: Optional[dict | list] = None):
        self.__name = name
        self.__value = value
        self.__validation = validation

    def __repr__(self):
        return f"Configurable(name={self.__name!r}, value={self.__value!r})"

    @property
    def name(self) -> str:
        return self.__name

    @property
    def value(self) -> Any:
        return self.__value

    def register_value(self, value: Any):
        iter_val = None
        if self.__validation is not None:
            iter_val = value if value in self.__validation else None
            if type(self.__validation) is dict:
                iter_val = self.__validation.get(value) or (value if value in self.__validation.values() else None)

            if iter_val is None:
                raise ValueError

        self.__value = iter_val or value


max_array_print_rows = Configurable("max_array_print_rows", 30)
array_print_columns = Configurable("array_print_columns", 80)
dataset_print_columns = Configurable("dataset_print_columns", 120)
indentation_character = Configurable("indentation_character", "<", validation={"left": "<", "right": ">"})

dataset_configurables = [
    max_array_print_rows,
    array_print_columns,
    dataset_print_columns,
    indentation_character,
]
