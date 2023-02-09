import inspect
import types
import typing as t

__all__ = (
    "is_union_type",
    "NoneType",
)


if hasattr(types, "NoneType"):
    # reintroduced into Python 3.10
    NoneType = types.NoneType
else:
    NoneType = type(None)


def is_union_type(type_: t.Any) -> bool:
    if hasattr(types, "UnionType") and isinstance(type_, types.UnionType):
        return True

    if hasattr(type_, "__origin__"):
        type_ = type_.__origin__

    if isinstance(type_, t._SpecialForm):
        return type_._name == "Union"  # type: ignore

    return False


def is_optional_type(type_: t.Any) -> bool:
    if hasattr(type_, "__origin__"):
        type_ = type_.__origin__

    if isinstance(type_, t._SpecialForm):
        return type_._name == "Optional"  # type: ignore

    return False


def is_list_type(type_: t.Any) -> bool:
    if hasattr(type_, "__origin__"):
        type_ = type_.__origin__

    if type_ is list:
        return True

    return False


def is_dict_type(type_: t.Any) -> bool:
    if hasattr(type_, "__origin__"):
        type_ = type_.__origin__

    if type_ is dict:
        return True

    return False


def get_annotation(config: t.Type) -> t.Tuple[
    t.Dict[str, t.Any],
    t.Dict[str, t.Any],
]:
    """
    Returns a tuple of (annotations, default_values) for the given config
    class, respecting the MRO.
    """
    annotations = {}
    default_values = {}

    for cls in inspect.getmro(config)[::-1]:
        if not hasattr(cls, "__annotations__"):
            continue

        for name, type_ in cls.__annotations__.items():
            annotations[name] = type_

            if hasattr(cls, name):
                default_values[name] = getattr(cls, name)

    return annotations, default_values


def to_dict(data: t.Any) -> t.Dict[str, t.Any]:
    if isinstance(data, dict):
        return data

    if hasattr(data, "__dict__"):
        return t.cast(t.Dict[str, t.Any], data.__dict__)

    raise TypeError(f"Expected dict or dataclass, got {type(data)}")
