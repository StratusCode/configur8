from email_validator import EmailNotValidError, validate_email

from .core import InvalidConfig

__all__ = ("parse",)


def parse(email: str) -> str:
    try:
        result = validate_email(email, check_deliverability=False)
    except EmailNotValidError as exc:
        raise InvalidConfig(str(exc)) from exc

    if hasattr(result, "normalized"):
        res = result.normalized
    else:
        res = result.email

    if not res:
        raise InvalidConfig(f"Email is not valid?? ({email!r})")

    assert isinstance(res, str)

    return res
