import pytest

from apis import login, new_phone, register


@pytest.fixture
def user_token():
    phone = new_phone()
    register(phone, "abc12345")
    token = login(phone, "abc12345").json()["data"]["token"]
    return phone, token


@pytest.fixture
def registered_user():
    phone = new_phone()
    register(phone, "abc12345")
    return phone