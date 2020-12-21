import enum

__all__ = (
    "Empty",
    "MISSING",
)


# some stupid nonsense to get mypy to work with sentinels
class Empty(enum.Enum):
    token = 0


MISSING = Empty.token
