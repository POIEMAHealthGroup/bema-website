import html
import hmac
import json
import os
import re
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from http.server import BaseHTTPRequestHandler
from pathlib import Path


SUPPORT_EMAIL = "support@bemahealth.org"
POSTAL_ADDRESS = ""
SEND_TIMES = []
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
    source_path = Path(__file__).resolve().parents[1] / "src" / "data" / "plans.ts"
    source = source_path.read_text(encoding="utf-8")
    plans = {}
    for block in re.findall(r"\{([^{}]*)\}", source, re.DOTALL):
        values = dict(re.findall(r'^\s*([a-z_]+):\s*"([^"]*)",?\s*$', block, re.MULTILINE))
        if values.get("plan_id"):
            plans[values["plan_id"]] = values
    return plans


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


def _build_email(data, plan):
    first_name = html.escape(data["recipient_first_name"])
    last_name = html.escape(data["recipient_last_name"])
    full_name = f"{first_name} {last_name}"
    plan_name = html.escape(plan["plan_name"])
    fee = html.escape(plan["program_service_fee"])
    interval = html.escape(plan["billing_interval"])
    checkout_url = plan["stripe_url"]
    quantity = int(data.get("addon_quantity") or "1")

    lines = [
        f"Hello {data['recipient_first_name']},",
        "",
        "BEMA Health Incorporated is a Florida nonprofit that coordinates access to care.",
        "",
        f"Plan: {plan['plan_name']}",
        f"Program service fee: {plan['program_service_fee']} per {plan['billing_interval']}",
    ]
    links = [("Continue to checkout", checkout_url)]

    if plan["plan_id"] == "family-add-on" and quantity > 1:
        lines.extend([
            "",
            f"Quantity needed: {quantity}",
            "This add-on covers each member beyond the 4 included in Family Membership.",
        ])
    elif plan["audience"] == "employer":
        lines.extend([
            "",
            "Both payments are required.",
            f"Enrollment setup fee: {plan['setup_fee_amount']} as a one time payment.",
            f"Group membership: {plan['program_service_fee']} as a recurring monthly payment.",
        ])
        links = [
            ("Continue to enrollment setup", plan["setup_fee_url"]),
            ("Continue to group membership", checkout_url),
        ]

    lines.extend([
        "",
        "Reply to support@bemahealth.org with questions.",
        "Please do not include health information in any reply.",
    ])
    if POSTAL_ADDRESS:
        lines.extend(["", POSTAL_ADDRESS])

    link_html = "".join(
        f'<p><a href="{html.escape(url, quote=True)}">{html.escape(label)}</a></p>'
        for label, url in links
    )
    extra_html = ""
    if plan["plan_id"] == "family-add-on" and quantity > 1:
        extra_html = f"<p>Quantity needed: {quantity}</p><p>This add-on covers each member beyond the 4 included in Family Membership.</p>"
    elif plan["audience"] == "employer":
        extra_html = (
            f"<p><strong>Both payments are required.</strong></p>"
            f"<p>Enrollment setup fee: {html.escape(plan['setup_fee_amount'])} as a one time payment.</p>"
            f"<p>Group membership: {fee} as a recurring monthly payment.</p>"
        )
    postal_html = f"<p>{html.escape(POSTAL_ADDRESS)}</p>" if POSTAL_ADDRESS else ""
    html_body = (
        f"<p>Hello {full_name},</p>"
        "<p>BEMA Health Incorporated is a Florida nonprofit that coordinates access to care.</p>"
        f"<p>Plan: <strong>{plan_name}</strong><br />Program service fee: {fee} per {interval}</p>"
        f"{extra_html}{link_html}"
        "<p>Reply to support@bemahealth.org with questions.<br />Please do not include health information in any reply.</p>"
        f"{postal_html}"
    )
    message = MIMEMultipart("alternative")
    message.attach(MIMEText("\n".join(lines), "plain"))
    message.attach(MIMEText(html_body, "html"))
    return message


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
            if not configured_password or not hmac.compare_digest(password, configured_password):
                return _generic_error(self, 401)

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
                return _generic_error(self, 429)
            SEND_TIMES.append(now)

            gmail_address = os.environ.get("GMAIL_ADDRESS", "").strip()
            gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
            if not gmail_address or not gmail_app_password:
                return _generic_error(self, 500)

            email_message = _build_email(data, plan)
            email_message["From"] = formataddr(("BEMA Health", gmail_address))
            email_message["To"] = data["recipient_email"]
            email_message["Reply-To"] = SUPPORT_EMAIL
            email_message["Bcc"] = SUPPORT_EMAIL
            email_message["Subject"] = plan["plan_name"]

            # Do not add donation language. This email is not a solicitation.
            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(gmail_address, gmail_app_password)
                smtp.sendmail(gmail_address, [data["recipient_email"], SUPPORT_EMAIL], email_message.as_string())
        except Exception:
            return _generic_error(self, 500)

        _send_json(self, 200, {"success": True})
