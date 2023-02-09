"""
Type-safe configuration and validation.

Python

An example ``config.py`` file:

```python
import typing as t

from configur8 import cfg


class BaseMySQL:
    username: str
    password: str
    database: str


class MySQLHost:
    host: str
    port: int = 3306


class MySQLSocket:
    socket: str


MySQL = t.Union[MySQLHost, MySQLSocket]


class Config:
    mysql: MySQL


def load(path: Optional[str] = None) -> Config:
    return cfg.load(Config, path)
```
"""

import inspect
import json
import re
import typing as t
import typing_extensions as te

import yaml

from configur8 import env, types


Data = t.TypeVar("Data")
PathLike = t.List[t.Union[str, int]]
DataValues = t.Dict[str, t.Any]
SupportedFormats = te.Literal["yaml", "json"]


class Path:
    data: t.List[t.Union[str, int]]

    match = re.compile(r"([a-zA-Z0-9_-]+)\.?|\[([0-9]+)\]\.?")

    def __init__(self, path: PathLike) -> None:
        self.data = list(path)

    def __str__(self) -> str:
        ret = ""

        first = True

        for count, part in enumerate(self.data):
            if isinstance(part, str):
                if not first:
                    ret += "."

                ret += part
            elif isinstance(part, int):
                ret += f"[{part}]"
            else:
                raise TypeError(
                    f"Unexpected {type(part)} at {count} in {self.data!r}"
                )

            first = False

        return ret

    def __iter__(self):
        return iter(self.data)

    @staticmethod
    def decode(path: str) -> "Path":
        ret: t.List[t.Union[str, int]] = []

        for s, i in Path.match.findall(path):
            if len(s) > 0:
                try:
                    ret.append(int(s))
                except ValueError:
                    ret.append(s)
            elif len(i) > 0:
                ret.append(int(i))
            else:
                raise RuntimeError

        return Path(ret)

    def __add__(self, other: t.Any) -> "Path":
        if isinstance(other, str):
            return Path(self.data + Path.decode(other).data)
        elif isinstance(other, Path):
            return Path(self.data + other.data)
        else:
            raise TypeError(f"{other!r}<{type(other)}>")


class ConfigError(Exception):
    path: Path

    def __init__(
        self,
        path: t.Union[PathLike, Path, str],
        message: str,
    ) -> None:
        self.message = message

        if isinstance(path, Path):
            self.path = path
        elif isinstance(path, str):
            self.path = Path.decode(path)
        else:
            self.path = Path(path)

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def into(  # noqa: C901
    config: t.Type[Data],
    data: t.Any,
    _path: t.Optional[PathLike] = None,
) -> Data:
    data_dict = types.to_dict(data)

    ret = config()
    path = (_path or [])

    def parse_value(
        type_: t.Any,
        value: t.Any,
        name: t.Union[str, int],
    ) -> t.Any:
        new_path = path + [name]

        if type_ is str:
            if not isinstance(value, str):
                raise ConfigError(
                    new_path,
                    f"Expected str, got {value!r}",
                )

            return value
        elif type_ is int:
            if not isinstance(value, int):
                raise ConfigError(
                    new_path,
                    f"Expected int, got {value!r}",
                )

            return value
        elif type_ is bool:
            if not isinstance(value, bool):
                raise ConfigError(
                    new_path,
                    f"Expected bool, got {value!r}",
                )

            return value
        elif type_ is float:
            if not isinstance(value, float):
                raise ConfigError(
                    new_path,
                    f"Expected float, got {value!r}",
                )

            return value
        elif isinstance(type_, types.NoneType):
            if value is not None:
                raise ConfigError(
                    new_path,
                    f"Expected None, got {value!r}",
                )

            return value
        elif value is None:
            if isinstance(type_, types.NoneType):
                return value

            if types.is_union_type(type_):
                if types.NoneType in type_.__args__:
                    return value

            if types.is_optional_type(type_):
                return value

            raise ConfigError(new_path, "Unexpected None")
        elif inspect.isclass(type_):
            return into(type_, value, path)
        elif types.is_union_type(type_):
            for union_arg in type_.__args__:
                try:
                    return parse_value(union_arg, value, name)
                except ConfigError:
                    pass

            raise ConfigError(new_path, "expected one of the union types")
        elif types.is_list_type(type_):
            if not isinstance(value, list):
                raise ConfigError(new_path, f"Expected list, got {value!r}")

            return [
                parse_value(type_.__args__[0], item, i)
                for i, item in enumerate(value)
            ]
        elif types.is_dict_type(type_):
            if not isinstance(value, dict):
                raise ConfigError(new_path, f"Expected dict, got {value!r}")

            ret = {}

            for k, v in value.items():
                k = parse_value(type_.__args__[0], k, k)
                v = parse_value(type_.__args__[1], v, k)

                ret[k] = v

            return ret
        else:
            raise ConfigError(
                path,
                f"Unexpected type {type_!r} for {name!r}, got {value!r}"
            )

    annotations, default_values = types.get_annotation(config)

    for name, value in default_values.items():
        if name not in data_dict:
            data_dict[name] = value

    for name, type_ in annotations.items():
        try:
            data_value = data_dict[name]
        except KeyError:
            raise ConfigError(name, "missing")

        parsed_value = parse_value(type_, data_value, name)

        setattr(ret, name, parsed_value)

    return ret


def parse(
    config: t.Type[Data],
    data: str,
    format: SupportedFormats = "yaml",
) -> Data:
    """
    Parse config from a string.

    :param config: The annotated config class to load into.
    :param data: The encoded config data.
    """
    if format == "yaml":
        parsed_data = yaml.safe_load(data)
    elif format == "json":
        parsed_data = json.loads(data)
    else:
        raise ValueError(f"Unknown format {format!r}")

    return into(config, parsed_data)


def load(
    config: t.Type[Data],
    path: t.Optional[str] = None,
    format: SupportedFormats = "yaml",
) -> Data:
    """
    Load a config from a file.

    :param config: The annotated config class to load into.
    :param path: The path to the config file. If not given, the
        ``CONFIGUR8_PATH`` environment variable is used.
    """
    if path is None:
        path = env.str("CONFIGUR8_PATH")

    with open(path, "rb") as fp:
        raw_config = fp.read().decode("utf-8")

    return parse(config, raw_config, format=format)
