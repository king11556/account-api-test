import allure
import pytest

from apis import new_phone, register

pytestmark = allure.feature("注册模块")


@pytest.mark.parametrize("password, status, code", [
    pytest.param("abc1234", 400, 2002),
    pytest.param("abcdefgh12345678", 200, 0,
                 marks=pytest.mark.xfail(reason="缺陷：16 位密码被拒，文案却写 8-16 位")),
])
def test_password_length(password, status, code):
    phone = new_phone()
    print("本次使用的手机号:", phone)
    r = register(phone, password)
    body = r.json()
    assert r.status_code == status
    assert body["code"] == code


@pytest.mark.smoke
def test_register_ok():
    phone = new_phone()
    print("本次使用的手机号:", phone)
    r = register(phone, "abc12345")
    body = r.json()
    assert r.status_code == 200
    assert body["code"] == 0


@pytest.mark.smoke
def test_phone_empty():
    r = register("", "abc12345")
    body = r.json()
    assert r.status_code == 400
    assert body["code"] == 2001


def test_register_duplicate(registered_user):
    phone = registered_user
    print("本次使用的手机号:", phone)
    r = register(phone, "abc12345")
    body = r.json()
    assert r.status_code == 409
    assert body["code"] == 2006


def test_phone_format_10():
    r = register("1390000123", "abc12345")
    body = r.json()
    assert r.status_code == 400
    assert body["code"] == 2004


def test_password_empty():
    phone = new_phone()
    print("本次使用的手机号:", phone)
    r = register(phone, "")
    body = r.json()
    assert r.status_code == 400
    assert body["code"] == 2001


@pytest.mark.xfail(reason="缺陷：密码组成只校验数字，未校验字母")
def test_password_composition():
    phone = new_phone()
    print("本次使用的手机号:", phone)
    r = register(phone, "12345678")
    body = r.json()
    assert r.status_code == 400
    assert body["code"] == 2003


def test_phone_first_digit_not_1():
    r = register("23900001234", "abc12345")
    body = r.json()
    assert r.status_code == 400
    assert body["code"] == 2004
