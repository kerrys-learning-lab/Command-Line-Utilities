import command_line_utilities as clu
import pytest
import re
import typing
from . import conftest


# def test_table_output_formatter(
#     table_properties: dict,
#     entity_list: list[conftest.MockEntity],
#     valid_entity_filter: conftest.ValidEntityFilter,
#     expected_table_re: re.Pattern,
#     capsys,
# ):
#     uut = clu.TableOutputFormatter(
#         table_properties["title"],
#         table_properties["columns"],
#         filter=valid_entity_filter,
#         box=None,
#     )
#     with uut:
#         [uut.append(e) for e in entity_list]
#         assert len(uut) == sum(i.is_valid for i in entity_list)

#     captured = capsys.readouterr()

#     assert expected_table_re.search(captured.out)


def test_table_output_invalid_column(
    table_properties: dict, entity_list: list[typing.Any]
):
    uut = clu.TableOutputFormatter(
        table_properties["title"], table_properties["columns"], box=None
    )

    with pytest.raises(clu.TableAttributeError):
        with uut:
            for e in entity_list:
                uut.append(e)
            assert len(uut) == len(entity_list)
