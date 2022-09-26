import builtins
from dataclasses import dataclass
from typing import Optional
import yaml

from configur8 import cfg


@dataclass
class Config:
    str: str
    str_optional: Optional[builtins.str]


def parse(data: str) -> Config:
    config = cfg.YamlConfig(yaml.safe_load(data))
    return Config(
        str=config.str("str"),
        str_optional=config.str_optional("str_optional"),
    )


def test_optional_str():
    ret = parse("str: bar")

    assert ret.str_optional is None

    ret = parse("""
str: bar
str_optional: baz
""")

    assert ret.str_optional == "baz"

    ret = parse("""
str: bar
str_optional: null
""")

    assert ret.str_optional is None
