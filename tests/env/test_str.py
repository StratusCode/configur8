import os

import pytest
from configur8 import env


def test_sanity(my_env):
    """
    Basic sanity check to see if env.str works as expected
    """
    assert env.str("STR") == "foo bar"


def test_missing():
    """
    A missing env var should result in an error
    """
    assert "STR" not in os.environ

    with pytest.raises(env.MissingFromEnv):
        env.str("STR")


def test_default():
    """
    A default passed in MUST be returned when it doesn't exist
    """
    assert "STR" not in os.environ

    assert env.str("STR", "mystr") == "mystr"


def test_default_not_missing(my_env):
    """
    Supply a default but ensure that the env var is used
    """
    assert os.environ["STR"] != "mystr"

    assert env.str("STR", "mystr") == "foo bar"


def test_optional_missing():
    """
    optional() allows you to use a type safe api
    """
    assert "STR" not in os.environ

    assert env.str.optional("STR") is None


def test_optional_not_missing(my_env):
    """
    optional() allows you to use a type safe api
    """
    assert "STR" in os.environ

    assert env.str.optional("STR") == "foo bar"


def test_list(my_env):
    """
    must return a list for the supplied env var
    """
    assert env.str.list("STR_LIST") == ["foo", "bar"]


def test_list_missing():
    """
    A missing env var must raise an error when expecting a list
    """
    assert "STR_LIST" not in os.environ

    with pytest.raises(env.MissingFromEnv):
        env.str.list("STR_LIST")


def test_list_separator(my_env):
    """
    Ensure that the list separator argument works as expected
    """
    os.environ["MY_VAR"] = "one|two|three"

    assert env.str.list("MY_VAR", separator="|") == ["one", "two", "three"]


def test_list_optional(my_env):
    """
    A missing env var must raise an error when expecting a list
    """
    assert "STR_LIST" in os.environ

    assert env.str.list_optional("STR_LIST") == ["foo", "bar"]


def test_list_optional_missing():
    """
    must return a list for the supplied env var
    """
    assert "STR_LIST" not in os.environ

    assert env.str.list_optional("STR_LIST") is None


def test_list_optional_separator(my_env):
    os.environ["MY_VAR"] = "one|two|three"

    assert env.str.list_optional("MY_VAR", separator="|") == [
        "one",
        "two",
        "three",
    ]
