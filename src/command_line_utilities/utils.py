import inspect
import rich.console
import typing


T = typing.TypeVar("T")

IS_DRY_RUN: bool = False

def first_match(collection: list[T],
                assertion: typing.Callable[[T], bool],
                default: T = None) -> T:
    for item in collection:
        if assertion(item):
            return item
    return default


def snake_case_to_words(value: str, capitalize: bool = False) -> str:
    """Convert a snake-case phrase to a space-separated phrase.

    Example: snake_case_phrase --> snake case phrase (capitalize: False)
                               --> Snake case phrase (capitalize: True)"""
    value = value.replace("_", " ")
    return value.capitalize() if capitalize else value


def class_properties(cls) -> list[str]:
    properties: list[str]|None = getattr(cls, "PROPERTIES", None)
    if properties is None:
        properties = []

        for name, _ in inspect.getmembers(cls, lambda v: isinstance(v, property)):
            properties.append(name)

        setattr(cls, "PROPERTIES", properties)

    return properties

def truncate(value, limit: int = 20) -> str|None:
    if value:
        return value[:(limit - 3)] + '...' if len(value) > limit else value

console = rich.console.Console(stderr=True)
