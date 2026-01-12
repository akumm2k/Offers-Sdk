from http import HTTPStatus
from typing import Type

import pytest

from http_client.base_client import HttpResponse, JSONType


@pytest.fixture
def sample_json() -> dict:
    return {"key1": "value1", "key2": 2, "key3": [1, 2, 3]}


@pytest.mark.parametrize(
    "json_type,json_data",
    [
        (dict, {"key": "value"}),
        (list, [1, 2, 3]),
        (dict, {"number": 42, "list": ["a", "b"]}),
        (list, [{"id": 1}, {"id": 2}, {"id": 3}]),
    ],
)
def test_get_json_as_dictionary(json_type: Type, json_data: JSONType):
    # Arrange
    http_response = HttpResponse(
        status_code=HTTPStatus.OK,
        json=json_data,
    )

    # Act
    actual_data = http_response.get_json_as(json_type)

    # Assert
    assert actual_data == json_data


@pytest.mark.parametrize(
    "json_data,invalid_type",
    [
        ({"key": "value"}, list),
        ({"number": 42, "list": ["a", "b"]}, list),
        ([1, 2, 3], dict),
        ([{"id": 1}, {"id": 2}, {"id": 3}], dict),
    ],
)
def test_get_json_as_invalid_type_raises(
    json_data: JSONType, invalid_type: Type
):
    # Arrange
    http_response = HttpResponse(
        status_code=HTTPStatus.OK,
        json=json_data,
    )

    # Act & Assert
    with pytest.raises(
        ValueError,
        match=f"Response JSON is not a {invalid_type.__name__}",
    ):
        http_response.get_json_as(invalid_type)
