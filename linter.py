import re

import click

from config import Config
from errors import Errors
from state_enum import CheckName, State


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
        self.__check_var_unused()
        self.__check_methods_unused()
        self.__check_complexity()
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
            methods_reg = r"!\w+([a-z]+_[a-z]+\(|\d+[a-zA-Z]+\(|_[a-z]+\(|[A-Z][a-z]+[A-Z][a-z]+\(|[A-Z]+\(.*\))"
            self.__find_errors(methods_reg, CheckName.METHODS)

        if self.__config.naming.classes == State.PASCAL_CASE.value:
            c_reg = r"class\s[a-z]"
            self.__find_errors(c_reg, CheckName.CLASSES)

    def __check_var_unused(self) -> None:
        """Проверка на неиспользуемые переменные и методы"""
        if self.__config.usage.unused_vars:
            declared_vars = set()
            var_decl_lines = {}
            used_vars = {}

            var_decl_pattern = r"(?:int|double|float|String|boolean|char|byte|short|long)\s+([a-zA-Z_]\w*)\s*[;=]"
            var_use_pattern = r"\b([a-zA-Z_]\w*)\b(?!\s*\(|\.)"

            for i, line in enumerate(self.formated_java_doc):
                # Находим объявленные переменные
                for match in re.finditer(var_decl_pattern, line):
                    declared_vars.add(match.group(1))
                    var_decl_lines[match.group(1)] = i + 1

                # Находим используемые переменные
                for match in re.finditer(var_use_pattern, line):
                    var_name = match.group(1)
                    if var_name not in used_vars and var_name in declared_vars:
                        used_vars[var_name] = 1
                    elif var_name in used_vars:
                        used_vars[var_name] += 1

            # Находим неиспользуемые переменные
            unused_vars = [var for var, count in used_vars.items() if count == 1]
            for var in unused_vars:
                self.__errors.append_var_usage_er(
                    f"Неиспользуемая переменная '{var}' в строке {var_decl_lines[var]}"
                )

    def __check_methods_unused(self) -> None:
        if self.__config.usage.unused_methods:
            declared_methods = set()
            methods_decl_lines = {}
            used_methods = set()
            method_decl_pattern = (
                r"(public|private)\s(?:static)?\s?"
                + r"(?:void|int|double|float|String|boolean|char|byte|short|long)\s+([a-zA-Z_]\w*)\("
            )
            method_use_pattern = r"\.?(([a-z]\w*)\(.*\);)"

            for i, line in enumerate(self.formated_java_doc):
                # Находим объявленные переменные
                for match in re.finditer(method_decl_pattern, line):
                    declared_methods.add(match.group(2))
                    methods_decl_lines[match.group(2)] = i + 1

                # Находим используемые переменные
                for match in re.finditer(method_use_pattern, line):
                    method_name = match.group(2)
                    if (
                        method_name not in used_methods
                        and method_name in declared_methods
                    ):
                        used_methods.add(method_name)

            # Находим неиспользуемые переменные
            unused_methods = declared_methods - used_methods
            for var in unused_methods:
                if var != "main":
                    self.__errors.append_methods_usage_er(
                        f"Неиспользуемый метод '{var}' в строке {methods_decl_lines[var]}"
                    )

    def __check_complexity(self) -> None:
        """Проверка цикломатической сложности методов"""
        current_method = None
        complexity = 1  # Базовая сложность
        bracer_count = 0

        for i, line in enumerate(self.formated_java_doc):
            if "{" in line:
                bracer_count += 1
            if "}" in line:
                bracer_count -= 1
            # Определяем начало метода
            if re.search(
                r"\b(public|private|protected)\s+[^()]+\s+[a-zA-Z_]\w*\s*\(", line
            ):
                current_method = line.split("(")[0].split()[-1]
                complexity = 1

            # Увеличиваем сложность при обнаружении условных конструкций
            if current_method:
                if re.search(r"\b(if|else if|while|for|case|catch)\b", line):
                    complexity += 1
                elif "?" in line and ":" in line:  # Тернарный оператор
                    complexity += 1

            # Определяем конец метода
            if current_method and "}" in line:
                if bracer_count == 0:
                    if complexity > self.__config.complexity.max_complexity:
                        self.__errors.append_complexity_er(
                            f"Метод '{current_method}' имеет высокую цикломатическую сложность ({complexity})"
                        )
                    current_method = None

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
        ("Неиспользуемые переменные", "red"),
        ("Неиспользуемые методы", "red"),
        ("Цикломатическая сложность", "blue"),
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
naming:
  variables: camelCase
  constants: UPPER_CASE
  methods: camelCase
  classes: PascalCase
max_consecutive_empty_lines: 2
usage:
  unused_vars: true
  unused_methods: true
complexity:
  max_complexity: 9
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
