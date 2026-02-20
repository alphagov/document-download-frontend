import re
from datetime import date

from dateutil import parser
from notifications_utils.recipient_validation.email_address import EMAIL_REGEX_PATTERN


def assess_contact_type(service_contact_info):
    if re.search(EMAIL_REGEX_PATTERN, service_contact_info):
        return "email"
    if service_contact_info.startswith("http"):
        return "link"
    else:
        return "other"


def document_has_expired(available_until):
    file_expiry_date = parser.parse(available_until).date()

    # if expiry date passed, even if file is still available, we do not return it to respect data retention period
    # set by the service
    if file_expiry_date < date.today():
        return True

    return False
