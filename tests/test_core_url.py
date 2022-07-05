from configur8.url import parse
from configur8.url import Url


def test_sanity():
    result = parse("https://admin:password@localhost:9090/foo?hello=world#bar")

    assert isinstance(result, Url)

    assert (
        result == "https://admin:password@localhost:9090/foo?hello=world#bar"
    )  # noqa: E501
    assert (
        "https://admin:password@localhost:9090/foo?hello=world#bar" == result
    )  # noqa: E501
    assert result.protocol == "https"
    assert result.username == "admin"
    assert result.password == "password"
    assert result.host == "localhost"
    assert result.port == 9090
    assert result.path == "/foo"
    assert result.query == {
        "hello": ["world"],
    }
    assert result.fragment == "bar"


def test_empty_protocol():
    result = parse("localhost")

    assert isinstance(result, Url)

    assert result == "localhost"
    assert result.protocol is None
    assert result.username is None
    assert result.password is None
    assert result.host == "localhost"
    assert result.port is None
    assert result.path is None
    assert result.query is None
    assert result.fragment is None


def test_with_path():
    result = parse("localhost/foo/bar")

    assert isinstance(result, Url)

    assert result == "localhost/foo/bar"
    assert result.protocol is None
    assert result.username is None
    assert result.password is None
    assert result.host == "localhost"
    assert result.port is None
    assert result.path == "/foo/bar"
    assert result.query is None
    assert result.fragment is None
