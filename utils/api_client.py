import requests

from utils.helper import Helper


class ApiClient:

    def post(self, url: str, headers: dict, payload: dict) -> requests.Response:
        response = requests.post(url=url, headers=headers, json=payload)
        Helper.attach_response("Response HTTP status", response.status_code)
        Helper.attach_response("Response headers", dict(response.headers))
        Helper.attach_response("Response body", response.text)
        return response

    def get(self, url: str, headers: dict) -> requests.Response:
        response = requests.get(url=url, headers=headers)
        Helper.attach_response("Response HTTP status", response.status_code)
        Helper.attach_response("Response headers", dict(response.headers))
        Helper.attach_response("Response body", response.text)
        return response
