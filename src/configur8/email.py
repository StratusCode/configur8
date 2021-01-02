from email_validator import validate_email, EmailNotValidError

from .core import InvalidConfig

__all__ = (
    "parse",
)


def parse(email: str) -> str:
    try:
        result = validate_email(email, check_deliverability=False)
    except EmailNotValidError as exc:
        raise InvalidConfig(str(exc)) from exc

    if not result.email:
        raise InvalidConfig("Email is not valid??")

    return result.email
