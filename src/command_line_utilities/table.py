import rich.box
import rich.table
from .output import to_string


class TableError(RuntimeError):
    """Raised when a table operation results in an error"""


class TableAttributeError(TableError):
    """Raised when an entity added to a table is missing a required attribute"""


class ObjectTable:
    DEFAULT_NESTED_TABLE_KWARGS = {
        "show_header": False,
        "box": rich.box.SIMPLE,
    }

    def __init__(self, title: str, *columns: list[str], **kwargs):
        # Allow title=False to disable the title, but title=None uses default
        title = None if title is False else (title or self.title)
        columns = columns or ["Attribute", "Value"]
        self.table = rich.table.Table(*columns, title=title, **kwargs)

    def add_attributes(self, object, attributes: list[str], prefix: str = None):
        for attr in attributes:
            attr_column_text = f"{prefix} - {attr}" if prefix else attr
            attr_name = _sanitize_attr_name(attr)
            attr_value = getattr(object, attr_name)
            attr_value = to_string(attr_value)

            self.add_row(attr_column_text, attr_value)

    def add_row(self, key: str, value: str):
        self.table.add_row(key, value)

    def add_nested_table(
        self, name: str, object, attributes: list[str], prefix: str = None
    ):
        nested = ObjectTable(False, **ObjectTable.DEFAULT_NESTED_TABLE_KWARGS)
        nested.add_attributes(object, attributes, prefix=prefix)
        self.table.add_row(name, nested.table)


class ObjectListTable:
    def __init__(self, title: str, *columns: list[str], **kwargs):
        self.attr_names = [_sanitize_attr_name(col_name) for col_name in columns]
        self.table = rich.table.Table(*columns, title=title, **kwargs)

    def add_row(self, object):
        try:
            row = []
            for attr in self.attr_names:
                attr_value = to_string(getattr(object, attr))
                row.append(attr_value)
            self.table.add_row(*row)
        except AttributeError as ex:
            raise TableAttributeError(str(ex))

    def print(self, stderr: bool = False):
        console = rich.console.Console(stderr=stderr)
        console.print(self.table)


def _sanitize_attr_name(attr_name: str) -> str:
    return attr_name.lower().replace(" ", "_")


def create(title: str, attributes: list[str], entries: list) -> rich.table:
    table = rich.table.Table(*attributes, title=title)

    for ent in entries:
        row = []
        for col_name in attributes:
            attr_name = _sanitize_attr_name(col_name)
            attr_value = to_string(getattr(ent, attr_name))
            row.append(attr_value)
        table.add_row(*row)
