import os
from typing import List, overload

import pytest
from configur8 import env, url


def test_sanity(my_env):
    """
    Basic sanity check to see if env.url works as expected
    """
    assert env.url("URL") == my_env["URL"]


def test_missing():
    """
    A missing env var should result in an error
    """
    assert "URL" not in os.environ

    with pytest.raises(env.MissingFromEnv):
        env.url("URL")


def test_default():
    """
    A default passed in MUST be returned when it doesn't exist
    """
    assert "URL" not in os.environ

    assert env.url("URL", "http://localhost") == "http://localhost"


def test_default_not_missing(my_env):
    """
    Supply a default but ensure that the env var is used
    """
    assert os.environ["URL"] != "http://foo-bar"

    assert env.url("URL", "http://foo-bar") == my_env["URL"]


def test_optional_missing():
    """
    optional() allows you to use a type safe api
    """
    assert "URL" not in os.environ

    assert env.url.optional("URL") is None


def test_optional_not_missing(my_env):
    """
    optional() allows you to use a type safe api
    """
    assert "URL" in os.environ

    assert env.url.optional("URL") == my_env["URL"]


def test_list(my_env):
    """
    must return a list for the supplied env var
    """
    assert env.url.list("URL_LIST") == to_url(["http://foo", "http://bar"])


def test_list_missing():
    """
    A missing env var must raise an error when expecting a list
    """
    assert "URL_LIST" not in os.environ

    with pytest.raises(env.MissingFromEnv):
        env.url.list("URL_LIST")


def test_list_separator(my_env):
    """
    Ensure that the list separator argument works as expected
    """
    os.environ["MY_VAR"] = "http://foo|http://bar"

    assert env.url.list("MY_VAR", separator="|") == to_url([
        "http://foo",
        "http://bar",
    ])


def test_list_optional(my_env):
    """
    A missing env var must raise an error when expecting a list
    """
    assert "URL_LIST" in os.environ

    assert env.url.list_optional("URL_LIST") == to_url([
        "http://foo",
        "http://bar",
    ])


def test_list_optional_missing():
    """
    must return a list for the supplied env var
    """
    assert "URL_LIST" not in os.environ

    assert env.url.list_optional("URL_LIST") is None


def test_list_optional_separator(my_env):
    """
    Ensure that the list separator argument works as expected
    """
    os.environ["MY_VAR"] = "http://foo|http://bar"

    assert env.url.list_optional("MY_VAR", separator="|") == to_url([
        "http://foo",
        "http://bar",
    ])


def test_str_protocol(my_env):
    os.environ["MY_VAR"] = "http://localhost"

    value = env.url("MY_VAR")

    assert hasattr(value, "rstrip")
    assert hasattr(value, "lstrip")
    assert hasattr(value, "replace")
    assert hasattr(value, "upper")
    assert hasattr(value, "lower")


@overload
def to_url(value: List[str]) -> List[url.Url]:
    ...


@overload
def to_url(value: str) -> url.Url:
    ...


def to_url(value):
    if isinstance(value, str):
        return url.parse(value)

    if isinstance(value, list):
        return [url.parse(v) for v in value]

    raise TypeError(f"Cannot convert {value} to url")
