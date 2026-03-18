import command_line_utilities as clu
import typing
from . import conftest


def test_progress_with_progress_update(entity_list: list[conftest.MockEntity]):

    def entity_generator() -> typing.Generator[clu.ProgressUpdate[conftest.MockEntity]]:
        for i, e in enumerate(entity_list, 1):
            yield clu.ProgressUpdate(e, i, len(entity_list))

    with clu.Progress(
        "test_progress_with_progress_update", entity_generator
    ) as progress:
        count = 0
        for _ in progress.invoke():
            count += 1
            assert progress.task.completed == count
