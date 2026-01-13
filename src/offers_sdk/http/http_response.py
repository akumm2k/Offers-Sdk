from dataclasses import dataclass
from http import HTTPStatus
from typing import List, Mapping, Type, TypeAlias

JSONType: TypeAlias = (
    Mapping[str, "JSONType"]
    | List["JSONType"]
    | int
    | str
    | float
    | bool
    | None
)


@dataclass(frozen=True)
class HttpResponse:
    status_code: HTTPStatus
    json: JSONType

    def get_json_as[T](self, _type: Type[T]) -> T:
        if isinstance(self.json, _type):
            return self.json
        raise ValueError(
            f"Response JSON is not a {_type.__name__}"
            f", but {type(self.json).__name__}"
        )
