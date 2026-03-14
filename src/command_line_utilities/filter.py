import abc
import typing

T = typing.TypeVar("T")


class Filter(typing.Generic[T], abc.ABC):
    @abc.abstractmethod
    def accept(self, value: T) -> bool:
        """Return True if the given value is accepted by the filter."""
