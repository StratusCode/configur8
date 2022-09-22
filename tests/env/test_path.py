import os
import tempfile
from typing import List, overload

import pytest
from configur8 import env, path


def test_sanity(my_env):
    """
    Basic sanity check to see if env.path works as expected
    """
    assert env.path("CFG_PATH") == my_env["CFG_PATH"]


def test_missing():
    """
    A missing env var should result in an error
    """
    assert "CFG_PATH" not in os.environ

    with pytest.raises(env.MissingFromEnv):
        env.path("CFG_PATH")


def test_default():
    """
    A default passed in MUST be returned when it doesn't exist
    """
    assert "CFG_PATH" not in os.environ

    assert env.path("CFG_PATH", "bar") == "bar"


def test_default_not_missing(my_env):
    """
    Supply a default but ensure that the env var is used
    """
    assert os.environ["CFG_PATH"] != "/foo/bar"

    assert env.path("CFG_PATH", "/foo/bar") == my_env["CFG_PATH"]


def test_optional_missing():
    """
    optional() allows you to use a type safe api
    """
    assert "CFG_PATH" not in os.environ

    assert env.path.optional("CFG_PATH") is None


def test_optional_not_missing(my_env):
    """
    optional() allows you to use a type safe api
    """
    assert "CFG_PATH" in os.environ

    assert env.path.optional("CFG_PATH") == my_env["CFG_PATH"]


def test_list(my_env):
    """
    must return a list for the supplied env var
    """
    assert env.path.list("CFG_PATH_LIST") == to_path([
        "/usr/bin",
        "/usr/local/bin",
    ])


def test_list_missing():
    """
    A missing env var must raise an error when expecting a list
    """
    assert "CFG_PATH_LIST" not in os.environ

    with pytest.raises(env.MissingFromEnv):
        env.path.list("CFG_PATH_LIST")


def test_list_separator(my_env):
    """
    Ensure that the list separator argument works as expected
    """
    os.environ["MY_VAR"] = "foo:bar"

    assert env.path.list("MY_VAR", separator=":") == to_path(["foo", "bar"])


def test_list_optional(my_env):
    """
    A missing env var must raise an error when expecting a list
    """
    assert "CFG_PATH_LIST" in os.environ

    assert env.path.list_optional("CFG_PATH_LIST") == to_path([
        "/usr/bin",
        "/usr/local/bin",
    ])


def test_list_optional_missing():
    """
    must return a list for the supplied env var
    """
    assert "CFG_PATH_LIST" not in os.environ

    assert env.path.list_optional("CFG_PATH_LIST") is None


def test_list_optional_separator(my_env):
    """
    Ensure that the list separator argument works as expected
    """
    os.environ["MY_VAR"] = "foo:bar"

    assert env.path.list_optional("MY_VAR", separator=":") == to_path([
        "foo",
        "bar",
    ])


def test_read(my_env):
    assert "MY_VAR" not in os.environ

    with tempfile.NamedTemporaryFile() as fp:
        fp.write(b"hello world")
        fp.flush()

        os.environ["MY_VAR"] = fp.name

        x = env.path("MY_VAR")

        assert x.read() == "hello world"


def test_readlines(my_env):
    assert "MY_VAR" not in os.environ

    with tempfile.NamedTemporaryFile() as fp:
        fp.write(b"hello\nworld")
        fp.flush()

        os.environ["MY_VAR"] = fp.name

        x = env.path("MY_VAR")

        assert x.readlines() == ["hello\n", "world"]


@overload
def to_path(value: List[str]) -> List[path.Path]:
    ...


@overload
def to_path(value: str) -> path.Path:
    ...


def to_path(value):
    if isinstance(value, str):
        return path.parse(value)

    if isinstance(value, list):
        return [path.parse(v) for v in value]

    raise TypeError(f"Cannot convert {value} to path")
