from datetime import date, timedelta
from urllib import parse

import requests
from dateutil import parser
from flask import abort, current_app, redirect, render_template, request, url_for
from flask.ctx import has_request_context
from markupsafe import Markup
from notifications_python_client.errors import HTTPError
from werkzeug.exceptions import TooManyRequests

from app import service_api_client
from app.forms import EmailAddressForm
from app.main import main
from app.utils import (
    assess_contact_type,
    bytes_to_pretty_file_size,
    document_has_expired,
)

FILE_EXTENSION_TO_PRETTY_FILE_TYPE = {
    "csv": "CSV file",
    "doc": "Microsoft Word document",
    "docx": "Microsoft Word document",
    "odt": "text file",
    "pdf": "PDF",
    "png": "PNG file",
    "rtf": "text file",
    "txt": "text file",
    "jpeg": "JPEG file",
    "json": "JSON file",
    "xlsx": "Microsoft Excel spreadsheet",
}


@main.route("/_status")
def status():
    return {
        "status": "ok",
    }, 200


@main.route("/services/_status")
@main.route("/services/<uuid:service_id>/documents/<uuid:document_id>", methods=["GET"])
@main.route("/services/<uuid:service_id>/documents/<uuid:document_id>.<extension>", methods=["GET"])
@main.route("/services/<uuid:service_id>/documents/<uuid:document_id>/check", methods=["GET"])
def services(service_id=None, document_id=None, extension=None):
    api_host = current_app.config["DOCUMENT_DOWNLOAD_API_HOST_NAME"]
    path = request.path
    query_string = request.query_string.decode("utf-8")
    if len(query_string) > 1:
        return redirect(f"{api_host}{path}?{query_string}", 301)
    else:
        return redirect(f"{api_host}{path}", 301)


@main.route("/.well-known/security.txt", methods=["GET"])
@main.route("/security.txt", methods=["GET"])
def security_policy():
    # See GDS Way security policy which this implements
    # https://gds-way.cloudapps.digital/standards/vulnerability-disclosure.html#vulnerability-disclosure-and-security-txt
    return redirect("https://vdp.cabinetoffice.gov.uk/.well-known/security.txt")


@main.route("/d/<base64_uuid:service_id>/<base64_uuid:document_id>", methods=["GET"])
def landing(service_id, document_id):
    key = request.args.get("key", None)
    if not key:
        abort(404)

    service = _get_service_or_raise_error(service_id)

    service_contact_info = service["data"]["contact_link"]
    contact_info_type = assess_contact_type(service_contact_info)
    metadata = _get_document_metadata(service_id, document_id, key)

    if not metadata or document_has_expired(metadata["available_until"]):
        return render_template(
            "views/file_unavailable.html",
            service_name=service["data"]["name"],
            service_contact_info=service_contact_info,
            contact_info_type=contact_info_type,
        )

    if "confirm_email" not in metadata:
        current_app.logger.info(
            "Metadata for %(service_id)s/%(document_id)s does not contain `confirm_email` key: %(metadata)s",
            {"service_id": service_id, "document_id": document_id, "metadata": metadata},
        )

    if metadata.get("confirm_email", False) is True:
        continue_url = url_for("main.confirm_email_address", service_id=service_id, document_id=document_id, key=key)

    else:
        continue_url = url_for("main.download_document", service_id=service_id, document_id=document_id, key=key)

    return render_template(
        "views/index.html",
        service_id=service_id,
        service_name=service["data"]["name"],
        service_contact_info=service_contact_info,
        contact_info_type=contact_info_type,
        document_id=document_id,
        key=key,
        continue_url=continue_url,
    )


@main.route("/d/<base64_uuid:service_id>/<base64_uuid:document_id>/confirm-email-address", methods=["GET", "POST"])
def confirm_email_address(service_id, document_id):
    key = request.args.get("key")
    if not key:
        abort(404)

    service = _get_service_or_raise_error(service_id)

    metadata = _get_document_metadata(service_id, document_id, key)
    service_contact_info = service["data"]["contact_link"]
    service_name = service["data"]["name"]
    contact_info_type = assess_contact_type(service_contact_info)

    if not metadata or document_has_expired(metadata["available_until"]):
        return render_template(
            "views/file_unavailable.html",
            service_name=service_name,
            service_contact_info=service_contact_info,
            contact_info_type=contact_info_type,
        )

    if metadata["confirm_email"] is False:
        return redirect(url_for(".download_document", service_id=service_id, document_id=document_id, key=key))

    form = EmailAddressForm()

    if form.validate_on_submit():
        try:
            authentication_data = _authenticate_access_to_document(
                service_id, document_id, key, form.email_address.data
            )

        except TooManyRequests:
            return (
                render_template("error/429.html", go_back_link=request.url, page_name="confirm your email address"),
                429,
            )

        if authentication_data:
            set_cookie_values = {
                "key": "document_access_signed_data",
                "value": authentication_data["signed_data"],
                "path": authentication_data["cookie_path"],
                "secure": current_app.config["HTTP_PROTOCOL"] == "https",
                "httponly": True,
            }

            # the cookie is set by the frontend, and read by the api
            # this works fine when they're both under the same domain
            # but when we're in a subdomain, we need to allow the cookie to be sent to subdomains too
            # docs: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#domain_attribute
            cookie_domain = current_app.config["DOCUMENT_DOWNLOAD_API_HOST_NAME"].replace("https://download.", "")
            set_cookie_values["domain"] = cookie_domain

            response = redirect(url_for(".download_document", service_id=service_id, document_id=document_id, key=key))
            response.set_cookie(**set_cookie_values)
            return response

        form.form_errors.append(
            Markup(
                "This is not the email address the file was sent to.<br><br>"
                f"To confirm the file was meant for you, enter the email address {service_name} sent the file to."
            )
        )

    return (
        render_template(
            "views/confirm_email_address.html",
            form=form,
            service_name=service_name,
            service_id=service_id,
            service_contact_info=service_contact_info,
            contact_info_type=contact_info_type,
            document_id=document_id,
            key=key,
        ),
        400 if form.errors else 200,
    )


@main.route("/d/<base64_uuid:service_id>/<base64_uuid:document_id>/download", methods=["GET"])
def download_document(service_id, document_id):
    key = request.args.get("key", None)
    if not key:
        abort(404)

    service = _get_service_or_raise_error(service_id)

    metadata = _get_document_metadata(service_id, document_id, key)
    service_contact_info = service["data"]["contact_link"]
    contact_info_type = assess_contact_type(service_contact_info)

    if not metadata or document_has_expired(metadata["available_until"]):
        return render_template(
            "views/file_unavailable.html",
            service_name=service["data"]["name"],
            service_contact_info=service_contact_info,
            contact_info_type=contact_info_type,
        )

    return render_template(
        "views/download.html",
        download_link=metadata["direct_file_url"],
        file_size=bytes_to_pretty_file_size(metadata["size_in_bytes"]),
        file_type=FILE_EXTENSION_TO_PRETTY_FILE_TYPE[metadata["file_extension"]],
        service_name=service["data"]["name"],
        service_contact_info=service_contact_info,
        contact_info_type=contact_info_type,
        file_expiry_date=_format_file_expiry_date(metadata["available_until"]),
    )


def _format_file_expiry_date(available_until: str) -> str:
    file_expiry_date = parser.parse(available_until).date()

    # only show day of the week if file expiry date within a month from today
    if file_expiry_date - date.today() <= timedelta(days=30):
        return file_expiry_date.strftime("%A %d %B %Y")
    else:
        return file_expiry_date.strftime("%d %B %Y")


def _get_service_or_raise_error(service_id):
    try:
        return service_api_client.get_service(service_id)
    except HTTPError as e:
        abort(e.status_code)


def _get_document_metadata(service_id, document_id, key):
    check_file_url = "{}/services/{}/documents/{}/check?key={}".format(
        current_app.config["DOCUMENT_DOWNLOAD_API_HOST_NAME_INTERNAL"], service_id, document_id, key
    )
    headers = {}
    if has_request_context() and hasattr(request, "get_onwards_request_headers"):
        headers.update(request.get_onwards_request_headers())

    response = requests.get(check_file_url, headers=headers)

    if response.status_code == 400:
        error_msg = response.json().get("error", "")
        # If the decryption key is missing or can't be decoded using `urlsafe_b64decode`,
        # the error message will contain 'decryption key'.
        # If the decryption key is wrong, the error message is 'Forbidden'
        if "decryption key" in error_msg or "Forbidden" in error_msg:
            abort(404)

    # Let the `500` error handler handle unexpected errors from doc-download-api
    response.raise_for_status()

    return response.json().get("document")


def _authenticate_access_to_document(service_id, document_id, key, email_address) -> dict | None:
    auth_file_url = "{}/services/{}/documents/{}/authenticate".format(
        current_app.config["DOCUMENT_DOWNLOAD_API_HOST_NAME_INTERNAL"],
        service_id,
        document_id,
    )
    headers = {}
    if has_request_context() and hasattr(request, "get_onwards_request_headers"):
        headers.update(request.get_onwards_request_headers())

    response = requests.post(
        auth_file_url,
        json={"key": key, "email_address": email_address},
        headers=headers,
    )

    if response.status_code == 429:
        raise TooManyRequests

    elif response.status_code in {400, 403}:
        return None

    data = response.json()

    # Let the `500` error handler handle unexpected errors from doc-download-api
    response.raise_for_status()

    cookie_path = parse.urlsplit(data["direct_file_url"]).path

    return {
        "signed_data": data["signed_data"],
        "cookie_path": cookie_path,
    }
