from app.notify_client.service_api_client import ServiceApiClient


def test_client_gets_service(mocker):
    client = ServiceApiClient()
    mock_api_client = mocker.patch.object(client, 'api_client')

    client.get_service('foo')
    mock_api_client.get.assert_called_once_with('/service/foo')
