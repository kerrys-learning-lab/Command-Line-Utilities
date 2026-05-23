import dataclasses
import datetime
import enum
import humanize
import json
import markdown_it
import pathlib
import sys
import typing
import yaml


class OutputFormat(str, enum.Enum):
    JSON = "json"
    YAML = "yaml"
    TABLE = "table"


def custom_serializer(value):
    try:
        return value.asdict()
    except AttributeError:
        return dataclasses.asdict(value)

def dump(value, format: OutputFormat) -> str:
    if format == OutputFormat.JSON:
        return json.dumps(value, indent=4, default=custom_serializer)
    if format == OutputFormat.YAML:
        return yaml.dump(value, default_flow_style=False, sort_keys=False)
    raise RuntimeError(f"Invalid format for dump: '{format}'")


def write(value, format: OutputFormat, path: pathlib.Path) -> pathlib.Path:
    path = path.with_suffix(f".{format.value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fd:
        fd.write(dump(value, format))
    return path


def stream(value, format: OutputFormat, stream: typing.IO = sys.stdout):
    stream.write(dump(value, format))


def to_string(value) -> str:
    if isinstance(value, list):
        return ", ".join([to_string(v) for v in value])
    if isinstance(value, datetime.timedelta):
        return humanize.naturaldelta(value)
    if isinstance(value, datetime.datetime):
        return humanize.naturaltime(value)
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, str):
        # if guess_is_markdown(value):
        #     return rich.markdown.Markdown(value)
        return value

    return str(value)


def guess_is_markdown(value: str) -> bool:
    md = markdown_it.MarkdownIt()
    tokens = md.parse(value)
    trivial_types = {"paragraph_open", "inline", "text", "paragraph_close"}
    for t in tokens:
        if t.type not in trivial_types and not (t.type == "inline" and not t.children):
            return True
    return False
