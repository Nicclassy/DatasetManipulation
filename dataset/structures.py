__all__ = [
    "_DatasetArrayRow",
    "_DatasetArrayColumnView",
    "_DatasetArray",
    "_Schema",
]

import numpy as np
from abc import ABCMeta, abstractmethod
from typing import Callable, Any, List, Tuple

from dataset.constants import NAN
from dataset.functions import _generate_structure_string
from dataset.statmeasures import STATISTICAL_FUNCTIONS, Numeric


class _DatasetStructureABC(metaclass=ABCMeta):

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __getitem__(self, index: int):
        pass

    @abstractmethod
    def __str__(self):
        pass


class _DatasetArrayRow(_DatasetStructureABC):

    # Categorising by row allows entries to be sorted easier and better comparisons
    # However, statistical data is more difficult to obtain

    def __init__(self, data: list, dataset_column_names: List[str]):
        self.__data = data
        self.__dataset_column_names = dataset_column_names

    def __getitem__(self, index: int) -> Any:
        return self.__data[index]

    def __len__(self) -> int:
        return len(self.__data)

    def __setitem__(self, index: int, value: Any):
        self.__data[index] = value

    def __str__(self) -> str:
        return _generate_structure_string([self.__dataset_column_names, list(self)], ["Column", "Value"])

    def apply_function(self, function: Callable):
        self.__data = type(self.__data)(list(map(function, self.__data)))

    def apply_function_at_index(self, function: Callable, index: int):
        if self.__data[index] is not NAN:
            self.__data[index] = function(self.__data[index])


class _DatasetArrayColumnView(_DatasetStructureABC):

    # Copy of data. Not synonymous with real data; used for presentation purposes
    # All edits are made to the row data

    # Unlike its row counterpart, this class has no __setitem__, hence the inclusion of "view"

    def __init__(self, name: str, data: list, dtype: type):
        self.__data = data
        self.__dtype = dtype
        self.__name = name

    def __getitem__(self, index: int) -> Any:
        return self.__data[index]

    def __len__(self) -> int:
        return len(self.__data)

    def __str__(self):
        return _generate_structure_string([list(self)], [self.__name], index_column=True)

    @property
    def dtype(self):
        return self.__dtype

    @property
    def name(self):
        return self.__name

    def statistic(self, statistic: str, *args: Any, **kwargs) -> Numeric | list | bool:
        return STATISTICAL_FUNCTIONS[statistic](self.__data, *args, **kwargs)

    def get_statistical_summary(self, statistics_list: list) -> Tuple[list, list]:
        statistical_values = [self.statistic(statistic.lower()) for statistic in statistics_list]
        statistics_list[statistics_list.index("Mode")] = "Mode(s)"
        return statistics_list, statistical_values

    def get_statistical_summary_string(self, statistics_list: list) -> str:
        return _generate_structure_string(list(self.get_statistical_summary(statistics_list)), ["Statistic", "Value"],
                                          cut_data=False)


class _DatasetArray:

    def __init__(self, array: list):
        self.__data = array

    def __len__(self) -> int:
        return len(self.__data)

    def __getitem__(self, index: int) -> Any:
        return self.__data[index]

    def __setitem__(self, index: int, value: Any):
        self.__data[index] = value

    def __iter__(self):
        return iter(self.__data)


class _Schema:

    def __init__(self, data: dict):
        self.__data = data

    def __getitem__(self, item: str):
        return self.__data[item]

    def __str__(self) -> str:
        return _generate_structure_string([list(self.__data), list(self.__data.values())], ["Column", "Description"])


if __name__ == "__main__":
    # # col1 = _DatasetArrayColumnView(list(range(31))) # Sufficient values
    # col2 = _DatasetArrayColumnView(list(range(45))) # Too many; must be cut
    # # print(col1)
    # # print()
    # print(col2)
    # print()
    # import re
    # cd = re.split(r"\s+", """05.08.09	1.102		0.986		7	0.682	0.013	0.32	0.1	1.2	0.24	0.20	7.9	15	223	194""")
    # colnames = ['Date', 'Biovolume, mm3/L', 'Biomass, g d.w./m2', 'Chl a, µg/L', 'Length, mm',
    #             'NH4,mg/L as N', 'Nox,mg/L as N', 'FRP,mg/L as P', 'Total N,mg/L as N', 'Total P,mg/L',
    #             'Secchi,m', 'pH at 0.5m', 'Mean column toC', 'Conductivity,µS cm-1', 'Turbidity,NTU']
    # print(_DatasetArrayRow(cd, colnames))

    # d = _Schema({"a": "b", "c": "d", "g": "h"})
    # print(d)

    dr = _DatasetArrayColumnView("Integers", [1, 2, 3, 68, np.nan], int)
    # print(dr)
    print(dr.statistic("mean", na_action="average", outlier_action="average", round_dp=False))
