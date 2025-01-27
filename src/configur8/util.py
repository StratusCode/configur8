import enum

__all__ = (
    "Missing",
    "MISSING",
)


# some stupid nonsense to get mypy to work with sentinels
class Missing(enum.Enum):
    token = 0


MISSING = Missing.token
