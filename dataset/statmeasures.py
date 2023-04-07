__all__ = [
    "STATISTICAL_FUNCTIONS",
    "Numeric",
    "get_base_statistical_function",
]

import math
import operator
import numpy as np
from typing import NewType, Callable, List, Dict, Optional
from collections import Counter
from itertools import groupby

from dataset.constants import NAN
from dataset.functions import _remove_nans, _replace_nans, _get_array_dtype

Numeric = int | float
Data = NewType("Data", List[Numeric])


def _remove_outliers(data: Data | list) -> list:
    return [value for value in data if not get_base_statistical_function("outlier")(data, value)]


def _replace_outliers(data: Data, repl: Numeric) -> list:
    outlier = get_base_statistical_function("outlier")
    return [value if not outlier(_remove_nans(data), value) else repl for value in data]


def _no_outlier_mean(data: Data) -> Numeric:
    no_outlier_data = _remove_outliers(_remove_nans(data))
    no_outlier_mean = sum(no_outlier_data) / len(no_outlier_data)
    return no_outlier_mean


def _no_outlier_median(data: Data) -> Numeric:
    data = _remove_outliers(sorted(data))
    num_of_elements = len(data)
    if num_of_elements % 2 == 1:
        return data[num_of_elements // 2]
    else:
        return (data[num_of_elements // 2 - 1] + data[num_of_elements // 2]) / 2


def reformat_data(data: Data, *, na_action: str = "ignore", outlier_action: str = "keep"):
    modified_data = data[:]
    match outlier_action:
        case "remove" | "ignore":
            modified_data = _remove_outliers(modified_data)
        case "average" | "mean":
            no_outlier_mean = _no_outlier_mean(modified_data)
            modified_data = _replace_outliers(modified_data, no_outlier_mean)
        case "median":
            # modified_data = _replace_outliers(modified_data, _no_outlier_median(modified_data))
            median = _no_outlier_median(_remove_nans(modified_data))
            if na_action in ["remove", "ignore", "median"]:
                median = _no_outlier_median(_remove_nans(modified_data))
            elif na_action in ["average", "mean"]:
                median = _no_outlier_median(_replace_nans(modified_data, _no_outlier_mean(modified_data)))
            modified_data = _replace_outliers(modified_data, median)
    match na_action:
        case "remove" | "ignore":
            modified_data = _remove_nans(modified_data)
        case "average" | "mean":
            numeric_data = _remove_nans(modified_data)
            if outlier_action == "keep":
                mean = sum(numeric_data) / len(numeric_data)
            else:
                mean = _no_outlier_mean(numeric_data)
            modified_data = _replace_nans(modified_data, mean)
        case "median":
            modified_data = _replace_nans(modified_data, _no_outlier_median(modified_data))

    # if round_dp:
    #     return [round(value, round_dp) for value in modified_data]
    # else:
    #     return modified_data

    return modified_data


class _StatisticalMeasure:

    # Handles arguments of stat functions

    __instances = {}

    def __new__(cls, function_name: str, function: Callable):
        self = object.__new__(cls)
        self.__function_name = function_name
        self.__function = function
        # Extra arguments only; assumes data array is passed in
        self.__extra_args = self.__function.__code__.co_argcount - 1
        # Check if the variable name of the function != the actual name of the function in memory
        self.__is_alias = self.__function_name != self.__function.__name__
        cls.__instances[self.__function_name] = self.__function
        return self

    def __repr__(self):
        return f"_StatisticalMeasure(function={self.__function_name!r})"

    def __str__(self):
        return self.__function_name

    def __call__(self, data: Data, fargs: list | frozenset = frozenset(), *, na_action: str = "ignore",
                 outlier_action: str = "keep", round_dp: Optional[int] = None) -> list | None:
        # make the type checkers and PyCharm happy
        modified_data = data[:]
        if _get_array_dtype(modified_data) not in (int, float):
            # I don't particularly like this method, but
            # the case-match syntax does not accept the Numeric type hint
            return NAN

        modified_data = reformat_data(data, na_action=na_action, outlier_action=outlier_action)
        # The array data is an assumed argument
        assert (expected_additional_function_args := self.__extra_args) == len(fargs), \
            f"Expected {expected_additional_function_args} argument(s), got {len(fargs)}"

        stat = self.__function(modified_data, *fargs)
        return stat if round_dp is None else round(stat, round_dp)

    @property
    def extra_args(self) -> int:
        return self.__extra_args

    @property
    def function(self) -> Callable:
        return self.__function

    @property
    def is_alias(self) -> bool:
        return self.__is_alias


def _get_statistical_functions() -> Dict[str, _StatisticalMeasure]:
    # Enclose within function to store functions locally, defined only in this scope

    def range(data: Data) -> Numeric:
        return max(data) - min(data)

    def mean(data: Data) -> Numeric:
        return sum(data) / len(data)

    def mode(data: Data) -> Numeric | list:
        # Handles multimodal data
        value_counts = Counter(data).most_common()
        max_count, mode_values = next(groupby(value_counts, key=operator.itemgetter(1)), (0, []))
        return list(map(operator.itemgetter(0), mode_values))

    def median(data: Data) -> Numeric:
        # Use the non-inplace operation so that the data is not modified
        # i.e. the list.sort method modifies the parameter because it is passed in by reference
        data_copy = sorted(data)
        mid, remainder = divmod(len(data), 2)
        if remainder == 0:
            return (data_copy[mid - 1] + data_copy[mid]) / 2
        else:
            return data_copy[mid]

    def q1(data: Data) -> Numeric:
        return np.percentile(data, 25)

    def q3(data: Data) -> Numeric:
        return np.percentile(data, 75)

    def iqr(data: Data) -> Numeric:
        return q3(data) - q1(data)

    def upper_outlier(data: Data, value: Numeric) -> bool:
        return value > q3(data) + 1.5 * iqr(data)

    def lower_outlier(data: Data, value: Numeric) -> bool:
        return value < q1(data) - 1.5 * iqr(data)

    def outlier(data: Data, value: Numeric) -> bool:
        return lower_outlier(data, value) or upper_outlier(data, value)

    def stdev(data: Data) -> Numeric:
        return math.sqrt(sum(pow(x - mean(data), 2) for x in data) / (len(data) - 1))

    def variance(data: Data) -> Numeric:
        return pow(stdev(data), 2)

    def z_score(data: Data, value: Numeric) -> Numeric:
        return (value - mean(data)) / stdev(data)

    def cv(data: Data) -> Numeric:
        """Coefficient of variation"""
        return stdev(data) / mean(data)

    def se(data: Data) -> Numeric:
        """Standard error"""
        return stdev(data) / math.sqrt(len(data))

    # Aliasses
    q2 = median
    # var = variance
    # std = sd = stdev
    # z = z_score

    return {function_name: _StatisticalMeasure(function_name, function) for function_name, function in locals().items()}


# Functions cannot be updated post-runtime
STATISTICAL_FUNCTIONS = _get_statistical_functions()


def get_base_statistical_function(function_name: str) -> Callable:
    return STATISTICAL_FUNCTIONS[function_name].function
