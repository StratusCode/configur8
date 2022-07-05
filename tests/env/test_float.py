import os

import pytest
from configur8 import env
from configur8 import InvalidConfig


def test_sanity(my_env):
    """
    Basic sanity check to see if env.float works as expected
    """
    assert env.float("FLOAT") == 1.234


def test_missing():
    """
    A missing env var should result in an error
    """
    assert "FLOAT" not in os.environ

    with pytest.raises(env.MissingFromEnv):
        env.float("FLOAT")


def test_default():
    """
    A default passed in MUST be returned when it doesn't exist
    """
    assert "FLOAT" not in os.environ

    assert env.float("FLOAT", "0") == 0.0


def test_default_not_missing(my_env):
    """
    Supply a default but ensure that the env var is used
    """
    assert os.environ["FLOAT"] != "0"

    assert env.float("FLOAT", "0") == 1.234


def test_optional_missing():
    """
    optional() allows you to use a type safe api
    """
    assert "FLOAT" not in os.environ

    assert env.float.optional("FLOAT") is None


def test_optional_not_missing(my_env):
    """
    optional() allows you to use a type safe api
    """
    assert "FLOAT" in os.environ

    assert env.float.optional("FLOAT") == 1.234


def test_list(my_env):
    """
    must return a list for the supplied env var
    """
    assert env.float.list("FLOAT_LIST") == [1.0, 1.1, 1.2]


def test_list_missing():
    """
    A missing env var must raise an error when expecting a list
    """
    assert "FLOAT_LIST" not in os.environ

    with pytest.raises(env.MissingFromEnv):
        env.float.list("FLOAT_LIST")


def test_list_separator(my_env):
    """
    Ensure that the list separator argument works as expected
    """
    os.environ["MY_VAR"] = "1|2|3"

    assert env.float.list("MY_VAR", separator="|") == [1.0, 2.0, 3.0]


def test_list_optional(my_env):
    """
    A missing env var must raise an error when expecting a list
    """
    assert "FLOAT_LIST" in os.environ

    assert env.float.list_optional("FLOAT_LIST") == [1.0, 1.1, 1.2]


def test_list_optional_missing():
    """
    must return a list for the supplied env var
    """
    assert "FLOAT_LIST" not in os.environ

    assert env.float.list_optional("FLOAT_LIST") is None


def test_list_optional_separator(my_env):
    """
    Ensure that the list separator argument works as expected
    """
    os.environ["MY_VAR"] = "1|0|1"

    assert env.float.list_optional("MY_VAR", separator="|") == [1.0, 0.0, 1.0]


def test_bad_float(my_env):
    """
    Ensure that an invalid integer raises `InvalidConfig`
    """
    os.environ["MY_VAR"] = "abc"

    with pytest.raises(InvalidConfig):
        env.float("MY_VAR")
