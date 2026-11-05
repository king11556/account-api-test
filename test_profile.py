import allure
import pytest

from apis import change_password, get_profile, login, new_phone, register

pytestmark = allure.feature("个人资料模块")


@pytest.mark.smoke
@pytest.mark.security
@pytest.mark.xfail(reason="缺陷：可越权查看他人资料，已手工复现")
def test_profile_other_user_forbidden():
    phone_a = new_phone()
    phone_b = new_phone()
    print("甲:", phone_a, "乙:", phone_b)

    register(phone_a, "abc12345")
    user_b = register(phone_b, "abc12345").json()["data"]["userId"]

    token_a = login(phone_a, "abc12345").json()["data"]["token"]

    r = get_profile(token_a, user_b)
    body = r.json()
    assert r.status_code == 403
    assert body["code"] == 4003


@pytest.mark.security
@pytest.mark.xfail(reason="缺陷：改密后旧 token 未失效，已手工复现")
def test_old_token_invalid_after_change_password(user_token):
    phone, token = user_token
    print("本次使用的手机号:", phone)

    r = change_password(token, "abc12345", "newpass123")
    body = r.json()
    assert r.status_code == 200
    assert body["code"] == 0

    r = get_profile(token)
    body = r.json()
    assert r.status_code == 401
    assert body["code"] == 1002