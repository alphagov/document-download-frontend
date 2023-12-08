from __future__ import unicode_literals

from notifications_python_client import __version__
from notifications_python_client.notifications import BaseAPIClient


class ServiceApiClient(BaseAPIClient):
    def __init__(self):
        super().__init__("a" * 73, "b")

    def init_app(self, application):
        self.base_url = application.config["API_HOST_NAME"]
        self.service_id = application.config["ADMIN_CLIENT_USER_NAME"]
        self.api_key = application.config["ADMIN_CLIENT_SECRET"]
        self.route_secret = application.config["ROUTE_SECRET_KEY_1"]

    def generate_headers(self, api_token):
        return {
            "Content-type": "application/json",
            "Authorization": f"Bearer {api_token}",
            "X-Custom-Forwarder": self.route_secret,
            "User-agent": f"NOTIFY-API-PYTHON-CLIENT/{__version__}",
        }

    def get_service(self, service_id):
        """
        Retrieve a service.
        """
        return self.get(f"/service/{service_id}")
