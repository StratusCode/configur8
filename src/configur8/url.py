import typing as t
from urllib.parse import parse_qs, urlparse, ParseResult

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
    def protocol(self) -> str | None:
        if self.result.scheme == "":
            return None

        return self.result.scheme

    @property
    def username(self) -> str | None:
        return self.result.username

    @property
    def password(self) -> str | None:
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
    def port(self) -> int | None:
        return self.result.port

    @property
    def path(self) -> str | None:
        path = self.result.path

        if self.result.netloc == "":
            path = "/".join(self.result.path.split("/")[1:])

            if path:
                path = "/" + path

        if path == "":
            return None

        return path

    @property
    def query(self) -> t.Dict[str, t.List[str]] | None:
        if self.result.query == "":
            return None

        return parse_qs(
            self.result.query,
            keep_blank_values=True,
            strict_parsing=True,
        )

    @property
    def fragment(self) -> str | None:
        if self.result.fragment == "":
            return None

        return self.result.fragment

    # support the str methods
    def __getattr__(self, name):
        return getattr(str(self), name)


def parse(data: str | Url) -> Url:
    if isinstance(data, Url):
        return data

    return Url(urlparse(data))
