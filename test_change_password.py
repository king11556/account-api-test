import allure
import pytest

from apis import change_password

pytestmark = allure.feature("改密模块")

@pytest.mark.smoke
def test_change_password_ok(user_token):
    phone, token = user_token
    print("本次使用的手机号:", phone)
    r = change_password(token, "abc12345", "newpass123")
    body = r.json()
    assert r.status_code == 200
    assert body["code"] == 0


def test_change_password_wrong_old(user_token):
    # 原密码传 wrong9999，新密码 newpass123 → 400 / 3001
    phone, token = user_token
    print("本次使用的手机号:", phone)
    r = change_password(token, "wrong9999", "newpass123")
    body = r.json()
    assert r.status_code == 400
    assert body["code"] == 3001


def test_change_password_same_as_old(user_token):
    # 新密码传 abc12345（跟原密码一样）→ 400 / 3002
    phone, token = user_token
    print("本次使用的手机号:", phone)
    r = change_password(token, "abc12345", "abc12345")
    body = r.json()
    assert r.status_code == 400
    assert body["code"] == 3002


def test_change_password_too_short(user_token):
    # 新密码传 abc12（5 位）→ 400 / 2002
    phone, token = user_token
    print("本次使用的手机号:", phone)
    r = change_password(token, "abc12345", "abc12")
    body = r.json()
    assert r.status_code == 400
    assert body["code"] == 2002
