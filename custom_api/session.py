import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter



class HAClient:
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })

        retries = Retry(
            total=3,
            backoff_factor=0.3, # Waits 0.3s, 0.6s, 1.2s between retries
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get(self, endpoint: str, params=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self.session.get(url, params=params, timeout=10)

    def post(self, endpoint: str, json_data=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self.session.post(url, json=json_data, timeout=10)
    
    def close(self):
        self.session.close()
