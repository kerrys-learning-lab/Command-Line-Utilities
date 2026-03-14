import typing


T = typing.TypeVar("T")


def first_match(
    collection: list[T], assertion: typing.Callable[[T], bool], default=T | None
) -> T:
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
