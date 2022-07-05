import os

import pytest
from configur8 import env


def test_sanity(my_env):
    """
    Basic sanity check to see if env.bool works as expected
    """
    assert env.bool("BOOL") is True


def test_missing():
    """
    A missing env var should result in an error
    """
    assert "BOOL" not in os.environ

    with pytest.raises(env.MissingFromEnv):
        env.bool("BOOL")


def test_default():
    """
    A default passed in MUST be returned when it doesn't exist
    """
    assert "BOOL" not in os.environ

    assert env.bool("BOOL", "0") is False


def test_default_not_missing(my_env):
    """
    Supply a default but ensure that the env var is used
    """
    assert os.environ["BOOL"] != "0"

    assert env.bool("BOOL", "0") is True


def test_optional_missing():
    """
    optional() allows you to use a type safe api
    """
    assert "BOOL" not in os.environ

    assert env.bool.optional("BOOL") is None


def test_optional_not_missing(my_env):
    """
    optional() allows you to use a type safe api
    """
    assert "BOOL" in os.environ

    assert env.bool.optional("BOOL") is True


def test_list(my_env):
    """
    must return a list for the supplied env var
    """
    assert env.bool.list("BOOL_LIST") == [True] * 4


def test_list_missing():
    """
    A missing env var must raise an error when expecting a list
    """
    assert "BOOL_LIST" not in os.environ

    with pytest.raises(env.MissingFromEnv):
        env.bool.list("BOOL_LIST")


def test_list_separator(my_env):
    """
    Ensure that the list separator argument works as expected
    """
    os.environ["MY_VAR"] = "false|0|nope"

    assert env.bool.list("MY_VAR", separator="|") == [False] * 3


def test_list_optional(my_env):
    """
    A missing env var must raise an error when expecting a list
    """
    assert "BOOL_LIST" in os.environ

    assert env.bool.list_optional("BOOL_LIST") == [True] * 4


def test_list_optional_missing():
    """
    must return a list for the supplied env var
    """
    assert "BOOL_LIST" not in os.environ

    assert env.bool.list_optional("BOOL_LIST") is None


def test_list_optional_separator(my_env):
    """
    Ensure that the list separator argument works as expected
    """
    os.environ["MY_VAR"] = "1|0|1"

    assert env.bool.list_optional("MY_VAR", separator="|") == [
        True,
        False,
        True,
    ]
