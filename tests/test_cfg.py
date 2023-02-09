import typing as t

import pytest

from configur8 import cfg


class BaseMySQL:
    username: str
    password: str
    database: str


class MySQLHost(BaseMySQL):
    host: str
    port: int = 3306


class MySQLSocket(BaseMySQL):
    socket: str


MySQL = t.Union[MySQLHost, MySQLSocket]


class Config:
    mysql: MySQL


def parse(data: str) -> Config:
    return cfg.parse(Config, data)


def test_optional_str():
    class TestConfig:
        str: t.Optional[str]

    ret = cfg.parse(TestConfig, "str: null")

    assert ret.str is None

    ret = cfg.parse(TestConfig, """
str: bar
""")

    assert ret.str == "bar"


def test_union_str():
    class TestConfig:
        str: t.Union[str, None]

    ret = cfg.parse(TestConfig, "str: null")

    assert ret.str is None

    ret = cfg.parse(TestConfig, """
str: bar
""")

    assert ret.str == "bar"


def test_not_a_str():
    class TestConfig:
        str: str

    with pytest.raises(cfg.ConfigError) as err:
        cfg.parse(TestConfig, "str: null")

    assert str(err.value) == "str: Expected str, got None"


def test_int():
    class TestConfig:
        int: int

    ret = cfg.parse(TestConfig, "int: 42")

    assert ret.int == 42


def test_not_an_int():
    class TestConfig:
        int: int

    with pytest.raises(cfg.ConfigError) as err:
        cfg.parse(TestConfig, "int: foo")

    assert str(err.value) == "int: Expected int, got 'foo'"


def test_float():
    class TestConfig:
        float: float

    ret = cfg.parse(TestConfig, "float: 42.0")

    assert ret.float == 42.0


def test_not_a_float():
    class TestConfig:
        float: float

    with pytest.raises(cfg.ConfigError) as err:
        cfg.parse(TestConfig, "float: foo")

    assert str(err.value) == "float: Expected float, got 'foo'"


def test_bool():
    class TestConfig:
        bool: bool

    ret = cfg.parse(TestConfig, "bool: true")

    assert ret.bool is True

    ret = cfg.parse(TestConfig, "bool: false")

    assert ret.bool is False


def test_not_a_bool():
    class TestConfig:
        bool: bool

    with pytest.raises(cfg.ConfigError) as err:
        cfg.parse(TestConfig, "bool: foo")

    assert str(err.value) == "bool: Expected bool, got 'foo'"


def test_none():
    class TestConfig:
        none: None

    ret = cfg.parse(TestConfig, "none: null")

    assert ret.none is None


def test_not_none():
    class TestConfig:
        none: None

    with pytest.raises(cfg.ConfigError) as err:
        cfg.parse(TestConfig, "none: foo")

    assert str(err.value) == "none: Expected None, got 'foo'"


def test_unexpected_none():
    class StrConfig:
        str: str

    with pytest.raises(cfg.ConfigError) as err:
        cfg.parse(StrConfig, "str: null")

    assert str(err.value) == "str: Expected str, got None"

    class IntConfig:
        int: int

    with pytest.raises(cfg.ConfigError) as err:
        cfg.parse(IntConfig, "int: null")

    assert str(err.value) == "int: Expected int, got None"

    class FloatConfig:
        float: float

    with pytest.raises(cfg.ConfigError) as err:
        cfg.parse(FloatConfig, "float: null")

    assert str(err.value) == "float: Expected float, got None"

    class BoolConfig:
        bool: bool

    with pytest.raises(cfg.ConfigError) as err:
        cfg.parse(BoolConfig, "bool: null")

    assert str(err.value) == "bool: Expected bool, got None"


def test_list():
    class TestConfig:
        list: t.List[str]

    ret = cfg.parse(TestConfig, """
list:

    - foo
    - bar
""")

    assert ret.list == ["foo", "bar"]


def test_not_a_list():
    class TestConfig:
        list: t.List[str]

    with pytest.raises(cfg.ConfigError) as err:
        cfg.parse(TestConfig, "list: foo")

    assert str(err.value) == "list: Expected list, got 'foo'"


def test_dict():
    class TestConfig:
        dict: t.Dict[str, str]

    ret = cfg.parse(TestConfig, """
dict:
    foo: bar
    baz: qux
""")

    assert ret.dict == {"foo": "bar", "baz": "qux"}


def test_not_a_dict():
    class TestConfig:
        dict: t.Dict[str, str]

    with pytest.raises(cfg.ConfigError) as err:
        cfg.parse(TestConfig, "dict: foo")

    assert str(err.value) == "dict: Expected dict, got 'foo'"


def test_mysql_host():
    cfg = parse("""
mysql:
    host: localhost
    username: root
    password: password
    database: test
""")

    assert isinstance(cfg.mysql, MySQLHost)
    assert cfg.mysql.host == "localhost"
    assert cfg.mysql.port == 3306
    assert cfg.mysql.username == "root"
    assert cfg.mysql.password == "password"
    assert cfg.mysql.database == "test"


def test_mysql_socket():
    cfg = parse("""
mysql:
    socket: /foo/bar
    username: root
    password: password
    database: test
""")

    assert isinstance(cfg.mysql, MySQLSocket)
    assert cfg.mysql.socket == "/foo/bar"
    assert cfg.mysql.username == "root"
    assert cfg.mysql.password == "password"
    assert cfg.mysql.database == "test"
