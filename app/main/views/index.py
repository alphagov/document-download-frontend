from flask import abort, current_app, render_template, request
from notifications_python_client.errors import HTTPError

from app import service_api_client
from app.main import main


@main.route("/services/<service_id>/documents/<document_id>", methods=['GET'])
def download_document_landing(service_id, document_id):
    key = request.args.get('key', None)
    if not key:
        abort(404)

    try:
        service = service_api_client.get_service(service_id)
    except HTTPError as e:
        abort(e.status_code)

    return render_template(
        'views/index.html',
        service_id=service_id,
        service_name=service['data']['name'],
        service_contact_link='https://www.google.com',  # to be replaced by the contact URL when populated
        document_id=document_id,
        key=key
    )


@main.route("/services/<service_id>/documents/<document_id>/download", methods=['GET'])
def download_document_download(service_id, document_id):
    key = request.args.get('key', None)
    if not key:
        abort(404)

    download_link = '{}/services/{}/documents/{}?key={}'.format(
        current_app.config['DOCUMENT_DOWNLOAD_API_HOST_NAME'],
        service_id,
        document_id,
        key
    )

    return render_template(
        'views/download.html',
        download_link=download_link,
    )


@main.route("/post-my-document", methods=['GET'])
def post_my_document():

    return render_template(
        'views/post-my-document.html',
    )
