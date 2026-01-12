from dataclasses import dataclass


@dataclass(init=False)
class Actions:
    REGISTER_PRODUCT: str = "Register Product"
    GET_OFFERS: str = "Get Offers"
    EXIT: str = "Exit"
