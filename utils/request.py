from dataclasses import dataclass

import requests

@dataclass
class ApiResponse:
    status_code: int
    text: str
    as_dict: object
    headers: dict

class ApiRequest:
    def __init__(self, url, method, headers=None, params=None, data=None, json=None):
        self.url = url
        self.method = method
        self.headers = headers
        self.params = params
        self.data = data
        self.json = json

    def send(self):
        response = requests.request(
            self.method,
            self.url,
            headers=self.headers,
            params=self.params,
            data=self.data,
            json=self.json
        )
        return ApiResponse(
            status_code=response.status_code,
            text=response.text,
            as_dict=response.json(),
            headers=response.headers
        )