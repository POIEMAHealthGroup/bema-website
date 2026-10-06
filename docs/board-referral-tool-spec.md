# Board referral tool specification

## Implementation status

The implemented route is `/board/referral`, as required by the build task. The earlier proposal named `/board/referrals`; the singular route takes precedence. The page is not linked from site navigation or page content. It emits a noindex robots tag. The sitemap excludes `/board`, and robots.txt disallows `/board`, which also covers this route.

The page uses the existing BaseLayout and submits JSON with a POST request to `/api/board-referral`. The endpoint accepts POST only and returns generic success or failure responses. It rejects URL text, unexpected fields, invalid credentials, unknown plans, missing consent, invalid required fields, and sends over the in process hourly limit without identifying which check failed.

## Access control

The endpoint checks the submitted password on the server against `BOARD_REFERRAL_PASSWORD` with a constant time comparison. The current implementation does not issue a session cookie. The password is sent with each referral request and is cleared from the form after success. A shared password keeps the page and endpoint out of casual hands and nothing more. It does not identify an individual board member, prevent a board member from sharing the password, or protect a compromised device.

## Form fields

1. Recipient first name, required text.
2. Recipient last name, required text.
3. Recipient email, required email.
4. Recipient phone, optional telephone.
5. Plan, required select. The value is a plan identifier only.
6. Add on quantity, number with a default of 1. It is shown for the family add on plan.
7. This person asked BEMA to contact them about membership, required checkbox.
8. Board member name, required text.
9. Access password, required password.

There is no notes field. No field asks for medical or health details, diagnoses, conditions, symptoms, medications, treatment history, payment card numbers, or account numbers. The page carries this existing notice exactly:

Please do not include personal health information in this form.

## Plan data and URL protection

`src/data/plans.ts` contains the seven plan records and the Stripe checkout URLs. It is not imported by an Astro page, component, or client script. Because the Python runtime cannot import TypeScript directly, the endpoint reads the TypeScript source on the server and parses the plan records. This is an implementation difference from the earlier proposal for a private CSV or JSON store and should be replaced with a shared server data format if the deployment model changes.

The page contains a duplicated URL free safe plan list because the task requires `plans.ts` to be imported only by the API handler. The page receives plan identifiers, names, audiences, program service fees, billing intervals, and notes only. Stripe URLs and setup fee URLs are not rendered or included in the form payload. The endpoint accepts a plan identifier only, maps it to the server record, and rejects URL text in every submitted value.

## Endpoint and email

`api/board-referral.py` follows the existing Python smtplib pattern. It reads `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`, and `BOARD_REFERRAL_PASSWORD` by name only. It sends through `smtp.gmail.com` on port 587 with STARTTLS, from BEMA Health using `GMAIL_ADDRESS`, to the recipient, with Reply To and Bcc set to `support@bemahealth.org`. It does not log passwords, recipient details, request bodies, or message content.

The plain text and HTML templates live in `api/_board_referral_email.py`. The message identifies BEMA Health Incorporated as a Florida nonprofit that coordinates access to care, names the plan, fee, and interval, and supplies the server selected checkout links. Family add on quantity is stated when it is above 1. Employer messages separate the enrollment setup fee and recurring group membership payment and state that both payments are required. The message gives `support@bemahealth.org` as the reply address and asks the recipient not to include health information in a reply.

The templates contain no donation request, donation link, or fundraising language. This is intentional because adding a solicitation would trigger the FDACS disclosure requirement.

The empty `POSTAL_ADDRESS` constant is in the email template module. Whether a postal address is required in outbound email is an open legal question.

## Rate limiting

The endpoint permits at most 10 sends in one hour using an in process counter. The counter resets on a cold start and is a soft control only. It is not shared across server instances and should be replaced with a shared rate limit store before relying on it for abuse prevention.

## Privacy policy considerations

The privacy policy should explain that a board member enters information about another person, including the recipient name, email, and optional phone. It should explain the confirmation statement, the use of the information to send the requested plan link, the server side plan mapping, the email and hosting processors, retention, access restriction, and the support contact. It should state that the form must not contain health information or payment details. It should not imply that the confirmation proves legal consent or that the email channel is perfectly secure.

## Environment setup

Set `BOARD_REFERRAL_PASSWORD` in the Vercel project under Project Settings and Environment Variables. Set it for each environment where the tool is enabled, keep it out of source control, and rotate it through the same controlled process used for other operational secrets. A shared password among board members is a weak control that keeps the page out of casual hands and nothing more.

## Open questions for David

1. What is the SPF status for `bemahealth.org`?
2. What is the DKIM status for `bemahealth.org`?
3. What is the DMARC status and enforcement policy for `bemahealth.org`?
4. Must a postal address appear in outbound email?
5. How will the shared password be distributed to board members?
6. How often will the shared password be rotated, and who can rotate it?
7. Is a free text notes field wanted despite the risk that someone could enter health information?
8. What rate limits and retention period are approved?
9. Which plan records are approved for launch, and who controls the active state?
