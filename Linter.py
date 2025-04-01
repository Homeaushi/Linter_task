import re


class Config:
    def __init__(self, name_config_file: str):
        self.name_config_file = name_config_file
        self.settings = list[str]()
        self.__set_configguration()

    def get_state(self, index: int) -> str:
        return self.settings[index]

    def __set_configguration(self) -> None:
        config_file = open(self.name_config_file)
        for new_line in config_file:
            new_line = new_line.replace("\n", "")
            if len(new_line.split(":")) == 2:
                self.settings.append(new_line.replace(" ", "").split(":")[1])
        for i in range(3):
            self.settings.remove("")


class Linter:
    def __init__(self, java_doc: str, config: Config):
        self.java_doc = java_doc
        self.formated_java_doc = list[str]()
        self.__format_java_doc()
        self.config = config

    def linting(self) -> list:
        errors = []
        errors.append(self.__check_spacing())
        errors.append(self.__check_empthy_lines())
        errors.append(self.__check_naming())
        return errors

    def __check_spacing(self) -> list:
        errors = []
        space_reg = rf"\s{{{self.config.get_state(0)},}}"
        errors.append(self.__find_errors(space_reg))
        if self.config.get_state(1) == "true":
            errors.append(
                self.__find_errors(
                    r"""[\w\d]+[!=\+\-\*\/%]=|[!=\+\-\*\/%]=[\w\d]+|
                    [\w\d]+[\/=\*<>&|\+\-]|[\/=\*<>&|\+\-][\w\d]+""",
                    what_check="around_operators",
                )
            )
        if self.config.get_state(2) == "true":
            errors.append(self.__find_errors(r",\w+", what_check="after_c"))
        if self.config.get_state(3) == "true":
            errors.append(
                self.__find_errors(
                    r"""if\(|while\(|for\(""", what_check="around_keywords"
                )
            )

        return errors

    def __check_empthy_lines(self) -> list:
        errors = []
        count = 0

        for i, new_line in enumerate(self.formated_java_doc):
            if new_line == "":
                count += 1
                if count >= int(self.config.get_state(4)):
                    errors.append(
                        f"Слишком мнгого пустых строк подряд в строке {i + 1}"
                    )
            else:
                count = 0

        return errors

    def __check_naming(self) -> list:
        errors = []
        #
        if self.config.get_state(5) == "camelCase":
            errors.append(
                self.__find_errors(
                    r"[A-Z]?[a-z]+_[A-Za-z]+|\d+[a-zA-Z]+|_[a-z]+|\b[A-Z]\b",
                    what_check="variables_naming",
                )
            )
        if self.config.get_state(6) == "UPPER_CASE":
            # final\s+\w+\s+[a-zA-Z][a-zA-Z]+
            errors.append(
                self.__find_errors(
                    r"final\s\w+\s[^A-Z]+|final\s\w+\s[^a-z][a-z]",
                    what_check="const_naming",
                )
            )
        if self.config.get_state(7) == "camelCase":
            errors.append(
                self.__find_errors(
                    r"""[a-z]+_[a-z]+\(|\d+[a-zA-Z]+\(|
                    _[a-z]+\(|[A-Z][a-z]+[A-Z][a-z]+\(""",
                    what_check="methods_naming",
                )
            )
        if self.config.get_state(8) == "PascalCase":
            c_reg = r"class\s[a-z]"
            errors.append(self.__find_errors(c_reg, what_check="classes_n"))

        return errors

    def __find_errors(self, reg: str, what_check: str = "") -> list[str]:
        errors = []

        for i, new_line in enumerate(self.formated_java_doc):
            if re.search(reg, new_line):
                match what_check:
                    case "around_operators":
                        errors.append(
                            f"""Нет пробелов вокруг оператора в строке
                             {i + 1}: '{new_line}'"""
                        )
                    case "after_c":
                        errors.append(
                            f"""Не установлены пробелы после запятой
                             {i + 1}: '{new_line}'"""
                        )
                    case "around_braces":
                        errors.append(
                            f"""Лишний пробел после вызова метода
                            {i + 1}: '{new_line}'"""
                        )
                    case "around_keywords":
                        errors.append(
                            f"""Не установлены пробелы после ключеввых слов
                            {i + 1}: '{new_line}'"""
                        )
                    case "const_naming":
                        errors.append(
                            f"""Неправильное название константы в строке
                            {i + 1}: '{new_line}'"""
                        )
                    case "classes_n":
                        errors.append(
                            f"""Неправильное название класса в строке
                            {i + 1}: '{new_line}'"""
                        )
                    case "variables_naming":
                        errors.append(
                            f"""Неправильное название переменной в строке
                            {i + 1}: '{new_line}'"""
                        )
                    case "methods_naming":
                        errors.append(
                            f"""Неправильное название метода в строке
                            {i + 1}: '{new_line}'"""
                        )
                    case _:
                        errors.append(
                            f"""Лишние пробелы в строке
                                      {i + 1}: '{new_line}'"""
                        )
        return errors

    def __format_java_doc(self) -> None:
        self.formated_java_doc = self.java_doc.splitlines()
        for i, new_line in enumerate(self.formated_java_doc):
            self.formated_java_doc[i] = new_line.lstrip()


java_doc = open(input()).read()
linter = Linter(java_doc, Config("config.yaml"))
print(linter.linting())
