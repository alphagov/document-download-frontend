from unittest import mock

from notifications_utils.testing.comparisons import AnySupersetOf

from app.notify_client.service_api_client import ServiceApiClient


def test_client_gets_service(mocker):
    client = ServiceApiClient()
    mock_api_client = mocker.patch.object(client, "api_client")

    client.get_service("foo")
    mock_api_client.get.assert_called_once_with("/service/foo")


def test_client_uses_route_secret(app_, rmock, service_id, sample_service):
    app_.config["ROUTE_SECRET_KEY_1"] = "hello"

    client = ServiceApiClient()
    client.init_app(app_)

    rmock.get(
        "{}/service/{}".format(
            app_.config["API_HOST_NAME"],
            service_id,
        ),
        status_code=200,
        json={"data": sample_service},
    )

    client.get_service(service_id)

    assert len(rmock.request_history) == 1
    assert rmock.request_history[0].headers == AnySupersetOf({"X-Custom-Forwarder": "hello"})


def test_client_onward_headers(app_, rmock, service_id, sample_service):
    client = ServiceApiClient()
    client.init_app(app_)

    rmock.get(
        "{}/service/{}".format(
            app_.config["API_HOST_NAME"],
            service_id,
        ),
        status_code=200,
        json={"data": sample_service},
    )

    with app_.test_request_context():
        with mock.patch(
            "flask.request.get_onwards_request_headers",
            return_value={
                "some-onwards": "request-headers",
                "fooed": "barred",
            },
        ):
            client.get_service(service_id)

    assert len(rmock.request_history) == 1
    assert rmock.request_history[0].headers == AnySupersetOf(
        {"some-onwards": "request-headers", "fooed": "barred", "X-Custom-Forwarder": ""}
    )


def test_client_no_onward_headers(app_, rmock, service_id, sample_service):
    client = ServiceApiClient()
    client.init_app(app_)

    rmock.get(
        "{}/service/{}".format(
            app_.config["API_HOST_NAME"],
            service_id,
        ),
        status_code=200,
        json={"data": sample_service},
    )

    # ensure this still works outside a request context
    client.get_service(service_id)

    assert len(rmock.request_history) == 1
