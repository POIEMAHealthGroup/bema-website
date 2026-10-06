# Board referral flow as built

This document describes the behavior in `src/pages/board/referral.astro`, `api/board-referral.py`, `api/_board_referral_email.py`, and `src/data/plans.json`.

## Board member steps

1. The board member opens `/board/referral`. The page has a noindex tag and is excluded from the sitemap. `robots.txt` disallows `/board`.
2. The board member enters the recipient's first name, last name, email address, and optional phone number.
3. The board member selects one plan. If the selected plan is Family Membership Add-On, the page shows an add-on quantity input with a default of `1` and a minimum of `1`. The input stays in the form data when hidden.
4. The board member checks the statement that the person asked BEMA to contact them about membership, enters the board member name and access password, and selects Send Referral. The page asks the board member not to include personal health information. It does not ask for Mental Health details or a Partner Clinic selection.
5. Browser script prevents normal form submission and sends the form fields as JSON in a POST request to `/api/board-referral`. On success, it hides the form, displays a success message, and clears the password input. On failure, it displays one generic error message and enables the button again.

## Fields sent to the function

| Field | Browser control | Function check |
| --- | --- | --- |
| `recipient_first_name` | Required text | Nonempty after converting to text and trimming whitespace |
| `recipient_last_name` | Required text | Nonempty after converting to text and trimming whitespace |
| `recipient_email` | Required email | Nonempty and matches the function's basic email pattern |
| `recipient_phone` | Optional telephone | Must be present as a field, but may be empty |
| `plan_id` | Required selection | Must map to a record in `src/data/plans.json` |
| `addon_quantity` | Number, default `1`, minimum `1`, shown for the add-on plan | For Family Membership Add-On, digits only and at least `1`. No maximum. For other plans, the function sets it to `1` |
| `consent` | Required checkbox with value `true` | Text value must equal `true`, ignoring case |
| `board_member_name` | Required text | Nonempty after converting to text and trimming whitespace |
| `password` | Required password input | Compared with `BOARD_REFERRAL_PASSWORD` using `hmac.compare_digest` |

The function requires exactly these nine JSON keys. It rejects URL markers `http`, `://`, or `www.` anywhere in the serialized JSON, including field names and values. The page's form controls also apply browser validation before the script runs.

## Data movement and storage

The browser sends the JSON payload to the Vercel Python function. The function reads plan data from the repository JSON file and selects the plan name, program service fee, billing interval, and checkout URL. Employer plans also provide a setup fee and setup URL. It builds plain text and HTML email parts. It sends the message through `smtp.gmail.com` on port `587` with STARTTLS, authenticating with `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD`. The code does not hard code `systems@bemahealth.org`; that address applies only if `GMAIL_ADDRESS` is configured with it.

The email `From` address uses `GMAIL_ADDRESS`. The `To` header and SMTP envelope include the recipient email. The `Reply-To` header is `support@bemahealth.org`, and the SMTP envelope also sends a copy to `support@bemahealth.org`. The code does not add a Bcc header.

The function has no database or file write for referrals. It holds recent send timestamps and failed password timestamps by client IP in process memory. Both counters reset on a cold start. The failed password counter uses the first address in `x-forwarded-for`; if that header is absent, it uses an empty key. The browser keeps form values during a failed attempt. The code does not log the request payload. Email delivery and retention after SMTP submission are outside this repository's code.

The recipient gets the selected plan name, program service fee, billing interval, and server selected checkout URL. A Family Membership Add-On quantity above `1` is stated in both email parts, but the checkout URL does not vary with quantity. An employer plan email states that both payments are required and includes its setup fee link and recurring group membership link. The message includes the support reply address, a request not to include health information in a reply, and BEMA's mailing address. It does not include the board member name, recipient phone, consent value, or access password.

## Rejection and response paths

| Condition | HTTP response |
| --- | --- |
| GET, PUT, DELETE, or PATCH | `405` with the generic error body |
| JSON is not an object, contains a URL marker, or has missing or extra keys | `400` with the generic error body |
| Five failed passwords from the same client IP within 15 minutes | `400` with the generic error body for further attempts during that window |
| Password is wrong or `BOARD_REFERRAL_PASSWORD` is unset | `400` with the generic error body. Each attempt is added to the failure counter |
| Plan ID is unknown | `400` with the generic error body |
| Consent is missing or is not `true` | `400` with the generic error body |
| A required field is empty or recipient email fails the pattern | `400` with the generic error body |
| Family add-on quantity is not digits or is less than `1` | `400` with the generic error body |
| Ten sends are already recorded in the past hour | `400` with the generic error body |
| Gmail settings are missing, JSON parsing fails, email creation fails, or SMTP raises an exception | `500` with the generic error body |
| Message is submitted to SMTP without an exception | `200` with `{"success": true}` |

The generic error body is `{"success": false, "message": "Unable to process referral."}`. The hourly send counter is updated before the function checks Gmail settings or attempts SMTP delivery.
