import os

import pytest
from configur8 import env, core


def test_sanity(my_env):
    """
    Basic sanity check to see if env.email works as expected
    """
    assert env.email("EMAIL") == my_env["EMAIL"]


def test_missing():
    """
    A missing env var should result in an error
    """
    assert "EMAIL" not in os.environ

    with pytest.raises(env.MissingFromEnv):
        env.email("EMAIL")


def test_default():
    """
    A default passed in MUST be returned when it doesn't exist
    """
    assert "EMAIL" not in os.environ

    assert env.email("EMAIL", "a@b.com") == "a@b.com"


def test_default_not_missing(my_env):
    """
    Supply a default but ensure that the env var is used
    """
    assert os.environ["EMAIL"] != "a@b.com"

    assert env.email("EMAIL", "a@b.com") == my_env["EMAIL"]


def test_optional_missing():
    """
    optional() allows you to use a type safe api
    """
    assert "EMAIL" not in os.environ

    assert env.email.optional("EMAIL") is None


def test_optional_not_missing(my_env):
    """
    optional() allows you to use a type safe api
    """
    assert "EMAIL" in os.environ

    assert env.email.optional("EMAIL") == my_env["EMAIL"]


def test_list(my_env):
    """
    must return a list for the supplied env var
    """
    assert env.email.list("EMAIL_LIST") == ["foo@bar.com", "me@example.com"]


def test_list_missing():
    """
    A missing env var must raise an error when expecting a list
    """
    assert "EMAIL_LIST" not in os.environ

    with pytest.raises(env.MissingFromEnv):
        env.email.list("EMAIL_LIST")


def test_list_separator(my_env):
    """
    Ensure that the list separator argument works as expected
    """
    os.environ["MY_VAR"] = "foo@bar.com|me@example.com"

    assert env.email.list("MY_VAR", separator="|") == [
        "foo@bar.com",
        "me@example.com",
    ]


def test_list_optional(my_env):
    """
    Optional should return the expected prefilled value
    """
    assert "EMAIL_LIST" in os.environ

    assert env.email.list_optional("EMAIL_LIST") == [
        "foo@bar.com",
        "me@example.com",
    ]


def test_list_optional_missing():
    """
    Must return a None if no value is available
    """
    assert "EMAIL_LIST" not in os.environ

    assert env.email.list_optional("EMAIL_LIST") is None


def test_list_optional_separator(my_env):
    """
    Ensure that the list separator argument works as expected
    """
    os.environ["MY_VAR"] = "foo@bar.com|me@example.com"

    assert env.email.list_optional("MY_VAR", separator="|") == [
        "foo@bar.com",
        "me@example.com",
    ]


def test_invalid_email(my_env):
    """
    An invalid email must raise an exception
    """
    os.environ["MY_VAR"] = "foo"

    with pytest.raises(core.InvalidConfig) as exc:
        env.email("MY_VAR")

    assert str(exc.value) == (
        "The email address is not valid. " "It must have exactly one @-sign."
    )
