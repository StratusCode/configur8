from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from urllib.parse import parse_qs
from urllib.parse import ParseResult
from urllib.parse import urlparse

__all__ = (
    "parse",
    "Url",
)


class Url:
    result: ParseResult

    def __init__(self, result: ParseResult):
        self.result = result

    def __str__(self):
        return self.result.geturl()

    def __repr__(self):
        return f"<{__name__}.{self.__class__.__name__} {str(self)}>"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Url):
            return self.result == other.result

        if isinstance(other, str):
            return str(self) == other

        raise TypeError(f"Cannot compare {other!r} with <Url>")

    @property
    def protocol(self) -> Optional[str]:
        if self.result.scheme == "":
            return None

        return self.result.scheme

    @property
    def username(self) -> Optional[str]:
        return self.result.username

    @property
    def password(self) -> Optional[str]:
        return self.result.password

    @property
    def host(self) -> str:
        netloc = self.result.netloc

        if netloc == "":
            return self.result.path.split("/")[0]

        try:
            host = netloc.split("@")[1]
        except IndexError:
            # no username/password
            return netloc.split(":")[0]

        return host.split(":")[0]

    @property
    def port(self) -> Optional[int]:
        return self.result.port

    @property
    def path(self) -> Optional[str]:
        path = self.result.path

        if self.result.netloc == "":
            path = "/".join(self.result.path.split("/")[1:])

            if path:
                path = "/" + path

        if path == "":
            return None

        return path

    @property
    def query(self) -> Optional[Dict[str, List[str]]]:
        if self.result.query == "":
            return None

        return parse_qs(
            self.result.query,
            keep_blank_values=True,
            strict_parsing=True,
        )

    @property
    def fragment(self) -> Optional[str]:
        if self.result.fragment == "":
            return None

        return self.result.fragment

    # support the str methods
    def __getattr__(self, name):
        return getattr(str(self), name)


def parse(data: Union[str, Url]) -> Url:
    if isinstance(data, Url):
        return data

    return Url(urlparse(data))
