<<<<<<< HEAD
from flask import abort, current_app, render_template, request
=======
from flask import current_app, render_template, request
>>>>>>> initial build for document download

from app.main import main


@main.route("/services/<service_id>/documents/<document_id>", methods=['GET'])
<<<<<<< HEAD
def download_document_landing(service_id, document_id):
    key = request.args.get('key', None)
    if not key:
        abort(404)

    return render_template(
        'views/index.html',
        service_id=service_id,
        document_id=document_id,
        key=key
    )


@main.route("/services/<service_id>/documents/<document_id>/download", methods=['GET'])
def download_document_download(service_id, document_id):
    key = request.args.get('key', None)
    if not key:
        abort(404)
=======
def download_document(service_id, document_id):
>>>>>>> initial build for document download

    download_link = '{}/services/{}/documents/{}?key={}'.format(
        current_app.config['DOCUMENT_DOWNLOAD_API_HOST_NAME'],
        service_id,
        document_id,
<<<<<<< HEAD
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
=======
        request.args.get('key', 0)
    )

    return render_template(
        'views/index.html',
        download_link=download_link,
    )
>>>>>>> initial build for document download
