import html
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


SUPPORT_EMAIL = "support@bemahealth.org"
# Whether a postal address is required in outbound email is an open legal question.
POSTAL_ADDRESS = ""


def build_email(data, plan):
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
