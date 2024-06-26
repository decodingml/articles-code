import os


class ProxyConnection:

    def __init__(
        self,
        host: str = None,
        port: str = None,
        username: str = None,
        password: str = None,
        verify_ssl: bool = False
    ):
        self.host = host or os.getenv('PROXY_HOST')
        self.port = port or os.getenv('PROXY_PORT')
        self.username = username or os.getenv('PROXY_USERNAME')
        self.password = password or os.getenv('PROXY_PASSWORD')
        self.verify_ssl = verify_ssl
        self._url = f"{self.username}:{self.password}@{self.host}:{self.port}"

    def __dict__(self):
        return {
            'https': 'https://{}'.format(self._url.replace(" ", "")),
            'http': 'http://{}'.format(self._url.replace(" ", "")),
            'no_proxy': 'localhost, 127.0.0.1',
            'verify_ssl': self.verify_ssl
        }
