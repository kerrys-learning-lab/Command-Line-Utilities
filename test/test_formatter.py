import command_line_utilities as clu
import json
import os
import pathlib
import pytest
import re
import yaml
from . import conftest


# def test_output_formatter_create_table_formatter(
#     table_properties: dict,
#     entity_list: list[conftest.MockEntity],
#     valid_entity_filter: conftest.ValidEntityFilter,
#     expected_table_re: re.Pattern,
#     capsys,
# ):
#     uut = clu.OutputFormatter.create(
#         clu.OutputFormat.TABLE, **table_properties, filter=valid_entity_filter
#     )

#     assert isinstance(uut, clu.TableOutputFormatter)
#     assert uut.title == table_properties["title"]
#     assert uut.columns == table_properties["columns"]

#     with uut:
#         [uut.append(e) for e in entity_list]

#     captured = capsys.readouterr()

#     assert expected_table_re.search(captured.out)


def test_output_formatter_create_stream_formatter_json(
    entity_list: list[conftest.MockEntity],
    valid_entity_filter: conftest.ValidEntityFilter,
    capsys,
):
    for stream in ["out", "err"]:
        uut = clu.OutputFormatter.create(
            clu.OutputFormat.JSON, filter=valid_entity_filter, stderr=stream == "err"
        )
        assert isinstance(uut, clu.StreamOutputFormatter)
        with uut:
            [uut.append(e) for e in entity_list]

        captured = capsys.readouterr()
        actual: list[dict] = json.loads(getattr(captured, stream))

        assert sum(e.is_valid for e in entity_list) == len(uut)
        for i, e in enumerate(entity_list):
            if not e.is_valid:
                continue
            assert e == conftest.MockEntity(**actual[i])


def test_output_formatter_create_stream_formatter_yaml(
    entity_list: list[conftest.MockEntity],
    valid_entity_filter: conftest.ValidEntityFilter,
    capsys,
):
    for stream in ["out", "err"]:
        uut = clu.OutputFormatter.create(
            clu.OutputFormat.YAML, filter=valid_entity_filter, stderr=stream == "err"
        )
        assert isinstance(uut, clu.StreamOutputFormatter)
        with uut:
            [uut.append(e) for e in entity_list]

        captured = capsys.readouterr()
        actual: list[dict] = list(yaml.safe_load_all(getattr(captured, stream)))

        assert sum(e.is_valid for e in entity_list) == len(uut)
        for i, e in enumerate(entity_list):
            if not e.is_valid:
                continue
            assert e == conftest.MockEntity(**actual[i])


def test_output_formatter_create_file_formatter(
    entity_list: list[conftest.MockEntity],
    valid_entity_filter: conftest.ValidEntityFilter,
    tmp_path: pathlib.Path,
):
    uut = clu.OutputFormatter.create(
        clu.OutputFormat.JSON,
        root=tmp_path,
        entity_id="col1",
        filter=valid_entity_filter,
    )
    assert isinstance(uut, clu.FileOutputFormatter)

    with uut:
        [uut.append(e) for e in entity_list]

    file_paths = [item for item in tmp_path.iterdir() if item.is_file()]

    assert sum(e.is_valid for e in entity_list) == len(file_paths)

    for p in file_paths:
        assert os.path.samefile(tmp_path, p.parent)
        assert p.name.startswith("MockEntity")
        assert p.suffix == ".json"

    for e in entity_list:
        if not e.is_valid:
            continue

        actual = None
        for p in file_paths:
            if e.col1 in p.name:
                with open(p) as fd:
                    actual = json.load(fd)
                    actual = conftest.MockEntity(**actual)
                    break

        assert e == actual


def test_output_formatter_create_file_formatter_2(
    entity_list: list[conftest.MockEntity],
    valid_entity_filter: conftest.ValidEntityFilter,
    tmp_path: pathlib.Path,
):
    def entity_type_cb(item):
        return "FakeEntity"

    def entity_id_cb(item):
        return id(item)

    uut = clu.OutputFormatter.create(
        clu.OutputFormat.JSON,
        root=tmp_path,
        entity_type=entity_type_cb,
        entity_id=entity_id_cb,
        filter=valid_entity_filter,
    )

    with uut:
        [uut.append(e) for e in entity_list]

    file_paths = [item for item in tmp_path.iterdir() if item.is_file()]

    for p in file_paths:
        assert p.name.startswith("FakeEntity")


def test_output_formatter_create_file_formatter_3(
    entity_list: list[conftest.MockEntity],
    valid_entity_filter: conftest.ValidEntityFilter,
    tmp_path: pathlib.Path,
):
    def filename_cb(item):
        return f"FakeEntity--{id(item)}"

    uut = clu.OutputFormatter.create(
        clu.OutputFormat.JSON,
        root=tmp_path,
        filestem_cb=filename_cb,
        filter=valid_entity_filter,
    )

    with uut:
        [uut.append(e) for e in entity_list]

    file_paths = [item for item in tmp_path.iterdir() if item.is_file()]

    for p in file_paths:
        assert p.name.startswith("FakeEntity")


def test_output_formatter_create_invalid():
    with pytest.raises(RuntimeError):
        clu.OutputFormatter.create(clu.OutputFormat.TABLE)
    with pytest.raises(RuntimeError):
        clu.OutputFormatter.create(clu.OutputFormat.TABLE, title="Foo")
    with pytest.raises(RuntimeError):
        clu.OutputFormatter.create(clu.OutputFormat.TABLE, columns=["foo", "bar"])
