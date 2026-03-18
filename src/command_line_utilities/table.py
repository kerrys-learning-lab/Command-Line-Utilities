import rich.box
import rich.table
from .output import to_string
from .utils import class_properties


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
    def create(*columns: list[str], title: str = None) -> "Table":
        return Table(*columns, title=title, **Table.DEFAULT_TABLE_KWARGS)

    def __init__(self, *columns: list[str], title: str = None, **kwargs):
        self.table = rich.table.Table(*columns, title=title, **kwargs)

    def add_row(self, key: str, *value):
        self.table.add_row(key, *value)

    def print(self, stderr: bool = False):
        console = rich.console.Console(stderr=stderr)
        console.print(self.table)

    def __rich__(self) -> rich.table.Table:
        return self.table


class ObjectTable(Table):
    @staticmethod
    def create(*columns: list[str], title: str = None) -> "ObjectTable":
        return ObjectTable(*columns, title=title, **ObjectTable.DEFAULT_TABLE_KWARGS)

    @staticmethod
    def create_nested(*columns: list[str], title: str = None) -> "ObjectTable":
        return ObjectTable(
            *columns, title=title, **ObjectTable.DEFAULT_NESTED_TABLE_KWARGS
        )

    def __init__(self, *columns: list[str], title: str = None, **kwargs):
        columns = columns or ["Attribute", "Value"]
        super().__init__(*columns, title=title, **kwargs)

    def add_attributes(self, object, attributes: list[str], prefix: str = None):
        for attr in attributes:
            attr_column_text = f"{prefix} - {attr}" if prefix else attr
            attr_name = _sanitize_attr_name(attr)
            attr_value = getattr(object, attr_name)
            attr_value = to_string(attr_value)

            self.add_row(attr_column_text, attr_value)


class ClassPropertyTable(Table):
    @staticmethod
    def create(cls) -> "ClassPropertyTable":
        table = Table("Property", "Type", title=f"{cls.__name__} Properties")

        for p in class_properties(cls):
            cls_property = getattr(cls, p)
            return_type = cls_property.fget.__annotations__.get("return")
            return_type = getattr(return_type, "__name__", return_type)
            table.add_row(p, str(return_type))

        return table


class ObjectListTable(Table):
    def __init__(self, *columns: list[str], title: str = None, **kwargs):
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
