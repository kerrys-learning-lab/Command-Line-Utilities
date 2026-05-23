import rich.progress
import typing
from . import utils

T = typing.TypeVar("T")


class ProgressUpdate(typing.Generic[T]):
    def __init__(self, value: T, completed: int, total: int):
        self.value: T = value
        self.completed: int = completed
        self.total: int = total


class Progress(typing.Generic[T]):
    class Task:
        def __init__(self,
                     title: str,
                     progress: rich.progress.Progress,
                     show_each: bool = False):
            self.title = title
            self.task: rich.progress.TaskID|None = None
            self.rich_progress: rich.progress.Progress = progress
            self.completed = 0
            self.total = None
            self.show_each = show_each

        def update(self, value):
            self.completed += 1

            if isinstance(value, ProgressUpdate):
                self.total = value.total
                value = value.value

            self.rich_progress.update(self.task, **self._kwargs(value))

            return value

        def __enter__(self) -> "Progress.Task":
            self.start()
            return self

        def __exit__(self, exc_type, exc, tb):
            self.stop()

        def start(self):
            self.task = self.rich_progress.add_task(self.title, **self._kwargs())

        def stop(self):
            self.rich_progress.update(self.task, visible=False)

        def _kwargs(self, value=None):
            return {
                "completed": self.completed,
                "total": self.total,
                "each": str(value) if (self.show_each and value) else "",
                "refresh": True,
            }

    def __init__(self,
                 title: str,
                 generator_callable: typing.Generator[ProgressUpdate[T], None, None],
                 show_text = True,
                 show_bar = True,
                 show_progress = True,
                 show_mofn = True,
                 show_each = True,
                 transient = True):
        self.generator_callable = generator_callable

        columns = []
        if show_text:
            columns.append(
                rich.progress.TextColumn("[progress.description]{task.description}")
            )
        if show_bar:
            columns.append(rich.progress.BarColumn())
        if show_progress:
            columns.append(rich.progress.TaskProgressColumn())
        if show_mofn:
            columns.append(rich.progress.MofNCompleteColumn())
        if show_each:
            columns.append(rich.progress.TextColumn("{task.fields[each]}"))

        self.progress = rich.progress.Progress(*columns,
                                               console=utils.console,
                                               transient=transient)
        self.task = Progress.Task(title, self.progress, show_each=show_each)

    def __enter__(self):
        self.progress.start()
        self.task.start()
        return self

    def new_task(self, title: str) -> Task:
        return Progress.Task(title, self.progress)

    def invoke(self, *args, **kwargs) -> typing.Generator[T, None, None]:
        for value in self.generator_callable(*args, **kwargs):
            yield self.task.update(value)

    def __call__(self, *args, **kwargs) -> typing.Generator[T, None, None]:
        return self.invoke(*args, **kwargs)

    def __exit__(self, exc_type, exc, tb):
        if self.progress:
            self.progress.stop()
