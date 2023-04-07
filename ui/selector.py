__all__ = [
    "Selector",
    "SelectionDisplay",
    "BROKEN_LOOP",
]

from typing import Any, Optional
from collections import OrderedDict

from dataset.constants import VALID_NUMERIC_MATCH

# Sentinel used to indicate a loop is broken; referenced when the user types blank input (i.e. "")
BROKEN_LOOP = object()
# Sentinel used to indicate predetermined input has been exhausted
DATA_END = object()


class SelectionDisplay:

    def __init__(self, options):
        # Attribute is protected; private attributes cannot be inherited
        self._options = options if type(options) is list else OrderedDict(options)

    def __str__(self):
        output = "\n"
        for option_number, option in enumerate(self._options, 1):
            output += f"{option_number}. {option}\n"
        return output


class Selector(SelectionDisplay):
    INPUT_CHARACTERS = ">>> "
    PREDETERMINED_INPUT = False
    iterator = None

    def __init__(self, options: list | dict, *, breakable: bool = True, notify_option: bool = True):
        super().__init__(options)
        self.__option_list = list(self._options)
        self.__function_options = type(self._options) is OrderedDict
        self.__option_count = len(options)
        self.__breakable = breakable
        self.__notify_option = notify_option
        self.__running = True

    @property
    def running(self):
        return self.__running

    def _process_user_input(self, user_input: Any) -> bool | int | object:
        if user_input is DATA_END:
            return DATA_END
        elif self.__breakable and not user_input:
            return BROKEN_LOOP
        elif VALID_NUMERIC_MATCH.match(user_input):
            integer_value = int(user_input)
            if 0 < integer_value <= self.__option_count:
                return integer_value
            else:
                return False
        else:
            return False

    def _get_user_input(self) -> bool | int:
        cls = type(self)
        if len(self._options) == 1 and not cls.PREDETERMINED_INPUT:
            print(f"\nAutomatically selected {self._options[0]!r} because it is the only option available.\n")
            return 1
        elif not cls.PREDETERMINED_INPUT:
            print(f"\nChoose an option number between 1 and {self.__option_count}:")
            print(self)
            return self._process_user_input(input(cls.INPUT_CHARACTERS))
        else:
            return self._process_user_input(cls.next())

    def _validate_user_input(self) -> int:
        user_input = self._get_user_input()
        while not user_input or user_input is DATA_END:
            if user_input is not DATA_END:
                print("\nPlease re-enter an appropriate option number.\n")
            user_input = self._get_user_input()
        if not type(self).PREDETERMINED_INPUT and self.__notify_option and user_input is not BROKEN_LOOP:
            # "and user_input is not BROKEN_LOOP" is necessary so that this doesn't print if no input is entered
            print(f"\nSelected option {self.__option_list[user_input - 1]!r}.")
        return user_input

    @classmethod
    def next(cls):
        next_value = next(cls.iterator, DATA_END)
        if next_value is DATA_END:
            cls.PREDETERMINED_INPUT = False
            return DATA_END
        else:
            return next_value

    def run(self) -> Optional[int | object]:
        validated_input = self._validate_user_input()
        if validated_input is BROKEN_LOOP:
            self.__running = False
            return BROKEN_LOOP
        elif self.__function_options:
            option_index = validated_input - 1
            option_chosen = self.__option_list[option_index]
            function = self._options[option_chosen]
            function()
        else:
            return validated_input

    @classmethod
    def parse_predetermined_input(cls, values: list):
        cls.PREDETERMINED_INPUT = True
        cls.iterator = iter(values)


if __name__ == "__main__":
    # Example code

    # 1: List structure; sutied for case-match
    selector1 = Selector(["A", "B", "C"])
    val = selector1.run()
    if val:
        print(val)


    # 2: Function mapping structure; useful for major routines
    def f():
        print("A function f")


    def g():
        return 3


    selector2 = Selector({"O1": f, "O2": g, "O3": print, "O4": lambda: 5})
    selector2.run()
