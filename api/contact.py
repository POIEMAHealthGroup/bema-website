import html
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        response = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(raw_body or "{}")
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"success": False, "message": "Invalid JSON request body."})
            return

        fields = {
            "name": str(data.get("name", "")).strip(),
            "email": str(data.get("email", "")).strip(),
            "phone": str(data.get("phone", "")).strip(),
            "subject": str(data.get("subject", "")).strip(),
            "message": str(data.get("message", "")).strip(),
        }

        required_fields = ["name", "email", "subject", "message"]
        missing_fields = [field for field in required_fields if not fields[field]]

        if missing_fields:
            missing = ", ".join(missing_fields)
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

        escaped_fields = {key: html.escape(value) for key, value in fields.items()}
        phone_value = escaped_fields["phone"] or "Not provided"
        message_value = escaped_fields["message"].replace("\n", "<br>")

        html_body = f"""
        <div style="background-color: #F2F0E8; padding: 32px; font-family: Arial, sans-serif;">
          <div style="background-color: #2C3D2F; padding: 24px; color: #F2F0E8;">
            <div style="font-size: 22px; font-weight: bold;">BEMA Health</div>
            <div style="font-size: 14px; color: #B5A080; margin-top: 6px;">New Contact Form Submission</div>
          </div>

          <div style="background-color: #FFFFFF; border-radius: 6px; padding: 32px; margin-top: 16px;">
            <div style="font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; color: #B5A080;">Name</div>
            <div style="font-size: 15px; color: #2C3D2F; margin-bottom: 20px;">{escaped_fields["name"]}</div>

            <div style="font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; color: #B5A080;">Email</div>
            <div style="font-size: 15px; color: #2C3D2F; margin-bottom: 20px;">{escaped_fields["email"]}</div>

            <div style="font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; color: #B5A080;">Phone</div>
            <div style="font-size: 15px; color: #2C3D2F; margin-bottom: 20px;">{phone_value}</div>

            <div style="font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; color: #B5A080;">Subject</div>
            <div style="font-size: 15px; color: #2C3D2F; margin-bottom: 20px;">{escaped_fields["subject"]}</div>

            <div style="font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; color: #B5A080;">Message</div>
            <div style="font-size: 15px; color: #2C3D2F; margin-bottom: 20px;">{message_value}</div>
          </div>

          <div style="margin-top: 24px; font-size: 12px; color: #B5A080; text-align: center;">
            This message was submitted through the BEMA Health contact form at bemahealth.org.
          </div>
        </div>
        """

        email_message = MIMEMultipart("alternative")
        email_message["From"] = formataddr(("BEMA Health", gmail_address))
        email_message["To"] = recipient_email
        email_message["Reply-To"] = fields["email"]
        email_message["Subject"] = f"New BEMA Contact Form Submission: {fields['subject']}"
        email_message.attach(MIMEText(html_body, "html"))

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
