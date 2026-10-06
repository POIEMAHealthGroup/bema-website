import html
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


SUPPORT_EMAIL = "support@bemahealth.org"
# The address is included as a mailing address in outbound email.
POSTAL_ADDRESS = "BEMA Health Incorporated\n580 Lexington Green Lane\nSanford, FL 32771"


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
    if plan["plan_id"] == "family-add-on" and quantity > 1:
        lines.extend([
            "",
            f"Quantity needed: {quantity}",
            "This add-on covers each member beyond the 4 included in Family Membership.",
        ])
    if plan["audience"] == "employer":
        lines.extend([
            "",
            "Both payments are required.",
            f"Enrollment setup fee: {plan['setup_fee_amount']} as a one time payment.",
            "Continue to enrollment setup:",
            plan["setup_fee_url"],
            "",
            f"Group membership: {plan['program_service_fee']} as a recurring monthly payment.",
            "Continue to group membership:",
            checkout_url,
        ])
    else:
        lines.extend([
            "",
            "Continue to checkout:",
            checkout_url,
        ])
    lines.extend([
        "",
        "Reply to support@bemahealth.org with questions.",
        "Please do not include health information in any reply.",
    ])
    if POSTAL_ADDRESS:
        lines.extend(["", "Mailing address:", POSTAL_ADDRESS])

    checkout_url_html = html.escape(checkout_url, quote=True)
    quantity_html = html.escape(str(quantity))

    def button_html(label, url):
        return (
            '<table role="presentation" border="0" cellpadding="0" cellspacing="0">'
            '<tr>'
            '<td bgcolor="#2C3D2F" style="padding: 12px 20px; border-radius: 4px;">'
            f'<a href="{url}" style="display: inline-block; color: #FFFFFF; '
            f'font-family: Arial, sans-serif; font-size: 15px; font-weight: bold; '
            f'text-decoration: none;">{label}</a>'
            '</td>'
            '</tr>'
            '</table>'
        )

    payment_html = button_html("Continue to checkout", checkout_url_html)
    if plan["plan_id"] == "family-add-on" and quantity > 1:
        payment_html = (
            '<div style="font-size: 11px; font-weight: bold; text-transform: uppercase; '
            'letter-spacing: 1px; color: #B5A080;">Quantity needed:</div>'
            f'<div style="font-size: 15px; color: #2C3D2F; margin-bottom: 8px;">{quantity_html}</div>'
            '<div style="font-size: 15px; line-height: 22px; color: #2C3D2F; margin-bottom: 20px;">'
            'This add-on covers each member beyond the 4 included in Family Membership.'
            '</div>'
            f'{button_html("Continue to checkout", checkout_url_html)}'
        )
    elif plan["audience"] == "employer":
        setup_fee_amount = html.escape(plan["setup_fee_amount"])
        setup_fee_url = html.escape(plan["setup_fee_url"], quote=True)
        payment_html = (
            '<div style="font-size: 15px; line-height: 22px; color: #2C3D2F; margin-bottom: 20px;">'
            'Both payments are required.'
            '</div>'
            '<table role="presentation" width="100%" border="0" cellpadding="0" cellspacing="0" '
            'bgcolor="#F2F0E8" style="background-color: #F2F0E8;">'
            '<tr><td style="padding: 20px;">'
            '<div style="font-size: 11px; font-weight: bold; text-transform: uppercase; '
            'letter-spacing: 1px; color: #B5A080;">Enrollment setup fee:</div>'
            f'<div style="font-size: 15px; line-height: 22px; color: #2C3D2F; margin-bottom: 16px;">'
            f'{setup_fee_amount} as a one time payment.</div>'
            f'{button_html("Continue to enrollment setup", setup_fee_url)}'
            '</td></tr>'
            '</table>'
            '<table role="presentation" width="100%" border="0" cellpadding="0" cellspacing="0">'
            '<tr><td height="16" style="font-size: 0; line-height: 0;">&nbsp;</td></tr>'
            '</table>'
            '<table role="presentation" width="100%" border="0" cellpadding="0" cellspacing="0" '
            'bgcolor="#F2F0E8" style="background-color: #F2F0E8;">'
            '<tr><td style="padding: 20px;">'
            '<div style="font-size: 11px; font-weight: bold; text-transform: uppercase; '
            'letter-spacing: 1px; color: #B5A080;">Group membership:</div>'
            f'<div style="font-size: 15px; line-height: 22px; color: #2C3D2F; margin-bottom: 16px;">'
            f'{fee} as a recurring monthly payment.</div>'
            f'{button_html("Continue to group membership", checkout_url_html)}'
            '</td></tr>'
            '</table>'
        )

    postal_html = ""
    if POSTAL_ADDRESS:
        postal_address_html = html.escape(POSTAL_ADDRESS).replace("\n", "<br />")
        postal_html = (
            '<tr>'
            '<td align="center" style="padding: 24px 16px 0; font-family: Arial, sans-serif; '
            'font-size: 12px; line-height: 18px; color: #B5A080;">'
            f'Mailing address:<br />{postal_address_html}'
            '</td>'
            '</tr>'
        )

    html_body = (
        '<!doctype html>'
        '<html>'
        '<body style="margin: 0; padding: 0; background-color: #F2F0E8;">'
        '<table role="presentation" width="100%" border="0" cellpadding="0" cellspacing="0" '
        'bgcolor="#F2F0E8" style="background-color: #F2F0E8;">'
        '<tr>'
        '<td align="center" style="padding: 32px 16px;">'
        '<table role="presentation" width="600" border="0" cellpadding="0" cellspacing="0" '
        'style="width: 100%; max-width: 600px;">'
        '<tr>'
        '<td bgcolor="#2C3D2F" style="padding: 24px; background-color: #2C3D2F; '
        'font-family: Arial, sans-serif; font-size: 22px; font-weight: bold; color: #F2F0E8;">'
        'BEMA Health'
        '</td>'
        '</tr>'
        '<tr>'
        '<td style="padding-top: 16px;">'
        '<table role="presentation" width="100%" border="0" cellpadding="0" cellspacing="0" '
        'bgcolor="#FFFFFF" style="background-color: #FFFFFF; border-radius: 6px;">'
        '<tr>'
        '<td style="padding: 32px; font-family: Arial, sans-serif;">'
        f'<div style="font-size: 15px; line-height: 22px; color: #2C3D2F; margin-bottom: 20px;">'
        f'Hello {full_name},</div>'
        '<div style="font-size: 15px; line-height: 22px; color: #2C3D2F; margin-bottom: 24px;">'
        'BEMA Health Incorporated is a Florida nonprofit that coordinates access to care.'
        '</div>'
        '<div style="font-size: 11px; font-weight: bold; text-transform: uppercase; '
        'letter-spacing: 1px; color: #B5A080;">Plan:</div>'
        f'<div style="font-size: 15px; line-height: 22px; color: #2C3D2F; margin-bottom: 20px;">'
        f'{plan_name}</div>'
        '<div style="font-size: 11px; font-weight: bold; text-transform: uppercase; '
        'letter-spacing: 1px; color: #B5A080;">Program service fee:</div>'
        f'<div style="font-size: 15px; line-height: 22px; color: #2C3D2F; margin-bottom: 24px;">'
        f'{fee} per {interval}</div>'
        f'{payment_html}'
        '<div style="font-size: 15px; line-height: 22px; color: #2C3D2F; margin-top: 24px;">'
        'Reply to <a href="mailto:support@bemahealth.org" style="color: #2C3D2F;">'
        'support@bemahealth.org</a> with questions.'
        '</div>'
        '<div style="font-size: 15px; line-height: 22px; color: #2C3D2F; margin-top: 8px;">'
        'Please do not include health information in any reply.'
        '</div>'
        '</td>'
        '</tr>'
        '</table>'
        '</td>'
        '</tr>'
        f'{postal_html}'
        '</table>'
        '</td>'
        '</tr>'
        '</table>'
        '</body>'
        '</html>'
    )
    message = MIMEMultipart("alternative")
    message.attach(MIMEText("\n".join(lines), "plain"))
    message.attach(MIMEText(html_body, "html"))
    return message
