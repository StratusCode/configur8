import os

import pytest
from configur8 import env
from configur8 import InvalidConfig


def test_sanity(my_env):
    """
    Basic sanity check to see if env.int works as expected
    """
    assert env.int("INT") == 1234


def test_missing():
    """
    A missing env var should result in an error
    """
    assert "INT" not in os.environ

    with pytest.raises(env.MissingFromEnv):
        env.int("INT")


def test_default():
    """
    A default passed in MUST be returned when it doesn't exist
    """
    assert "INT" not in os.environ

    assert env.int("INT", "0") == 0


def test_default_not_missing(my_env):
    """
    Supply a default but ensure that the env var is used
    """
    assert os.environ["INT"] != "0"

    assert env.int("INT", "0") == 1234


def test_optional_missing():
    """
    optional() allows you to use a type safe api
    """
    assert "INT" not in os.environ

    assert env.int.optional("INT") is None


def test_optional_not_missing(my_env):
    """
    optional() allows you to use a type safe api
    """
    assert "INT" in os.environ

    assert env.int.optional("INT") == 1234


def test_list(my_env):
    """
    must return a list for the supplied env var
    """
    assert env.int.list("INT_LIST") == [1, 2, 3, 4]


def test_list_missing():
    """
    A missing env var must raise an error when expecting a list
    """
    assert "INT_LIST" not in os.environ

    with pytest.raises(env.MissingFromEnv):
        env.int.list("INT_LIST")


def test_list_separator(my_env):
    """
    Ensure that the list separator argument works as expected
    """
    os.environ["MY_VAR"] = "1|2|3"

    assert env.int.list("MY_VAR", separator="|") == [1, 2, 3]


def test_list_optional(my_env):
    """
    A missing env var must raise an error when expecting a list
    """
    assert "INT_LIST" in os.environ

    assert env.int.list_optional("INT_LIST") == [1, 2, 3, 4]


def test_list_optional_missing():
    """
    must return a list for the supplied env var
    """
    assert "INT_LIST" not in os.environ

    assert env.int.list_optional("INT_LIST") is None


def test_list_optional_separator(my_env):
    """
    Ensure that the list separator argument works as expected
    """
    os.environ["MY_VAR"] = "1|0|1"

    assert env.int.list_optional("MY_VAR", separator="|") == [1, 0, 1]


def test_bad_int(my_env):
    """
    Ensure that an invalid integer raises `InvalidConfig`
    """
    os.environ["MY_VAR"] = "abc"

    with pytest.raises(InvalidConfig):
        env.int("MY_VAR")
