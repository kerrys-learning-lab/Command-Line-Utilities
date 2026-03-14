import abc
import pathlib
import sys
import typing
from .filter import Filter
from .output import OutputFormat, stream, write
from .table import ObjectListTable
from .utils import snake_case_to_words


class OutputFormatter(abc.ABC):
    @staticmethod
    def create(
        format: OutputFormat,
        *,
        title: str = None,
        columns: list[str] = None,
        root: pathlib.Path = None,
        filter: Filter = None,
        entity_type: str | typing.Callable[[typing.Any], str] = None,
        entity_id: str | typing.Callable[[typing.Any], str] = None,
        filestem_cb: typing.Callable[[typing.Any], pathlib.Path] = None,
        stderr: bool = False,
        **kwargs,
    ) -> "OutputFormatter":
        if format == OutputFormat.TABLE:
            if not title or not columns:
                raise RuntimeError(
                    "'title' and 'columns' are required when format is 'table'"
                )
            if root:
                raise RuntimeError(
                    "Output directory not allowed then format is 'table'"
                )
            return TableOutputFormatter(title, columns, filter=filter, **kwargs)

        if root:
            return FileOutputFormatter(
                root,
                format,
                filter=filter,
                entity_type=entity_type,
                entity_id=entity_id,
                filestem_cb=filestem_cb,
                **kwargs,
            )

        return StreamOutputFormatter(format, filter=filter, stderr=stderr, **kwargs)

    def __init__(self, format: OutputFormat, filter: Filter = None, **kwargs):
        super().__init__()
        self.format = format
        self.filter = filter
        self.kwargs = kwargs
        self.values = []

    def append(self, value):
        if self.filter and not self.filter.accept(value):
            return

        self.values.append(value)

    def __enter__(self):
        return self

    @abc.abstractmethod
    def __exit__(self, exc_type, exc, tb):
        """Derived classes should produce their output when the context is
        exited"""

    def __len__(self) -> int:
        return len(self.values)

    def _as_dict(self, value) -> dict:
        return value.asdict() if hasattr(value, "asdict") else value.__dict__

    def _all_as_dict(self) -> list[dict]:
        return [self._as_dict(v) for v in self.values]


class FileOutputFormatter(OutputFormatter):
    def __init__(
        self,
        root: pathlib.Path,
        format: OutputFormat,
        filter: Filter = None,
        entity_type: str | typing.Callable[[typing.Any], str] = None,
        entity_id: str | typing.Callable[[typing.Any], str] = None,
        filestem_cb: typing.Callable[[typing.Any], pathlib.Path] = None,
        **kwargs,
    ):
        super().__init__(format, filter=filter, **kwargs)
        self.format = format
        self.root = root
        self.filestem_cb = filestem_cb
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.suffix = f".{self.format.value}" if self.format else None

    def _get_entity_filename(self, entity) -> pathlib.Path:
        if self.filestem_cb:
            stem = self.filestem_cb(entity)
        else:
            stem = f"{self._get_entity_type(entity)}-{self._get_entity_id(entity)}"

        return self.root / stem

    def _get_entity_type(self, entity) -> str:
        if isinstance(self.entity_type, str):
            return self.entity_type

        if callable(self.entity_type):
            return self.entity_type(entity)

        return entity.__class__.__name__

    def _get_entity_id(self, entity) -> str:
        if isinstance(self.entity_id, str):
            return getattr(entity, self.entity_id)

        if callable(self.entity_id):
            return self.entity_id(entity)

        return str(id(entity))

    def __exit__(self, exc_type, exc, tb):
        for v in self.values:
            write(self._as_dict(v), self.format, self._get_entity_filename(v))


class StreamOutputFormatter(OutputFormatter):
    def __init__(
        self,
        format: OutputFormat,
        filter: Filter = None,
        stderr: bool = False,
        **kwargs,
    ):
        super().__init__(format, filter=filter, **kwargs)
        self.stderr = stderr

    def __exit__(self, exc_type, exc, tb):
        data = self._all_as_dict()
        io_stream = sys.stderr if self.stderr else sys.stdout

        if self.format == OutputFormat.YAML:
            for d in data:
                io_stream.write("---\n")
                stream(d, OutputFormat.YAML, stream=io_stream)
        else:
            stream(data, OutputFormat.JSON, stream=io_stream)


class TableOutputFormatter(OutputFormatter):
    def __init__(self, title: str, columns: list[str], filter: Filter = None, **kwargs):
        super().__init__(OutputFormat.TABLE, filter=filter, **kwargs)
        self.title = title
        self.columns = (
            [snake_case_to_words(c, capitalize=True) for c in columns]
            if columns
            else []
        )

    def __exit__(self, exc_type, exc, tb):
        table = ObjectListTable(self.title, *self.columns, **self.kwargs)

        for v in self.values:
            table.add_row(v)

        table.print()
