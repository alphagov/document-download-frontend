import requests
from flask import (
    abort,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)
from markupsafe import Markup
from notifications_python_client.errors import HTTPError

from app import service_api_client
from app.forms import EmailAddressForm
from app.main import main
from app.utils import assess_contact_type


@main.route('/_status')
def status():
    return "ok", 200


@main.route('/.well-known/security.txt', methods=['GET'])
@main.route('/security.txt', methods=['GET'])
def security_policy():
    # See GDS Way security policy which this implements
    # https://gds-way.cloudapps.digital/standards/vulnerability-disclosure.html#vulnerability-disclosure-and-security-txt
    return redirect("https://vdp.cabinetoffice.gov.uk/.well-known/security.txt")


@main.route('/d/<base64_uuid:service_id>/<base64_uuid:document_id>', methods=['GET'])
def landing(service_id, document_id):
    key = request.args.get('key', None)
    if not key:
        abort(404)

    service = _get_service_or_raise_error(service_id)

    service_contact_info = service['data']['contact_link']
    contact_info_type = assess_contact_type(service_contact_info)

    if not _get_document_metadata(service_id, document_id, key):
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


@main.route('/d/<base64_uuid:service_id>/<base64_uuid:document_id>/confirm-email-address', methods=['GET', 'POST'])
def confirm_email_address(service_id, document_id):
    key = request.args.get('key')
    if not key:
        abort(404)

    service = _get_service_or_raise_error(service_id)

    service_contact_info = service['data']['contact_link']
    contact_info_type = assess_contact_type(service_contact_info)

    if not _get_document_metadata(service_id, document_id, key):
        return render_template(
            'views/file_unavailable.html',
            service_name=service['data']['name'],
            service_contact_info=service_contact_info,
            contact_info_type=contact_info_type,
        )

    form = EmailAddressForm()

    if form.validate_on_submit():
        if 'email_address_wrong':
            form.form_errors.append(
                Markup(
                    "This is not the email address the file was sent to."
                    "<br><br>"
                    "To confirm the file was meant for you, enter the email address ((service name)) sent the file to."
                )
            )

        else:
            return redirect(url_for('.download_document', service_id=service_id, document_id=document_id, key=key))

    return render_template(
        'views/confirm_email_address.html',
        form=form,
        service_id=service_id,
        document_id=document_id,
        key=key,
    )


@main.route('/d/<base64_uuid:service_id>/<base64_uuid:document_id>/download', methods=['GET'])
def download_document(service_id, document_id):
    key = request.args.get('key', None)
    if not key:
        abort(404)

    service = _get_service_or_raise_error(service_id)

    metadata = _get_document_metadata(service_id, document_id, key)
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


def _get_service_or_raise_error(service_id):
    try:
        return service_api_client.get_service(service_id)
    except HTTPError as e:
        abort(e.status_code)


def _get_document_metadata(service_id, document_id, key):
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
