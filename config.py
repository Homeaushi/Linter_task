from pathlib import Path

import yaml  # type: ignore[import]
from pydantic import BaseModel, Field

from state_enum import State


class ComplexityConfig(BaseModel):
    """BaseModel для флагов проверки сложности кода"""

    max_complexity: int = Field(
        9, gt=0, description="Максимальная допустимая цикломатическая сложность"
    )


class UsageConfig(BaseModel):
    """BaseModel для флагов проверки использования переменных и методов"""

    unused_vars: bool = Field(True, description="Проверять неиспользуемые переменные")
    unused_methods: bool = Field(True, description="Проверять неиспользуемые методы")


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

    usage: UsageConfig = Field(default_factory=UsageConfig)

    complexity: ComplexityConfig = Field(default_factory=ComplexityConfig)

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
