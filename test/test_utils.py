import command_line_utilities as clu
import faker.generator
from . import conftest


def test_first_match(entity_list: list[conftest.MockEntity]):
    actual = clu.first_match(entity_list, lambda x: x.col1 == "baz")
    assert actual.col1 == "baz"
    assert actual.col2 == "bop"


def test_first_match_no_match(
    entity_list: list[conftest.MockEntity], random_mock_entity: conftest.MockEntity
):
    actual = clu.first_match(entity_list, lambda x: x.col1 == "bop", random_mock_entity)
    assert actual.col1 == random_mock_entity.col1


def test_snake_case_to_words(faker: faker.generator.Generator):
    test_words = faker.words()
    test_words_snake_case = "_".join(test_words)
    test_words_space_separated = " ".join(test_words)
    assert clu.snake_case_to_words(test_words_snake_case) == test_words_space_separated


def test_snake_case_to_words_capitalize(faker: faker.generator.Generator):
    test_words = faker.words()
    test_words_snake_case = "_".join(test_words)
    test_words_space_separated = " ".join(test_words)
    assert (
        clu.snake_case_to_words(test_words_snake_case, capitalize=True)
        == test_words_space_separated.capitalize()
    )
