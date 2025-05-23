import pytest

from config import Config
from linter import Linter


@pytest.fixture
def base_config_file(tmp_path):
    config_file_1 = tmp_path / "config_without_changing.yaml"
    text_1 = """
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
    config_file_1.write_text(text_1)
    config_1 = Config.from_yaml(str(tmp_path / "config_without_changing.yaml"))
    return config_1


@pytest.fixture
def changed_config_file(tmp_path):
    config_file_2 = tmp_path / "config_with_changing.yaml"
    text_2 = """
spacing:
  max_row: 3
  around_operators: true
  after_commas: true
  around_keywords: false
naming:
  variables: disabled
  constants: UPPER_CASE
  methods: camelCase
  classes: PascalCase
max_consecutive_empty_lines: 3
usage:
  unused_vars: true
  unused_methods: false
complexity:
  max_complexity: 9
    """
    config_file_2.write_text(text_2)
    config_2 = Config.from_yaml(str(tmp_path / "config_with_changing.yaml"))
    return config_2


@pytest.fixture
def correct_linter_without_errors(tmp_path, base_config_file):
    java_code_file_1 = tmp_path / "correct_java_code.txt"
    text_1 = """
public class Calculator {
    private static final int FAX_VALUE = 100;
    private int Result;

    public void setResult(int result) {
        this.Result = result;
    }

    public int getResult() {
        return this.Result;
    }

    public int add(int a, int b) {
        return a + b;
    }

    public int subtract(int a, int b) {
        return a - b;
    }

    public int multiply(int a, int b) {
        return a * b;
    }

    public int divide(int a, int b) {
        if (b == 0) {
            throw new illegalargumentException("Divisor cannot be zero");
        }
        return a / b;
    }

    public void printResult() {
        System.out.println("Result: " + this.Result);
    }

    public static void main(String[] args) {
        Calculator myCalculator = new Calculator();

        int sum = myCalculator.add(10, 20);

        myCalculator.setResult(sum);

        int difference = myCalculator.subtract(50, 30);

        myCalculator.setResult(difference);

        int product = myCalculator.multiply(5, 6);

        myCalculator.setResult(product);

        int quotient = myCalculator.divide(100, 10);

        myCalculator.setResult(quotient);

        int finalResult = myCalculator.getResult();

        System.out.println("Final Result: " + finalResult);
    }
}
        """

    java_code_file_1.write_text(text_1)

    linter_1 = Linter(str(tmp_path / "correct_java_code.txt"), base_config_file)

    return linter_1


@pytest.fixture
def correct_linter_with_errors(tmp_path, base_config_file):
    java_code_file_3 = tmp_path / "correct_java_code.txt"
    text_3 = """
// Неправильное имя класса (должно быть PascalCase)
public class badClassName {

    // Неправильное имя константы (должно быть UPPER_CASE)
    final static int Maxsize = 10;

    // Неправильное имя переменной (должно быть camelCase)
    private String User_name;

    // Слишком много пробелов
    public void  printMessage (String message )  {
        System.out.println(message);
    }


    // Неправильное имя метода (должно быть camelCase)
    public void    PrintUserInfo() {
        // Неправильное имя локальной переменной
        int user_age = 25;
    }
        """

    java_code_file_3.write_text(text_3)

    linter_3 = Linter(str(tmp_path / "correct_java_code.txt"), base_config_file)

    return linter_3


@pytest.fixture
def linter_with_errors(tmp_path, changed_config_file):
    java_code_file_2 = tmp_path / "uncorrect_java_code.txt"
    text_2 = """
// Неправильное имя класса (должно быть PascalCase)
public class badClassName {

    // Неправильное имя константы (должно быть UPPER_CASE)
    final static int Maxsize = 10;

    // Неправильное имя переменной (должно быть camelCase)
    private String User_name;

    // Слишком много пробелов
    public void  printMessage (String message )  {
        System.out.println(message);
    }


    // Неправильное имя метода (должно быть camelCase)
    public void    PrintUserInfo() {
        // Неправильное имя локальной переменной
        int user_age = 25;
    }
        """

    java_code_file_2.write_text(text_2)

    linter_2 = Linter(str(tmp_path / "uncorrect_java_code.txt"), changed_config_file)

    return linter_2


def test_config_without_changing(base_config_file):
    assert base_config_file.spacing.max_row == 2
    assert base_config_file.naming.classes == "PascalCase"
    assert base_config_file.spacing.around_operators is True
    assert base_config_file.max_consecutive_empty_lines == 2
    assert base_config_file.usage.unused_methods is True


def test_config_with_changing(changed_config_file):
    assert changed_config_file.spacing.max_row == 3
    assert changed_config_file.spacing.around_keywords is False
    assert changed_config_file.max_consecutive_empty_lines == 3
    assert changed_config_file.usage.unused_methods is False


def test_linting_correct_java_file(correct_linter_without_errors):
    errors = correct_linter_without_errors.linting()
    assert errors.get_all_errors()[0] == []
    assert errors.get_all_errors()[1] == []
    assert errors.get_all_errors()[2] == []


def test_linting_base_config_wrong_java_file(correct_linter_with_errors):
    errors = correct_linter_with_errors.linting()

    assert (
        errors.get_lines_errors()[0] == "Слишком много пустых строк подряд в строке 16"
    )

    assert (
        errors.get_spacing_errors()[0]
        == """Лишние пробелы в строке 12: 'public void  printMessage (String message )  {'"""
    )

    assert (
        errors.get_naming_errors()[0]
        == """Неправильное название переменной в строке 9: 'private String User_name;'"""
    )


def test_linting_changed_config_wrong_java_file(linter_with_errors):
    errors = linter_with_errors.linting()

    assert errors.get_lines_errors() == []
    assert (
        errors.get_spacing_errors()[0]
        == """Лишние пробелы в строке 18: 'public void    PrintUserInfo() {'"""
    )
    assert (
        errors.get_naming_errors()[0]
        == """Неправильное название константы в строке 6: 'final static int Maxsize = 10;'"""
    )
