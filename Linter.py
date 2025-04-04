import re
from enum import StrEnum
from pathlib import Path

import click
import yaml  # type: ignore[import]
from pydantic import BaseModel, Field


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


class SpacingConfig(BaseModel):
    """BaseModel для флагов проверки пробелов"""

    max_row: int = Field(2, gt=0, description="Максимальное количество пробелов подряд")
    around_operators: bool = Field(
        True, description="Проверять пробелы вокруг операторов"
    )
    after_commas: bool = Field(True, description="Проверять пробелы после запятых")
    around_keywords: bool = Field(
        True, description="Проверять пробелы после ключевых слов"
    )


class NamingConfig(BaseModel):
    """BaseModel для флагов проверки имён переменных"""

    variables: State = Field(
        State.CAMEL_CASE, description="Стиль именования переменных"
    )
    constants: State = Field(State.UPPER_CASE, description="Стиль именования констант")
    methods: State = Field(State.CAMEL_CASE, description="Стиль именования методов")
    classes: State = Field(State.PASCAL_CASE, description="Стиль именования классов")


class Config(BaseModel):
    """BaseModel для флагов проверки из файла конфигурации"""

    spacing: SpacingConfig

    naming: NamingConfig

    max_consecutive_empty_lines: int = Field(
        2, gt=0, description="Максимальное количество пустых строк подряд"
    )

    @classmethod
    def from_yaml(cls, config_path: str) -> "Config":
        """Загрузка конфигурации из .yaml файла"""

        try:
            path = Path(config_path)
            if not path.exists():
                raise FileNotFoundError(
                    "Файл конфигурации не найден(\nПроверьте его наличие"
                )

            with path.open("r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
                return cls(**config_data)

        except yaml.YAMLError as e:
            raise ValueError(f"Ошибка в параметрах конфигурационного файла: {str(e)}")
        except Exception as e:
            raise ValueError(f"Ошибка загрузки файла конфигурации: {str(e)}")


class Errors:
    """Класс для хранения ошибок"""

    def __init__(self):
        self.__spacing_errors: list[str] = []
        self.__empthy_lines_errors: list[str] = []
        self.__naming_errors: list[str] = []

    def append_spacing_er(self, error: str) -> None:
        self.__spacing_errors.append(error)

    def append_empthy_lines_er(self, error: str) -> None:
        self.__empthy_lines_errors.append(error)

    def append_naming_er(self, error: str) -> None:
        self.__naming_errors.append(error)

    def get_all_errors(self) -> list[list[str]]:
        return [self.__spacing_errors, self.__empthy_lines_errors, self.__naming_errors]

    def get_lines_errors(self) -> list[str]:
        return self.__empthy_lines_errors

    def get_naming_errors(self) -> list[str]:
        return self.__naming_errors

    def get_spacing_errors(self) -> list[str]:
        return self.__spacing_errors


class Linter:
    """Основной класс линтера, для проверки стиля java кода"""

    def __init__(self, java_doc: str, config: Config):
        self.__formated_java_doc: list[str] = []
        self.__format_java_doc(java_doc)
        self.__config: Config = config
        self.__errors: Errors = Errors()

    def __format_java_doc(self, java_doc: str) -> None:
        """Разбивает java файл на строки, убирая отсупы вначале"""

        try:
            self.formated_java_doc = [
                line.lstrip() for line in open(java_doc).read().splitlines()
            ]
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Ошибка при открытие файла: {java_doc}\n"
                f"Проверьте правильность ввода названия файла"
            )

    def linting(self) -> Errors:
        """
        Основная функция линтинга, запускающая все проверки
        Возвращает список списков строк(ошибок)
        """
        self.__check_spacing()
        self.__check_empthy_lines()
        self.__check_naming()
        return self.__errors

    def __check_spacing(self) -> None:
        """
        Проверка на пробелы, проверяем флаги из файла конфигурации и,
        если они подняты, то делаем соответсвующую проверку по регуляркам
        """
        space_reg = rf"\s{{{str(self.__config.spacing.max_row)},}}"
        self.__find_errors(space_reg, CheckName.MAX_ROW)

        if self.__config.spacing.around_operators:
            a_op_reg_1: str = r"[\w\d]+[!=\+\-\*\/%]=|[!=\+\-\*\/%]=[\w\d]+"
            a_op_reg_2: str = r"[\w\d]+[\/=\*<>&|\+\-]| [\/=\*<>&|\+\-][\w\d]+"

            self.__find_errors(
                a_op_reg_1,
                CheckName.AROUND_OPERATORS,
            )
            self.__find_errors(
                a_op_reg_2,
                CheckName.AROUND_OPERATORS,
            )

        if self.__config.spacing.after_commas:
            a_commas_reg = r",\w+"
            self.__find_errors(a_commas_reg, CheckName.AFTER_COMMAS)

        if self.__config.spacing.around_keywords:
            a_key_reg = r"if\(|while\(|for\("
            self.__find_errors(a_key_reg, CheckName.AROUND_KEY)

    def __check_empthy_lines(self) -> None:
        """Проверка на пустые строки, идём по файлу и считаем пустые строки"""
        count: int = 0

        for i, new_line in enumerate(self.formated_java_doc):
            if new_line == "":
                count += 1
                if count >= self.__config.max_consecutive_empty_lines:
                    self.__errors.append_empthy_lines_er(
                        f"Слишком много пустых строк подряд в строке {i + 1}"
                    )
            else:
                count = 0

    def __check_naming(self) -> None:
        """
        Проверка нейминга, проверяем соответсвующие типы названий переменных из файла конфигурации
        и если они базовые, то делаем соответсвующую проверку по регуляркам, иначе пропуск
        """
        if self.__config.naming.variables == State.CAMEL_CASE.value:
            variables_reg = r"[A-Z]?[a-z]+_[A-Za-z]+|\d+[a-zA-Z]+|_[a-z]+|\b[A-Z]\b|^\w+\s[A-Z]+.+ =.+$"
            self.__find_errors(variables_reg, CheckName.VARIABLES)

        if self.__config.naming.constants == State.UPPER_CASE.value:
            constants_reg = r"final\s\w+\s[^A-Z]+|final\s\w+\s[^a-z]+[a-z]+_"
            self.__find_errors(constants_reg, CheckName.CONSTANTS)

        if self.__config.naming.methods == State.CAMEL_CASE.value:
            methods_reg = (
                r"[a-z]+_[a-z]+\(|\d+[a-zA-Z]+\(|_[a-z]+\(|[A-Z][a-z]+[A-Z][a-z]+\("
            )
            self.__find_errors(methods_reg, CheckName.METHODS)

        if self.__config.naming.classes == State.PASCAL_CASE.value:
            c_reg = r"class\s[a-z]"
            self.__find_errors(c_reg, CheckName.CLASSES)

    def __find_errors(self, reg: str, what_check: CheckName) -> None:
        """
        Функция которая находит ошибки с помощью переданного в неё регулярногов выражения и
        типа проверки, после чего добавляет найденную ошибку в основной массив
        """
        for i, new_line in enumerate(self.formated_java_doc):
            if re.search(reg, new_line):
                match what_check:
                    case CheckName.AROUND_OPERATORS:
                        self.__errors.append_spacing_er(
                            f"Нет пробелов вокруг оператора в строке {i + 1}: '{new_line}'"
                        )

                    case CheckName.AFTER_COMMAS:
                        self.__errors.append_spacing_er(
                            f"Не установлены пробелы после запятой {i + 1}: '{new_line}'"
                        )

                    case CheckName.AROUND_KEY:
                        self.__errors.append_spacing_er(
                            f"Не установлены пробелы после ключеввых слов {i + 1}: '{new_line}'"
                        )

                    case CheckName.CONSTANTS:
                        self.__errors.append_naming_er(
                            f"Неправильное название константы в строке {i + 1}: '{new_line}'"
                        )

                    case CheckName.CLASSES:
                        self.__errors.append_naming_er(
                            f"Неправильное название класса в строке {i + 1}: '{new_line}'"
                        )

                    case CheckName.VARIABLES:
                        self.__errors.append_naming_er(
                            f"Неправильное название переменной в строке {i + 1}: '{new_line}'"
                        )

                    case CheckName.METHODS:
                        self.__errors.append_naming_er(
                            f"Неправильное название метода в строке {i + 1}: '{new_line}'"
                        )

                    case CheckName.MAX_ROW:
                        self.__errors.append_spacing_er(
                            f"Лишние пробелы в строке {i + 1}: '{new_line}'"
                        )


@click.group()
def start_linting():
    """Java Code Linter.py - проверяет стиль кода java файла"""
    pass


@start_linting.command()
@click.argument(
    "java_file",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=True,
)
@click.option(
    "--config",
    "-c",
    default="config.yaml",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Задать название файла конфигурации (по умолчанию config.yaml)",
)
@click.option(
    "--verbose",
    "-v",
    default=True,
    is_flag=True,
    help="Отключить подробный вывод с указанием строк",
)
def lint(java_file: str, config: str, verbose: bool) -> None:
    """
    Проверяет Java-файл на соответствие стилю

    JAVA_FILE - путь к проверяемому .java файлу
    """
    try:
        linter = Linter(java_file, Config.from_yaml(config))
        errors = linter.linting()

        report = generate_report(java_file, errors, verbose)

        click.echo(report)

    except Exception as e:
        click.secho(f"Ошибка: {str(e)}", fg="red", err=True)
        raise click.Abort()


def generate_report(java_file: str, errors: Errors, verbose: bool) -> str:
    """Генерирует отчет об ошибках"""
    report = []
    error_types = [
        ("Пробелы и отступы", "yellow"),
        ("Пустые строки", "blue"),
        ("Нейминг", "magenta"),
    ]

    total_errors = sum(len(err_group) for err_group in errors.get_all_errors())
    header = f"Линтинг файла: {java_file}\nНайдено ошибок: {total_errors}"
    report.append(click.style(header, fg="green", bold=True))

    for (title, color), err_group in zip(error_types, errors.get_all_errors()):
        if err_group:
            report.append(click.style(f"\n=== {title} ===", fg=color, bold=True))
            for error in err_group:
                if verbose:
                    report.append(f" • {error}")

    return "\n".join(report)


@start_linting.command()
@click.option(
    "--file_name",
    "-f",
    default="config.yaml",
    type=click.Path(dir_okay=False),
    help="Имя файла конфигурации (по умолчанию config.yaml)",
)
def init_config(file_name: str) -> None:
    """Генерирует стандартный конфигурационный файл"""
    default_config = """\
spacing:
  max_row: 2
  around_operators: true
  after_commas: true
  around_keywords: true

empty_lines:
  max_consecutive_empty_lines: 2

naming:
  variables: camelCase
  constants: UPPER_CASE
  methods: camelCase
  classes: PascalCase
"""
    try:
        with open(file_name, "w") as f:
            f.write(default_config)
        click.echo(f"Создан файл конфигурации: {file_name}")
    except IOError as e:
        click.secho(f"Ошибка при создании файла: {str(e)}", fg="red", err=True)
        raise click.Abort()


if __name__ == "__main__":
    start_linting()
