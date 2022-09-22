from email_validator import EmailNotValidError, validate_email

from .core import InvalidConfig

__all__ = ("parse",)


def parse(email: str) -> str:
    try:
        result = validate_email(email, check_deliverability=False)
    except EmailNotValidError as exc:
        raise InvalidConfig(str(exc)) from exc

    if not result.email:
        raise InvalidConfig(f"Email is not valid?? ({email!r})")

    assert isinstance(result.email, str)

    return result.email
