import rich.progress
import typing


T = typing.TypeVar("T")


class ProgressUpdate(typing.Generic[T]):
    def __init__(self, value: T, completed: int, total: int):
        self.value: T = value
        self.completed: int = completed
        self.total: int = total


class Progress(typing.Generic[T]):
    def __init__(
        self,
        title: str,
        generator_callable: typing.Generator[ProgressUpdate[T], None, None],
        show_text=True,
        show_bar=True,
        show_progress=True,
        show_mofn=True,
        show_each=True,
        transient=True,
    ):
        self.title = title
        self.generator_callable = generator_callable
        self.progress = None
        self.task = None
        self.update = {
            "completed": 0,
            "total": None,
            "refresh": True,
        }

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
            self.update["each"] = ""

        self.progress = rich.progress.Progress(*columns, transient=transient)

    def __enter__(self):
        self.progress.start()
        self.task = self.progress.add_task(self.title, **self.update)
        return self

    def invoke(self, *args, **kwargs) -> typing.Generator[T, None, None]:
        for value in self.generator_callable(*args, **kwargs):
            self.update["completed"] = self.update["completed"] + 1

            if isinstance(value, ProgressUpdate):
                self.update["total"] = value.total
                value = value.value

            if "each" in self.update:
                self.update["each"] = str(value)

            self.progress.update(self.task, **self.update)

            yield value

    def __call__(self, *args, **kwargs) -> typing.Generator[T, None, None]:
        return self.invoke(*args, **kwargs)

    def __exit__(self, exc_type, exc, tb):
        if self.progress:
            self.progress.stop()
