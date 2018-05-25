from app.notify_client.service_api_client import ServiceAPIClient


def test_client_gets_service(mocker):
    client = ServiceAPIClient()
    mock_get = mocker.patch.object(client, 'get', return_value={})

    client.get_service('foo')
    mock_get.assert_called_once_with('/service/foo')
