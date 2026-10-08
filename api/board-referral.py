from importlib.util import module_from_spec, spec_from_file_location
import hmac
import json
import os
import re
import smtplib
import sys
import time
from email.utils import formataddr
from http.server import BaseHTTPRequestHandler
from pathlib import Path

_EMAIL_MODULE_PATH = Path(__file__).with_name("_board_referral_email.py")
_EMAIL_SPEC = spec_from_file_location("_board_referral_email", _EMAIL_MODULE_PATH)
if _EMAIL_SPEC is None or _EMAIL_SPEC.loader is None:
    raise ImportError("Unable to load referral email module")
_EMAIL_MODULE = module_from_spec(_EMAIL_SPEC)
sys.modules[_EMAIL_SPEC.name] = _EMAIL_MODULE
_EMAIL_SPEC.loader.exec_module(_EMAIL_MODULE)

SUPPORT_EMAIL = _EMAIL_MODULE.SUPPORT_EMAIL
build_email = _EMAIL_MODULE.build_email


SEND_TIMES = []
# This in process password failure counter resets on cold start.
FAILED_PASSWORD_TIMES = {}
ALLOWED_FIELDS = {
    "recipient_first_name",
    "recipient_last_name",
    "recipient_email",
    "recipient_phone",
    "plan_id",
    "addon_quantity",
    "consent",
    "board_member_name",
    "password",
}


def _load_plans():
    plans_path = os.path.join(os.path.dirname(__file__), "..", "src", "data", "plans.json")
    with open(plans_path, encoding="utf-8") as plans_file:
        records = json.load(plans_file)
    if not isinstance(records, list):
        raise ValueError("Invalid plan data")
    return {record["plan_id"]: record for record in records if isinstance(record, dict) and record.get("plan_id")}


def _contains_url(value):
    return any(token in str(value).lower() for token in ("http", "://", "www."))


def _send_json(handler, status, payload):
    response = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(response)))
    handler.end_headers()
    handler.wfile.write(response)


def _generic_error(handler, status=400):
    _send_json(handler, status, {"success": False, "message": "Unable to process referral."})


class handler(BaseHTTPRequestHandler):
    def _read_data(self):
        content_length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(content_length).decode("utf-8") or "{}")

    def _reject_method(self):
        _generic_error(self, 405)

    do_GET = _reject_method
    do_PUT = _reject_method
    do_DELETE = _reject_method
    do_PATCH = _reject_method

    def do_POST(self):
        try:
            data = self._read_data()
            if not isinstance(data, dict) or _contains_url(json.dumps(data)):
                return _generic_error(self)
            if set(data) != ALLOWED_FIELDS:
                return _generic_error(self)

            password = str(data.get("password", ""))
            configured_password = os.environ.get("BOARD_REFERRAL_PASSWORD", "")
            # Cloudflare provides the visitor IP; forwarded-for may contain its edge IP.
            client_ip = self.headers.get("cf-connecting-ip", "").strip() or self.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
            now = time.time()
            failures = [stamp for stamp in FAILED_PASSWORD_TIMES.get(client_ip, []) if now - stamp < 900]
            if failures:
                FAILED_PASSWORD_TIMES[client_ip] = failures
            else:
                FAILED_PASSWORD_TIMES.pop(client_ip, None)
            if len(failures) >= 5:
                return _generic_error(self)
            if not configured_password or not hmac.compare_digest(password, configured_password):
                FAILED_PASSWORD_TIMES[client_ip] = failures + [now]
                return _generic_error(self)

            plans = _load_plans()
            plan = plans.get(str(data.get("plan_id", "")))
            if not plan:
                return _generic_error(self)

            if str(data.get("consent", "")).lower() != "true":
                return _generic_error(self)

            required = ("recipient_first_name", "recipient_last_name", "recipient_email", "plan_id", "board_member_name")
            if any(not str(data.get(field, "")).strip() for field in required):
                return _generic_error(self)
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", str(data["recipient_email"])):
                return _generic_error(self)

            quantity = str(data.get("addon_quantity", "1"))
            if plan["plan_id"] == "family-add-on":
                if not quantity.isdigit() or int(quantity) < 1:
                    return _generic_error(self)
            else:
                data["addon_quantity"] = "1"

            now = time.time()
            SEND_TIMES[:] = [stamp for stamp in SEND_TIMES if now - stamp < 3600]
            if len(SEND_TIMES) >= 10:
                return _generic_error(self)
            SEND_TIMES.append(now)

            gmail_address = os.environ.get("GMAIL_ADDRESS", "").strip()
            gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
            if not gmail_address or not gmail_app_password:
                return _generic_error(self, 500)

            email_message = build_email(data, plan)
            email_message["From"] = formataddr(("BEMA Health", gmail_address))
            email_message["To"] = data["recipient_email"]
            email_message["Reply-To"] = SUPPORT_EMAIL
            email_message["Subject"] = plan["plan_name"]

            # Do not add donation language. This email is not a solicitation.
            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(gmail_address, gmail_app_password)
                smtp.sendmail(gmail_address, [data["recipient_email"], SUPPORT_EMAIL], email_message.as_string())
        except Exception:
            return _generic_error(self, 500)

        _send_json(self, 200, {"success": True})
