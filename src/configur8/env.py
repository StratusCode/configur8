"""
Helper to pull configuration values from the environment.

Example:

```python
from configur8 import env

SECRET_KEY = env.str("SECRET_KEY")
NUM_WORKERS = env.int("NUM_WORKERS", 2)
DEBUG = env.bool("DEBUG", False)
```

In the example above:
1. ``SECRET_KEY`` is a required environment variable - attempting execute the
   code without it defined will result in an exception. This is typically what
   you want so that apps and services don't start in an unintended state.
2. ``NUM_WORKERS`` will be parsed into an integer. If the env var is not
   defined, ``2`` will be used as a default. If a non integer value is parsed,
   an error will be raised.
3. ``DEBUG`` is a boolean with a default of ``False``. "Truthy" values can be
   used, e.g. "on", "1", etc.

Everything is designed to be type safe.
"""

import builtins
import os
from typing import Callable, Generic, Optional, List, Union, TypeVar

from .util import MISSING, Empty
from .core import InvalidConfig
from .url import Url, parse as parse_url
from .path import Path, parse as parse_path

__all__ = (
    "MissingFromEnv",
    "str",
    "bool",
    "int",
    "float",
    "url",
    "path",
)

T = TypeVar("T")

BOOLEAN_TRUTHY_VALUES = ["true", "1", "y", "yes", "ok"]
LIST_SEPARATOR = ","


class MissingFromEnv(InvalidConfig):
    """
    Raised if an attempt to get an environment variable fails
    """


def get_raw(env_var_name: builtins.str) -> builtins.str:
    try:
        return os.environ[env_var_name]
    except KeyError:
        raise MissingFromEnv(f"Missing env var {env_var_name!r}")


def get_raw_optional(env_var: builtins.str) -> Optional[builtins.str]:
    return os.getenv(env_var, None)


class EnvVar(Generic[T]):
    def __init__(self, parse_func: Callable[[builtins.str], T]):
        self.parse_func = parse_func

    def default(
        self,
        env_var_name: builtins.str,
        default: Union[Empty, builtins.str] = MISSING,
    ) -> builtins.str:
        if default is MISSING:
            return get_raw(env_var_name)

        raw_value = get_raw_optional(env_var_name)

        if raw_value is None:
            raw_value = default

        return raw_value

    def __call__(
        self,
        env_var_name: builtins.str,
        default: Union[Empty, builtins.str] = MISSING,
        **kwargs,
    ) -> T:
        return self.parse_func(self.default(env_var_name, default))

    def optional(self, env_var_name: builtins.str) -> Optional[T]:
        raw_value = get_raw_optional(env_var_name)

        if raw_value is None:
            return None

        return self.parse_func(raw_value)

    def list(
        self,
        env_var_name: builtins.str,
        default: Union[Empty, builtins.str] = MISSING,
        separator=LIST_SEPARATOR,
    ) -> List[T]:
        raw_value = self.default(env_var_name, default)

        return [self.parse_func(item) for item in raw_value.split(separator)]

    def list_optional(
        self,
        env_var_name: builtins.str,
        separator=LIST_SEPARATOR,
    ) -> Optional[List[T]]:
        raw_value = get_raw_optional(env_var_name)

        if raw_value is None:
            return None

        return [self.parse_func(item) for item in raw_value.split(separator)]


def parse_str(raw_value: builtins.str) -> builtins.str:
    return raw_value


def parse_bool(raw_value: builtins.str) -> builtins.bool:
    return raw_value in BOOLEAN_TRUTHY_VALUES


def parse_int(raw_value: builtins.str) -> builtins.int:
    try:
        return builtins.int(raw_value)
    except ValueError:
        raise InvalidConfig(f"{raw_value!r} is not a valid integer")


def parse_float(raw_value: builtins.str) -> builtins.float:
    try:
        return builtins.float(raw_value)
    except ValueError:
        raise InvalidConfig(f"{raw_value!r} is not a valid number")


str = EnvVar[builtins.str](parse_str)
bool = EnvVar[builtins.bool](parse_bool)
int = EnvVar[builtins.int](parse_int)
float = EnvVar[builtins.float](parse_float)
url = EnvVar[Url](parse_url)
path = EnvVar[Path](parse_path)