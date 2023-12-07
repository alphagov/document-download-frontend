from __future__ import unicode_literals

from notifications_python_client.notifications import BaseAPIClient


class ServiceApiClient:
    def __init__(self):
        self.api_client = None

    def init_app(self, application):
        self.api_client = BaseAPIClient(base_url=application.config["API_HOST_NAME"], api_key="a" * 75)
        self.api_client.service_id = application.config["ADMIN_CLIENT_USER_NAME"]
        self.api_client.api_key = application.config["ADMIN_CLIENT_SECRET"]

    def get_service(self, service_id):
        """
        Retrieve a service.
        """
        return self.api_client.get("/service/{0}".format(service_id))
