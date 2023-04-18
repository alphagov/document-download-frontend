import re
from datetime import date

from dateutil import parser
from notifications_utils.recipients import EMAIL_REGEX_PATTERN


def assess_contact_type(service_contact_info):
    if re.search(EMAIL_REGEX_PATTERN, service_contact_info):
        return "email"
    if service_contact_info.startswith("http"):
        return "link"
    else:
        return "other"


def bytes_to_pretty_file_size(bytes):
    if bytes < 1024 / 20:
        # File less than 0.05KB (one twentieth of a KB) don't round to 0.1KB at 1 d.p.
        # We will force them up to 0.1KB ourselves as we don't want to show users 0.0KB or bytes
        return "0.1KB"
    elif bytes < (1024**2) / 20:
        # File less than 0.05MB to be represented in KB
        # Anything bigger will round at 1dp to at least 0.1MB
        kb_to_1dp = round(bytes / 1024, 1)
        return str(kb_to_1dp).rstrip(".0") + "KB"
    else:
        mb_to_1dp = round(bytes / (1024**2), 1)
        return str(mb_to_1dp).rstrip(".0") + "MB"


def document_has_expired(available_until):
    file_expiry_date = parser.parse(available_until).date()

    # if expiry date passed, even if file is still available, we do not return it to respect data retention period
    # set by the service
    if file_expiry_date < date.today():
        return True

    return False
