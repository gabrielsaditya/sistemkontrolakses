
import requests
from frontend.config import FASTAPI_URL

def get_token(username, password):
    response = requests.post(
        f"{FASTAPI_URL}/auth/login",
        data={
            "username": username,
            "password": password
        }
    )

    print("LOGIN:", response.status_code, response.text)
    response.raise_for_status()
    return response.json()["access_token"]


def register(username, password, full_name):
    response = requests.post(
        f"{FASTAPI_URL}/auth/register",
        json={
            "username": username,
            "password": password,
            "full_name": full_name
        }
    )

    print("REGISTER:", response.status_code, response.text)
    response.raise_for_status()
    return response.json()["access_token"]

def request(method, endpoint, token=None, api_key=None, **kwargs):

    headers = kwargs.pop('headers', {})

    if token:
        headers['Authorization'] = f"Bearer {token}"

    if api_key:
        headers['X-Device-Key'] = f"{api_key}"

    response = requests.request(
        method,
        f"{FASTAPI_URL}{endpoint}",
        headers=headers,
        timeout=120,
        **kwargs
    )
    response.raise_for_status()
    if response.status_code == 403:
        raise Exception("You are not and admin! Please contact your administrator.")
    if response.status_code == 204:
        return None
    return response.json()

"""
CONTOH PENGGUNAAN:
request("GET", "/pekerja/", token=st.session_state.token)

request("POST", "/pekerja/", token=st.session_state.token, json=data)

request("DELETE", "/pekerja/123", token=st.session_state.token)
"""