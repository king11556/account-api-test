import requests

from apis.config import BASE


def register(phone, password):
    return requests.post(BASE + "/register", json={"phone": phone, "password": password})


def login(phone, password):
    return requests.post(BASE + "/login", json={"phone": phone, "password": password})


def change_password(token, old, new):
    return requests.post(BASE + "/change-password",
                         json={"oldPassword": old, "newPassword": new},
                         headers={"Authorization": "Bearer " + token})


def get_profile(token, user_id=None):
    url = BASE + "/profile"
    if user_id is not None:
        url = url + "?userId=" + str(user_id)
    return requests.get(url, headers={"Authorization": "Bearer " + token})
