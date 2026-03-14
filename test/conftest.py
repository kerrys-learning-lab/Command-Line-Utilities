import click.testing
import command_line_utilities as clu
import dataclasses
import faker.generator
import pytest
import re

FAKER = faker.Faker()


@dataclasses.dataclass
class MockEntity:
    col1: str
    col2: str
    col_3: int
    is_valid: bool


@dataclasses.dataclass
class InvalidMockEntity:
    col1: str
    # Missing col2 attribute!
    col_3: int
    is_valid: bool


class ValidEntityFilter(clu.Filter[MockEntity]):
    def accept(self, value: MockEntity):
        return value.is_valid


@pytest.fixture
def valid_entity_filter() -> clu.Filter:
    return ValidEntityFilter()


@pytest.fixture
def click_runner() -> click.testing.CliRunner:
    return click.testing.CliRunner()


@pytest.fixture
def table_properties() -> dict:
    return {
        "title": "Title",
        "columns": ["Col1", "Col2", "Col 3"],
        "box": None,
    }


@pytest.fixture
def entity_list() -> list[MockEntity]:
    # NOTE: This also tests converting the column human-readable name to a
    #       sanitized attribute name
    return [
        MockEntity(col1="foo", col2="bar", col_3=7, is_valid=True),
        MockEntity(col1="baz", col2="bop", col_3=42, is_valid=True),
        InvalidMockEntity(col1="bam", col_3=9, is_valid=False),
    ]


@pytest.fixture
def expected_table_re() -> re.Pattern:
    # NOTE: Should be kept in sync with valid entires in 'entity_list' above
    return re.compile(
        r"\s+Title\s+Col1\s+Col2\s+Col 3\s+foo\s+bar\s+7\s+baz\s+bop\s+42\s+"
    )


@pytest.fixture
def random_mock_entity(faker: faker.generator.Generator) -> MockEntity:
    return MockEntity(
        col1=faker.word(), col2=faker.word(), col_3=faker.word(), is_valid=True
    )
