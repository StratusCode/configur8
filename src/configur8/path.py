from typing import List, Optional
from typing import Union

__all__ = (
    "parse",
    "Path",
)


class Path:
    path: str

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
        mode: str = "r",
        buffering: int = -1,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
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
        ret = self.open(mode="rt", encoding="utf-8").read()

        return ret  # type: ignore

    def readlines(self, newline: Optional[str] = None) -> List[str]:
        ret = self.open(newline=newline).readlines()

        return ret  # type: ignore


def parse(path: Union[str, Path]) -> Path:
    if isinstance(path, Path):
        return path

    return Path(path)
