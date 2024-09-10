from flask import request
from flask.ctx import has_request_context
from notifications_python_client.notifications import NotificationsAPIClient


class OnwardsRequestNotificationsAPIClient(NotificationsAPIClient):
    def generate_headers(self, api_token):
        headers = super().generate_headers(api_token)

        if has_request_context() and hasattr(request, "get_onwards_request_headers"):
            headers = {
                **request.get_onwards_request_headers(),
                **headers,
            }

        return headers


class ServiceApiClient:
    def __init__(self, app):
        self.api_client = OnwardsRequestNotificationsAPIClient(
            "x" * 100,
            base_url=app.config["API_HOST_NAME"],
        )
        # our credential lengths aren't what NotificationsAPIClient's __init__ will expect
        # given it's designed for destructuring end-user api keys
        self.api_client.service_id = app.config["ADMIN_CLIENT_USER_NAME"]
        self.api_client.api_key = app.config["ADMIN_CLIENT_SECRET"]

    def get_service(self, service_id):
        """
        Retrieve a service.
        """
        return self.api_client.get(f"/service/{service_id}")
