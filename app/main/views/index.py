import requests
from flask import abort, current_app, render_template, request
from notifications_python_client.errors import HTTPError

from app import service_api_client
from app.main import main
from app.utils import assess_contact_type


@main.route('/_status')
def status():
    return "ok", 200


@main.route('/d/<base64_uuid:service_id>/<base64_uuid:document_id>', methods=['GET'])
def landing(service_id, document_id):
    key = request.args.get('key', None)
    if not key:
        abort(404)

    try:
        service = service_api_client.get_service(service_id)
    except HTTPError as e:
        abort(e.status_code)

    service_contact_info = service['data']['contact_link']
    contact_info_type = assess_contact_type(service_contact_info)

    if not get_document_metadata(service_id, document_id, key):
        return render_template(
            'views/file_unavailable.html',
            service_name=service['data']['name'],
            service_contact_info=service_contact_info,
            contact_info_type=contact_info_type,
        )

    return render_template(
        'views/index.html',
        service_id=service_id,
        service_name=service['data']['name'],
        service_contact_info=service_contact_info,
        contact_info_type=contact_info_type,
        document_id=document_id,
        key=key
    )


@main.route('/d/<base64_uuid:service_id>/<base64_uuid:document_id>/download', methods=['GET'])
def download_document(service_id, document_id):
    key = request.args.get('key', None)
    if not key:
        abort(404)

    try:
        service = service_api_client.get_service(service_id)
    except HTTPError as e:
        abort(e.status_code)

    metadata = get_document_metadata(service_id, document_id, key)
    service_contact_info = service['data']['contact_link']
    contact_info_type = assess_contact_type(service_contact_info)

    if not metadata:
        return render_template(
            'views/file_unavailable.html',
            service_name=service['data']['name'],
            service_contact_info=service_contact_info,
            contact_info_type=contact_info_type,
        )

    return render_template(
        'views/download.html',
        download_link=metadata['direct_file_url'],
        service_name=service['data']['name'],
        service_contact_info=service_contact_info,
        contact_info_type=contact_info_type,
    )


def get_document_metadata(service_id, document_id, key):
    check_file_url = '{}/services/{}/documents/{}/check?key={}'.format(
        current_app.config['DOCUMENT_DOWNLOAD_API_HOST_NAME'],
        service_id,
        document_id,
        key
    )
    response = requests.get(check_file_url)

    if response.status_code == 400:
        error_msg = response.json().get('error', '')
        # If the decryption key is missing or can't be decoded using `urlsafe_b64decode`,
        # the error message will contain 'decryption key'.
        # If the decryption key is wrong, the error message is 'Forbidden'
        if 'decryption key' in error_msg or 'Forbidden' in error_msg:
            abort(404)

    # Let the `500` error handler handle unexpected errors from doc-download-api
    response.raise_for_status()

    return response.json().get('document')
