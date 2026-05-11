import html
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from http.server import BaseHTTPRequestHandler


FIELD_LABELS = {
    "name": "Name",
    "email": "Email",
    "phone": "Phone",
    "zip_code": "ZIP Code",
    "who_for": "Who is this for",
    "total_count": "How many total",
    "preferred_contact": "Preferred method of contact",
    "message": "Message",
    "contact_name": "Contact Name",
    "business_name": "Business Name",
    "employee_count": "Number of Employees",
    "work_arrangement": "Work Arrangement",
}


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        response = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def _field_row(self, label, value):
        safe_label = html.escape(label)
        safe_value = html.escape(str(value)).replace("\n", "<br>")

        return f"""
            <div style="font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; color: #B5A080;">{safe_label}</div>
            <div style="font-size: 15px; color: #2C3D2F; margin-bottom: 20px;">{safe_value}</div>
        """

    def _build_html_email(self, subheading, rows):
        field_rows = "".join(self._field_row(label, value) for label, value in rows)

        return f"""
        <div style="background-color: #F2F0E8; padding: 32px; font-family: Arial, sans-serif;">
          <div style="background-color: #2C3D2F; padding: 24px; color: #F2F0E8;">
            <div style="font-size: 22px; font-weight: bold;">BEMA Health</div>
            <div style="font-size: 14px; color: #B5A080; margin-top: 6px;">{html.escape(subheading)}</div>
          </div>

          <div style="background-color: #FFFFFF; border-radius: 6px; padding: 32px; margin-top: 16px;">
            {field_rows}
          </div>

          <div style="margin-top: 24px; font-size: 12px; color: #B5A080; text-align: center;">
            This message was submitted through the BEMA Health get started form at bemahealth.org.
          </div>
        </div>
        """

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(raw_body or "{}")
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"success": False, "message": "Invalid JSON request body."})
            return

        form_type = str(data.get("form_type", "")).strip()

        if form_type not in ["individual", "employer"]:
            self._send_json(400, {"success": False, "message": "Invalid form type."})
            return

        required_fields = (
            ["name", "email", "who_for", "preferred_contact"]
            if form_type == "individual"
            else ["contact_name", "business_name", "email", "employee_count", "work_arrangement", "preferred_contact"]
        )
        missing_fields = [field for field in required_fields if not str(data.get(field, "")).strip()]

        if missing_fields:
            missing = ", ".join(FIELD_LABELS.get(field, field) for field in missing_fields)
            self._send_json(400, {"success": False, "message": f"Missing required field(s): {missing}."})
            return

        gmail_address = os.environ.get("GMAIL_ADDRESS", "").strip()
        gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
        recipient_email = os.environ.get("RECIPIENT_EMAIL", "").strip()

        if not gmail_address or not gmail_app_password or not recipient_email:
            self._send_json(
                500,
                {
                    "success": False,
                    "message": "Email service is not configured.",
                },
            )
            return

        if form_type == "individual":
            subject = "New BEMA Get Started Submission: Individual Membership Inquiry"
            subheading = "Individual Membership Inquiry"
            rows = [
                ("Name", data.get("name", "")),
                ("Email", data.get("email", "")),
                ("Phone", data.get("phone") or "Not provided"),
                ("ZIP Code", data.get("zip_code") or "Not provided"),
                ("Who is this for", data.get("who_for", "")),
                ("How many total", data.get("total_count") or "Not applicable"),
                ("Preferred method of contact", data.get("preferred_contact", "")),
                ("Message", data.get("message") or "Not provided"),
            ]
        else:
            subject = "New BEMA Get Started Submission: Employer Group Inquiry"
            subheading = "Employer Group Inquiry"
            rows = [
                ("Contact Name", data.get("contact_name", "")),
                ("Business Name", data.get("business_name", "")),
                ("Email", data.get("email", "")),
                ("Phone", data.get("phone") or "Not provided"),
                ("Number of Employees", data.get("employee_count", "")),
                ("Work Arrangement", data.get("work_arrangement", "")),
                ("Preferred Method of Contact", data.get("preferred_contact", "")),
                ("Message", data.get("message") or "Not provided"),
            ]

        email_message = MIMEMultipart("alternative")
        email_message["From"] = formataddr(("BEMA Health", gmail_address))
        email_message["To"] = recipient_email
        email_message["Reply-To"] = str(data.get("email", "")).strip()
        email_message["Subject"] = subject
        email_message.attach(MIMEText(self._build_html_email(subheading, rows), "html"))

        try:
            # To transition to BEMA email accounts, update GMAIL_ADDRESS to the new sending address, regenerate GMAIL_APP_PASSWORD from that account, and update RECIPIENT_EMAIL to the BEMA staff recipient. No code changes required.
            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(gmail_address, gmail_app_password)
                smtp.sendmail(gmail_address, [recipient_email], email_message.as_string())
        except Exception as error:
            self._send_json(500, {"success": False, "message": str(error)})
            return

        self._send_json(200, {"success": True})
