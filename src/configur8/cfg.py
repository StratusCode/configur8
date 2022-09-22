"""
Type-safe (ish) YAML configuration and validation.

An example ``config.py`` file:

```python
from typing import Optional

import yaml

from configur8 import cfg, env


class MySQLConfig:
    host: str
    port: int
    username: Optional[str]
    password: Optional[str]
    database: str

    def __init__(
        self,
        # shame that nested inference is not a thing in MyPy yet
        host: str,
        port: int,
        username: Optional[str],
        password: Optional[str],
        database: str,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database


class Config:
    mysql: MySQLConfig

    def __init__(self, mysql: MySQLConfig) -> None:
        self.mysql = mysql


def get_mysql(data: cfg.YamlConfig) -> MySQLConfig:
    return MySQLConfig(
        host=data.str("host"),
        port=data.int("port"),
        username=data.str_optional("username"),
        password=data.str_optional("password"),
        database=data.str("database"),
    )


def parse(data: str) -> Config:
    config = yaml.safe_load(data)

    if not isinstance(config, dict):
        raise cfg.ConfigError("", "Expected root from yaml to be a dict")

    config = cfg.YamlConfig(config)

    return Config(
        mysql=get_mysql(config.with_prefix("mysql")),
    )


def load(path: Optional[str] = None) -> Config:
    if path is None:
        # Load from environment
        path = env.str("CONFIG_PATH")

    with open(path, "rb") as fp:
        return parse(fp.read().decode("utf-8"))
```
"""

import builtins
import re
from typing import Any, Dict, List, Optional, Sequence, Type, TypeVar, Union


class Missing:
    pass


MISSING = Missing()
Data = TypeVar("Data")
PathLike = Sequence[Union[str, int]]


class Path:
    data: List[Union[str, int]]

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
                    f"Unexpected {type(part)} at {count} in {self.path!r}"
                )

            first = False

        return ret

    def __iter__(self):
        return iter(self.data)

    @staticmethod
    def decode(path: str) -> "Path":
        ret: List[Union[str, int]] = []

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

    def __add__(self, other: Any) -> "Path":
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
        path: Union[PathLike, Path, str],
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


class YamlConfig:
    root: Dict[str, Any]
    prefix: Optional[Path]

    def __init__(
        self,
        root: Dict[str, Any],
        prefix: Optional[Union[str, Path]] = None,
    ) -> None:
        self.root = root

        if prefix is None:
            self.prefix = prefix
        else:
            if isinstance(prefix, str):
                self.prefix = Path.decode(prefix)
            else:
                self.prefix = prefix

    def path(
        self,
        path: str,
        default: Union[Missing, Any] = MISSING,
    ) -> Any:
        obj = self.root

        if self.prefix is not None:
            path = str(self.prefix) + "." + path

        for part in Path.decode(path):
            try:
                obj = obj[part]
            except KeyError as err:
                if default is not MISSING:
                    return default

                raise ConfigError(path.split("."), "missing") from err
            except TypeError as err:
                # report this please
                print(Path.decode(path).data)
                print(path, type(part), obj)

                raise ConfigError(path.split("."), "invalid") from err

        return obj

    def get(
        self,
        type_: Type[Data],
        path: str,
        default: Union[Missing, Data] = MISSING,
    ) -> Data:
        value = self.path(path, default)

        if value is default:
            if not isinstance(value, type_):
                raise TypeError(
                    "Expected {type_} at {path!r}, got {value!r} instead"
                )

            return value

        if not isinstance(value, type_):
            raise ConfigError(
                self.with_path(path),
                f"{type_} expected but found {type(value)}"
            )

        return value

    def optional(self, type_: Type[Data], path: str) -> Optional[Data]:
        return self.get(type_, path, default=None)

    def with_path(self, path: str) -> str:
        if self.prefix is None:
            return path

        return str(self.prefix + path)

    def with_prefix(self, prefix: str) -> "YamlConfig":
        if self.prefix is None:
            return YamlConfig(self.root, prefix)

        return YamlConfig(self.root, f"{self.prefix}.{prefix}")

    def str(
        self,
        path: str,
        default: Union[Missing, str] = MISSING,
    ) -> str:
        return self.get(str, path, default)

    def str_optional(self, path: builtins.str) -> Optional[builtins.str]:
        return self.optional(str, path)

    def int(
        self,
        path: builtins.str,
        default: Union[Missing, int] = MISSING,
    ) -> int:
        return self.get(int, path, default)

    def int_optional(self, path: builtins.str) -> Optional[builtins.int]:
        return self.optional(int, path)

    def list(
        self,
        path: builtins.str,
        default: Union[Missing, list] = MISSING,
    ) -> List[Any]:
        return self.get(list, path, default)

    def list_optional(self, path: builtins.str) -> Optional[List[Any]]:
        return self.optional(list, path)

    def dict(
        self,
        path: builtins.str,
        default: Union[Missing, builtins.dict] = MISSING,
    ) -> Dict[builtins.str, Any]:
        return self.get(dict, path, default)

    def dict_optional(
        self,
        path: builtins.str
    ) -> Optional[Dict[builtins.str, Any]]:
        return self.optional(dict, path)
