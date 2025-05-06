class Errors:
    """Класс для хранения ошибок"""

    def __init__(self):
        self.__spacing_errors: list[str] = []
        self.__empthy_lines_errors: list[str] = []
        self.__naming_errors: list[str] = []
        self.__unusage_var_errors: list[str] = []
        self.__unusage_methods_errors: list[str] = []
        self.__complexity_errors: list[str] = []

    def append_spacing_er(self, error: str) -> None:
        self.__spacing_errors.append(error)

    def append_empthy_lines_er(self, error: str) -> None:
        self.__empthy_lines_errors.append(error)

    def append_naming_er(self, error: str) -> None:
        self.__naming_errors.append(error)

    def append_var_usage_er(self, error: str) -> None:
        self.__unusage_var_errors.append(error)

    def append_methods_usage_er(self, error: str) -> None:
        self.__unusage_methods_errors.append(error)

    def append_complexity_er(self, error: str) -> None:
        self.__complexity_errors.append(error)

    def get_lines_errors(self) -> list[str]:
        return self.__empthy_lines_errors

    def get_naming_errors(self) -> list[str]:
        return self.__naming_errors

    def get_spacing_errors(self) -> list[str]:
        return self.__spacing_errors

    def get_append_complexity_errors(self) -> list[str]:
        return self.__complexity_errors

    def get_all_errors(self) -> list[list[str]]:
        return [
            self.__spacing_errors,
            self.__empthy_lines_errors,
            self.__naming_errors,
            self.__unusage_var_errors,
            self.__unusage_methods_errors,
            self.__complexity_errors,
        ]
