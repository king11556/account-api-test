import pytest
import allure


from apis import new_phone, register, login

pytestmark = allure.feature("登录模块")


@pytest.mark.smoke
def test_login_ok():
    phone = new_phone()
    print("本次使用的手机号:", phone)

    register(phone, "abc12345")

    r = login(phone, "abc12345")

    body = r.json()
    assert r.status_code == 200
    assert body["code"] == 0
    assert "token" in body["data"]


@pytest.mark.xfail(reason="缺陷：登录失败返回 200，文档要求 401")
def test_login_wrong_password():
    phone = new_phone()
    print("本次使用的手机号:", phone)

    register(phone, "abc12345")

    r = login(phone, "wrong9999")

    body = r.json()
    assert r.status_code == 401
    assert body["code"] == 1001


@pytest.mark.xfail(reason="缺陷：登录失败返回 200，文档要求 401")
def test_login_phone_not_exist():
    phone = new_phone()
    print("本次使用的手机号:", phone)

    r = login(phone, "abc12345")

    body = r.json()
    assert r.status_code == 401
    assert body["code"] == 1001