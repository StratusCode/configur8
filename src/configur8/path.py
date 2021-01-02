from typing import List, Union

__all__ = (
    "parse",
    "Path",
)


class Path:
    def __init__(self, path: str):
        self.path = path

    def __str__(self):
        return self.path

    def __repr__(self) -> str:
        return f"<{__name__}.{self.__class__.__name__} {str(self)}>"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Path):
            return self.path == other.path

        if isinstance(other, str):
            return str(self) == other

        raise TypeError(f"Cannot compare {other!r} with <Url>")

    def open(
        self,
        mode="r",
        buffering=-1,
        encoding=None,
        errors=None,
        newline=None,
    ):
        """
        See https://docs.python.org/3/library/functions.html#open for arg
        documentation
        """
        return open(
            self.path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    def read(self) -> str:
        return self.open().read()

    def readlines(self, newline=None) -> List[str]:
        return self.open().readlines()


def parse(path: Union[str, Path]) -> Path:
    if isinstance(path, Path):
        return path

    return Path(path)
