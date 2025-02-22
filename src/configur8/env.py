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
import typing as t

from .core import InvalidConfig
from .email import parse as parse_email
from .path import parse as parse_path
from .path import Path
from .url import parse as parse_url
from .url import Url
from .util import Missing
from .util import MISSING

__all__ = (
    "MissingFromEnv",
    "bool",
    "email",
    "float",
    "int",
    "path",
    "str",
    "url",
)

T = t.TypeVar("T")

#: List of environment variable values that will be converted into Python `True`
BOOLEAN_TRUTHY_VALUES = ["true", "1", "y", "yes", "ok"]
#: Default separator for list encoded values.
LIST_SEPARATOR = ","

ParseFunc = t.Callable[[builtins.str | T], T]


class MissingFromEnv(InvalidConfig):
    """
    Raised if an attempt to get an environment variable fails
    """


def get_raw(env_var_name: builtins.str) -> builtins.str:
    """
    Returns the value of the environment variable, or raises an error.
    """
    ret = os.getenv(env_var_name, None)

    if ret is not None:
        return ret

    raise MissingFromEnv(f"Missing env var {env_var_name!r}")


def get_raw_optional(env_var: builtins.str) -> builtins.str | None:
    """
    Returns the value of the environment variable, or `None` if it doesn't
    exist.
    """
    return os.getenv(env_var, None)


class EnvVar(t.Generic[T]):
    parse_func: ParseFunc[T]

    def __init__(self, parse_func: ParseFunc[T]):
        self.parse_func = parse_func

    @t.overload
    def default(
        self,
        env_var_name: builtins.str,
    ) -> T: ...

    @t.overload
    def default(
        self,
        env_var_name: builtins.str,
        default: Missing,
    ) -> T: ...

    @t.overload
    def default(
        self,
        env_var_name: builtins.str,
        default: T,
    ) -> T: ...

    @t.overload
    def default(
        self,
        env_var_name: builtins.str,
        default: builtins.str,
    ) -> T: ...

    def default(
        self,
        env_var_name: builtins.str,
        default: Missing | builtins.str | T = MISSING,
    ) -> builtins.str | T | t.List[T]:
        if default is MISSING:
            return get_raw(env_var_name)

        if t.TYPE_CHECKING:
            assert not isinstance(default, Missing)

        raw_value = get_raw_optional(env_var_name)

        if raw_value is None:
            return default

        return raw_value

    def __call__(
        self,
        env_var_name: builtins.str,
        default: Missing | builtins.str | T = MISSING,
    ) -> T:
        raw_value = self.default(env_var_name, default)

        if t.TYPE_CHECKING:
            assert not isinstance(raw_value, Missing)
            assert not isinstance(raw_value, list)

        return self.parse_func(raw_value)

    def optional(self, env_var_name: builtins.str) -> t.Optional[T]:
        raw_value = get_raw_optional(env_var_name)

        if raw_value is None:
            return None

        return self.parse_func(raw_value)

    def list(
        self,
        env_var_name: builtins.str,
        default: Missing | t.List[T] = MISSING,
        separator: builtins.str = LIST_SEPARATOR,
    ) -> t.List[T]:
        raw_value = self.default(env_var_name, t.cast(T, default))

        if isinstance(raw_value, list):
            return raw_value

        if t.TYPE_CHECKING:
            assert not isinstance(raw_value, Missing)
            assert isinstance(raw_value, builtins.str)

        return [self.parse_func(item) for item in raw_value.split(separator)]

    def list_optional(
        self,
        env_var_name: builtins.str,
        separator=LIST_SEPARATOR,
    ) -> t.List[T] | None:
        raw_value = get_raw_optional(env_var_name)

        if raw_value is None:
            return None

        return [self.parse_func(item) for item in raw_value.split(separator)]


def parse_str(raw_value: builtins.str) -> builtins.str:
    """
    Parse an environment variable value as a string.
    """
    return raw_value


def parse_bool(raw_value: builtins.str | builtins.bool) -> builtins.bool:
    """
    Parse an environment variable value as a boolean.
    """
    if isinstance(raw_value, builtins.bool):
        return raw_value

    return raw_value.lower() in BOOLEAN_TRUTHY_VALUES


def parse_int(raw_value: builtins.str | builtins.int) -> builtins.int:
    """
    Parse an environment variable value as an integer.
    """
    if isinstance(raw_value, builtins.int):
        return raw_value

    try:
        return builtins.int(raw_value)
    except ValueError:
        raise InvalidConfig(f"{raw_value!r} is not a valid integer")


def parse_float(raw_value: builtins.str | builtins.float) -> builtins.float:
    """
    Parse an environment variable value as a float.
    """
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
email = EnvVar[builtins.str](parse_email)
