from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class Offer(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: UUID
    price: int
    items_in_stock: int


Offers = TypeAdapter(List[Offer])


class Product(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    description: str


class ProductID(BaseModel):
    model_config = ConfigDict(frozen=True)
    product_id: str = Field(alias="id")
