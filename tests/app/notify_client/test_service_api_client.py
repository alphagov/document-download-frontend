from notifications_python_client import __version__

from app.notify_client.service_api_client import ServiceApiClient
from application import application


def test_client_gets_service(mocker):
    client = ServiceApiClient()
    client.init_app(application)
    perform_request_mock = mocker.patch.object(client, "_perform_request")

    client.get_service("foo")

    url = perform_request_mock.call_args_list[0][0][1]
    assert url == "http://test-notify-api/service/foo"


def test_client_passes_expected_headers(mocker):
    client = ServiceApiClient()
    client.init_app(application)
    perform_request_mock = mocker.patch.object(client, "_perform_request")

    client.get_service("foo")

    request_kwargs = perform_request_mock.call_args_list[0][0][2]
    headers = request_kwargs["headers"]
    assert headers["Content-type"] == "application/json"
    assert headers["Authorization"].startswith("Bearer ")
    assert headers["X-Custom-Forwarder"] == "route-secret"
    assert headers["User-agent"] == f"NOTIFY-API-PYTHON-CLIENT/{__version__}"
