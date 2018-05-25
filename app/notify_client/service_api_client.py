from __future__ import unicode_literals

from app.notify_client import NotifyAPIClient


class ServiceAPIClient(NotifyAPIClient):
    # Fudge assert in the super __init__ so
    # we can set those variables later.
    def __init__(self):
        super().__init__("a" * 73, "b")

    def get_service(self, service_id):
        """
        Retrieve a service.
        """
        return self.get('/service/{0}'.format(service_id))
