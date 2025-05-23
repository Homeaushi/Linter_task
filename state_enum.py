from enum import StrEnum


class State(StrEnum):
    """Енум для перечисления стилей именнования"""

    CAMEL_CASE = "camelCase"
    UPPER_CASE = "UPPER_CASE"
    PASCAL_CASE = "PascalCase"
    DISABLED = "disabled"


class CheckName(StrEnum):
    """Енум для перечисления типов проверки ф-ции find_error"""

    MAX_ROW = "max_row"
    AROUND_OPERATORS = "around_operators"
    AFTER_COMMAS = "after_commas"
    AROUND_KEY = "around_keywords"
    VARIABLES = "variables"
    CONSTANTS = "constants"
    METHODS = "methods"
    CLASSES = "classes"
