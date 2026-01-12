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


class HttpResponse:
    def __init__(
        self,
        status_code: HTTPStatus,
        json: JSONType,
    ):
        self.status_code = status_code
        self.json = json

    def get_json_as[T](self, _type: Type[T]) -> T:
        if isinstance(self.json, _type):
            return self.json
        raise ValueError(
            f"Response JSON is not a {_type.__name__}"
            f", but {type(self.json).__name__}"
        )
