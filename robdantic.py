"""
Robdantic
---------

Robtop String Serialization/Deserialization library in python.
It also makes everything very easy to repair when the boomlings 
api screws around.

"""

from __future__ import annotations as _annotations
from pydantic._internal._generics import PydanticGenericMetadata
from pydantic.fields import FieldInfo as PydanticFieldInfo
from pydantic.config import JsonDict
from pydantic_core import PydanticUndefined as Undefined
from pydantic import AliasChoices, AliasPath
from pydantic import BaseModel

from pydantic._internal._model_construction import (  # type: ignore[no-redef]
    ModelMetaclass as ModelMetaclass,
)

from typing import Callable, Tuple, TypeVar, Any, Union, overload, Optional
import typing
from pydantic import types
from enum import Enum

from warnings import warn

_T = TypeVar("_T")

__author__ = "CallocGD"
__version__ = "0.1.0"

def __dataclass_transform__(
    *,
    eq_default: bool = True,
    order_default: bool = False,
    kw_only_default: bool = False,
    field_descriptors: Tuple[Union[type, Callable[..., Any]], ...] = (()),
) -> Callable[[_T], _T]:
    return lambda a: a


class FieldInfo(PydanticFieldInfo):
    """Helps with Applying specific robtop keys and values when serilizing and deserilizing"""

    if typing.TYPE_CHECKING:
        key: int
        """The Key to a specific Robtop field"""

    def __init__(self, **kwargs) -> None:
        self.key = kwargs.get("key")
        self._raw_key = ("%i" % self.key).encode()
        super().__init__(**kwargs)

    @property
    def raw_key(self) -> bytes:
        """assists in the deserilization of Robtop strings"""
        return self._raw_key


@overload
def Field(
    key: int,
    annotation: type[Any] | None = Undefined,
    default: Any = Undefined,
    default_factory: Union[Callable[[], Any], None] = None,
    alias: Optional[str] = None,
    alias_priority: Optional[int] = None,
    validation_alias: Optional[Union[str, AliasPath, AliasChoices]] = None,
    serialization_alias: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    examples: Optional[list[Any]] = None,
    exclude: Optional[bool] = None,
    discriminator: Optional[Union[str, types.Discriminator]] = None,
    json_schema_extra: Optional[
        Union[JsonDict, typing.Callable[[JsonDict], None]]
    ] = None,
    frozen: Optional[bool] = None,
    validate_default: Optional[bool] = None,
    repr: bool = Undefined,
    init: Optional[bool] = None,
    init_var: Optional[bool] = None,
    kw_only: Optional[bool] = None,
    metadata: list[Any] = [],
) -> Any: ...


def Field(*args, **kw) -> Any:
    return FieldInfo(*args, **kw)


field = Field


class MissingKeyWarning(RuntimeWarning):
    """Robtop Implemented a New key into a Specific Struture type..."""


def load_key_fields(model: "RobtopModel") -> dict[bytes, Tuple[str, FieldInfo]]:
    return {v.raw_key: (k, v) for k, v in model.model_fields.items()}


@__dataclass_transform__(
    kw_only_default=True, field_descriptors=(Field, FieldInfo, field)
)
class RobtopModel(BaseModel):
    """A serializable Response Model for any Geometry dash Object"""

    if typing.TYPE_CHECKING:
        # NOTE: Overrides Original FieldInfo for ours...
        model_fields: dict[str, FieldInfo]

        __key_fields__: dict[bytes, Tuple[str, FieldInfo]]
        """Robtop String Numbers in Bytes in order to assist with deserilization of any given field"""

    def __init_subclass__(cls, **kwargs):
        # NOTE: This setup is meant for bypassing a bigger problem with pydantic's broken fucked up system...
        cls.default_splitter = kwargs.pop("splitter", None)
        return super().__init_subclass__(**kwargs)
    

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        cls.__key_fields__ = load_key_fields(cls)
        return cls.__init_subclass__(**kwargs)
 
    @classmethod
    def from_robtop(cls, data: bytes, splitter: Optional[bytes] = None):
        fields_dict = cls.__key_fields__
        resp = data.split(splitter or cls.default_splitter)
        model_dict = {}
        while resp:
            key = resp.pop(0)
            try:
                name, field = fields_dict[key]
            except KeyError:
                warn(
                    f'Undefined/Unknown Feild Key With ID: {key.decode()} for Model "{cls.__name__}", Value: {resp.pop(0)}',
                    category=MissingKeyWarning,
                    # NOTE: It's a pretty important one so I'm leaving it at 3... - Calloc
                    stacklevel=3,
                    source=f"{cls.__name__}.from_robtop",
                )
                continue

            item = resp.pop(0)

            annoation = field.annotation

            if issubclass(annoation, bytes):
                model_dict[name] = item

            elif issubclass(annoation, str):
                model_dict[name] = item.decode("utf-8", errors="surrogateescape")

            elif issubclass(annoation, int):
                model_dict[name] = int(item, base=10)

            elif issubclass(annoation, Enum):
                model_dict[name] = type(annoation)(int(item, base=10))

            elif issubclass(annoation, bool):
                model_dict[name] = False if item == b"0" else True

            else:
                raise ValueError(
                    f'{annoation.__name__} has not been properly implemented for field "{name}"'
                )
        return cls(**model_dict)

    def to_robtop(self, joiner: Optional[bytes] = None):
        joiner = joiner or self.default_splitter
        model = self.model_dump(mode="python")
        buffer = bytes()
        for k, v in self.__key_fields__.items():

            if buffer:
                buffer += joiner

            buffer += k
            name, field = v

            annotation = field.annotation
            item = model.get(name)

            buffer += joiner

            if issubclass(annotation, str):
                buffer += item.encode("utf-8", errors="surrogateescape")

            elif issubclass(annotation, int):
                buffer += f"{item}".encode("utf-8")

            elif issubclass(annotation, bytes):
                buffer += item

            elif issubclass(annotation, bool):
                buffer += b"1" if item is True else b"0"

            else:
                raise ValueError(
                    f'{annotation.__name__} has not been properly implemented for field "{name}"'
                )

        return buffer




