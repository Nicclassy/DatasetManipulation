__all__ = [
    "get_valid_plot_type",
    "plot_data",
    "plot_compared_data",
]

from typing import Callable, Any, Optional

import pandas as pd
from matplotlib import pyplot as plt

from dataset.constants import VALID_NUMERIC_MATCH
from ui.selector import SelectionDisplay

plt.style.use("fivethirtyeight")

PLOT_TYPES = {
    "plot": plt.plot,
    "bar": plt.bar,
    "barh": plt.barh,
    "pie": plt.pie,
    "scatter": plt.scatter,
}

PLOT_TYPE_ALIASES = {
    "Plot": "plot",
    "Bar chart": "bar",
    "Horizontal bar chart": "barh",
    "Pie chart": "pie",
    "Scatter plot": "scatter",
}


def _valid_plot_type(plot_type: str, max_number: int):
    if plot_type.isdigit() and VALID_NUMERIC_MATCH.match(plot_type):
        return 0 < int(plot_type) <= max_number
    else:
        return plot_type in PLOT_TYPES or plot_type in PLOT_TYPE_ALIASES


def get_valid_plot_type() -> Optional[Callable]:
    print("The available plot types are: ", SelectionDisplay(PLOT_TYPE_ALIASES))
    plot_type_name = input("Enter the plot type you would like: ")
    while not _valid_plot_type(plot_type_name, len(PLOT_TYPES)) or not plot_type_name:
        print("Please re-enter a valid plot type.")
        plot_type_name = input("Enter the plot type you would like: ")
    if plot_type_name.isdigit():
        plot_type_name = list(PLOT_TYPES)[int(plot_type_name) - 1]
    elif not plot_type_name:
        return None
    return PLOT_TYPES.get(plot_type_name) or PLOT_TYPES.get(PLOT_TYPE_ALIASES.get(plot_type_name))


def plot_data(plot_function: Callable, x_values: Any, y_values: Any,
              x_label: str, y_label: str, **kwargs: Any):
    x_values, y_values = pd.Series(list(x_values)), pd.Series(list(y_values))
    plot_function(x_values, y_values, **kwargs)
    plt.title(f"{x_label} vs {y_label}")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.tight_layout()
    plt.show()


def plot_compared_data(plot_function: Callable, datetimes: Any, x_values: Any, cmp_x_values: Any,
                       label1: str, label2: str, **kwargs: Any):
    x_values, cmp_x_values, datetimes = pd.Series(list(x_values)), \
                                        pd.Series(list(cmp_x_values)), \
                                        pd.Series(list(datetimes))
    plot_function(datetimes, x_values, label=label1, **kwargs)
    plot_function(datetimes, cmp_x_values, label=label2, **kwargs)
    plt.gcf().set_size_inches((10, 6))
    plt.title(f"{label1} vs {label2} with respect to time")
    plt.legend()
    plt.tight_layout()
    plt.show()
