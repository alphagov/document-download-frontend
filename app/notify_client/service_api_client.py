from __future__ import unicode_literals

from notifications_python_client.notifications import NotificationsAPIClient


class ServiceApiClient:

    def __init__(self):
        self.api_client = None

    def init_app(self, application):
        # get api_key and base_url out of application.config
        api_key = application.config['ADMIN_CLIENT_USER_NAME'] + '-' + application.config['ADMIN_CLIENT_SECRET']
        self.api_client = NotificationsAPIClient(base_url=application.config['API_HOST_NAME'],
                                                 api_key=api_key)

    def get_service(self, service_id):
        """
        Retrieve a service.
        """
        return self.api_client.get('/service/{0}'.format(service_id))
