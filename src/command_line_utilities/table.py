import rich.box
import rich.table
from .output import to_string
from . import utils


class TableError(RuntimeError):
    """Raised when a table operation results in an error"""


class TableAttributeError(TableError):
    """Raised when an entity added to a table is missing a required attribute"""


class Table:
    DEFAULT_TABLE_KWARGS = {
        "show_lines": True,
    }

    DEFAULT_NESTED_TABLE_KWARGS = {
        "show_header": False,
        "show_lines": False,
        "box": rich.box.SIMPLE,
    }

    @staticmethod
    def create(*columns: str, title: str|None = None) -> "Table":
        return Table(*columns, title=title, **Table.DEFAULT_TABLE_KWARGS)

    def __init__(self, *columns: str, title: str|None = None, **kwargs):
        self.table = rich.table.Table(*columns, title=title, **kwargs)

    def add_row(self, *value):
        self.table.add_row(*value)

    def print(self, stderr: bool = False):
        utils.console.print(self.table)

    def __rich__(self) -> rich.table.Table:
        return self.table


class ObjectTable(Table):
    @staticmethod
    def create(*columns: str, title: str|None = None) -> "ObjectTable":
        return ObjectTable(*columns, title=title, **ObjectTable.DEFAULT_TABLE_KWARGS)

    @staticmethod
    def create_nested(*columns: str, title: str|None = None) -> "ObjectTable":
        return ObjectTable(
            *columns, title=title, **ObjectTable.DEFAULT_NESTED_TABLE_KWARGS
        )

    def __init__(self, *columns: str, title: str|None = None, **kwargs):
        columns = columns or ("Attribute", "Value")
        super().__init__(*columns, title=title, **kwargs)

    def add_attributes(self, object, attributes: list[str], prefix: str|None = None):
        for attr in attributes:
            attr_column_text = f"{prefix} - {attr}" if prefix else attr
            attr_name = _sanitize_attr_name(attr)
            attr_value = getattr(object, attr_name)
            attr_value = to_string(attr_value)

            self.add_row(attr_column_text, attr_value)


class ClassPropertyTable:
    @staticmethod
    def create(obj) -> "Table":
        table = Table("Property", "Type", title=f"{obj.__name__} Properties")

        for p in utils.class_properties(obj):
            cls_property = getattr(obj, p)
            return_type = cls_property.fget.__annotations__.get("return")
            return_type = getattr(return_type, "__name__", return_type)
            table.add_row(p, str(return_type))

        return table


class ObjectListTable(Table):
    def __init__(self, *columns: str, title: str|None = None, **kwargs):
        super().__init__(*columns, title=title, **kwargs)
        self.attr_names = [_sanitize_attr_name(col_name) for col_name in columns]

    def add_object(self, object):
        try:
            row = []
            for attr in self.attr_names:
                attr_value = to_string(getattr(object, attr))
                row.append(attr_value)
            self.add_row(*row)
        except AttributeError as ex:
            raise TableAttributeError(str(ex))


def _sanitize_attr_name(attr_name: str) -> str:
    return attr_name.lower().replace(" ", "_")
