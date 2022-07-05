import os

from pytest import fixture

__all__ = ("my_env",)


@fixture
def my_env():
    current = os.environ.copy()

    data = {
        "STR": "foo bar",
        "STR_LIST": "foo,bar",
        "BOOL": "1",
        "BOOL_LIST": "1,yes,true,ok",
        "INT": "1234",
        "INT_LIST": "1,2,3,4",
        "FLOAT": "1.234",
        "FLOAT_LIST": "1.0,1.1,1.2",
        "URL": "https://admin:password@localhost:9090/foo#bar",
        "URL_LIST": "http://foo,http://bar",
        "CFG_PATH": "/var/run/secrets/foo/baz.key",
        "CFG_PATH_LIST": "/usr/bin,/usr/local/bin",
        "EMAIL": "foo@bar.com",
        "EMAIL_LIST": "foo@bar.com,me@example.com",
    }

    os.environ.update(data)

    yield data

    os.environ = current  # type: ignore
