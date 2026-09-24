# Board referral tool specification

## Purpose

This document specifies an internal tool for a BEMA board member to refer a prospective member. The board member enters contact information, selects a plan, confirms that the person asked to be contacted, and submits the referral. The server maps the selected plan identifier to a server side checkout link and emails the prospective member.

This is a specification only. It does not create a route, endpoint, form, data file, Stripe integration, or environment variable.

## Route and discoverability

1. Proposed route: `/board/referrals`.
2. The route is internal and must be excluded from header navigation and footer navigation.
3. The route must be excluded from the sitemap.
4. The route must be disallowed in robots.txt.
5. The page must emit a `noindex` robots meta tag.
6. Direct knowledge of the route must not be treated as access control. The server must authenticate every page request and every form request.

The route should use the existing document layout and the existing noindex prop pattern. The implementation must not modify the existing robots file unless that change is separately approved.

## Access control and session handling

1. Store the shared password in an environment variable named `BOARD_REFERRAL_PASSWORD`. The value must never be placed in source code, the client bundle, HTML, logs, email, analytics parameters, or the URL.
2. Check the password on the server. Compare a submitted password with the environment value using a constant time comparison.
3. Do not check the password in browser JavaScript. The browser may submit the password only over HTTPS to the server.
4. After successful authentication, issue a short lived, signed, encrypted, or otherwise integrity protected session cookie. The cookie must be `HttpOnly`, `Secure` in production, `SameSite=Lax` or stricter, and scoped to the board referral route.
5. Store only a session identifier or signed session state in the cookie. Do not store the password, plan checkout link, prospective member message, or contact details in the cookie.
6. Expire the session after a short period of inactivity and provide a server side logout action that clears the cookie.
7. Apply the same authentication check to the page and the referral endpoint. Reject unauthenticated requests before loading plan data or sending email.

This protects against casual public access, search discovery, and unauthenticated use of the referral endpoint. It does not protect against a board member sharing the password, an authenticated user misusing the tool, a compromised device, email account compromise, network level attacks when HTTPS is absent, or incorrect access decisions by an administrator. It also does not prove that the prospective member agreed to receive a message. The required confirmation checkbox provides an attestation, not independent proof.

## Form fields

The form should contain these fields:

1. Board member name. Required text.
2. Board member email. Required email.
3. Prospective member name. Required text.
4. Prospective member email. Required email.
5. Prospective member phone. Optional telephone.
6. Plan. Required select whose submitted value is a `plan_id`, never a URL.
7. Contact confirmation. Required checkbox with wording that confirms the prospective member asked to be contacted by BEMA.
8. Shared password. Required password field on the authentication screen, not part of the referral payload.

Do not add a notes field without explicit approval. If a notes field is later approved, it must not request or invite medical or health details, diagnoses, conditions, symptoms, medications, treatment history, payment card numbers, or account numbers. The form should display the site's existing notice wording before submission:

Please do not include personal health information in this form.

The confirmation checkbox is a required control. A referral must not be sent unless it is checked. The server must repeat this validation instead of relying only on browser validation.

## Plan data

The plan record must match these CSV columns exactly:

`plan_id`

`plan_name`

`audience`

`program_service_fee`

`billing_interval`

`includes`

`stripe_url`

`active`

Plan data should live in a private server side data file or a server side data store that is not imported by browser code. A private CSV or JSON file outside the public directory is acceptable if the deployment reliably includes it. A server environment secret or managed data store is preferable for the checkout link and active state.

The browser may receive only the active plan identifiers, names, audience values, program service fee display values, billing intervals, and safe inclusion summaries needed to render the select. The browser must never receive `stripe_url`. The form payload must contain only `plan_id` for plan identity.

The server must map `plan_id` to `stripe_url` after authentication and after validating that the plan is active. If the identifier is unknown or inactive, reject the request and send no email.

## Critical plan identity constraint

The form submits a `plan_id` only. The server maps `plan_id` to `stripe_url`.

The endpoint must reject any request containing a URL in any field. Reject values containing `http://`, `https://`, `www.`, or `://`, including URL like text in names, email fields, the plan identifier, and any future free text field. Validate both the parsed fields and the raw request object before sending mail. Do not accept a client supplied checkout URL, redirect URL, success URL, cancel URL, or return URL.

The server should also reject unexpected fields. This prevents a client from smuggling a link or an unreviewed value into the outbound message.

## Endpoint design

Proposed endpoint: `/api/board-referral`.

Follow the existing Python `smtplib` pattern in `api/`. The endpoint should:

1. Accept a JSON POST only.
2. Require an authenticated session.
3. Parse and validate the exact allowed fields.
4. Require the confirmation checkbox to be true.
5. Reject URLs in every field.
6. Map `plan_id` to the private plan record.
7. Confirm that the selected plan is active.
8. Construct the checkout link on the server.
9. Send an email to the prospective member.
10. Send from `GMAIL_ADDRESS`.
11. Set `Reply-To` to `support@bemahealth.org`.
12. Set `Bcc` to `support@bemahealth.org` for the audit trail.
13. Return a generic success or error response without exposing SMTP errors, credentials, plan data, or the checkout URL to an unauthenticated caller.

The current SMTP transport pattern uses `smtp.gmail.com` on port 587 with STARTTLS and credentials named `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD`. The proposed endpoint should follow that existing pattern. It must not log passwords, raw request bodies, contact details, or complete email content.

## Rate limiting and abuse controls

Because the endpoint sends messages to external recipients, apply several controls:

1. Limit authentication attempts per IP and per time window.
2. Limit referral sends per authenticated session, board member email, prospective member email, and source IP.
3. Apply a daily and hourly service wide ceiling.
4. Return the same generic failure response for rate limit, authentication, and validation failures where revealing the reason would help abuse.
5. Do not send a message when a limit is exceeded.
6. Record only minimal operational telemetry such as a one way identifier, timestamp, result category, and rate limit bucket. Do not record the request body or credentials.
7. Use a shared server side counter or managed rate limit store in production. An in memory counter is not sufficient across multiple server instances.
8. Add an email address normalization and duplicate suppression policy so repeated referrals do not create a mail flood.

The exact limits, retention, and alerting thresholds require operational approval before implementation.

## Draft outbound email

The email must contain no donation request. It must identify BEMA Health Incorporated, name the selected plan, provide the server selected checkout link, and identify `support@bemahealth.org` as the reply address.

### Plain text

Subject: Your BEMA plan link

Hello [Prospective member name],

BEMA Health Incorporated coordinates access to care for working individuals and families in Florida.

The plan selected for you is: [Plan name]

You can review the plan and continue to checkout here:
[Checkout link]

Questions about the plan or the next step can be sent to support@bemahealth.org.

Postal address: [Postal address to be supplied if required]

Whether a postal address is required in this email is an open question for David.

Thank you,

BEMA Health Incorporated

### HTML

```html
<p>Hello [Prospective member name],</p>
<p>BEMA Health Incorporated coordinates access to care for working individuals and families in Florida.</p>
<p>The plan selected for you is: <strong>[Plan name]</strong></p>
<p><a href="[Server selected checkout link]">Review the plan and continue to checkout</a></p>
<p>Questions about the plan or the next step can be sent to support@bemahealth.org.</p>
<p>Postal address: [Postal address to be supplied if required]</p>
<p>Whether a postal address is required in this email is an open question for David.</p>
<p>Thank you,<br />BEMA Health Incorporated</p>
```

The HTML link must be generated only after the server maps the submitted `plan_id`. Do not interpolate a client supplied URL.

## Privacy policy requirements

The privacy policy must explain that the tool can collect information about a prospective member from a board member who submits a referral. It should distinguish the board member from the person whose name and contact information are entered.

The policy should state:

1. What board member information is collected.
2. What prospective member information is collected.
3. That the board member confirms the prospective member asked to be contacted.
4. That BEMA uses the information to send the requested plan link and respond to support questions.
5. That the selected plan identifier is used server side to choose the checkout link.
6. That the checkout link is not supplied by the browser or stored in the form payload.
7. Which email and hosting providers process the referral.
8. How long referral records and audit copies are retained.
9. How access is restricted and how the shared password is handled.
10. How a prospective member can contact BEMA about their information.
11. That the form must not contain medical or health information or payment details.

The policy must not imply that the board member's confirmation proves legal consent, that the tool is HIPAA compliant, or that the email channel is perfectly secure. Legal review is required before publication.

## Open questions for David

1. What is the current SPF status for `bemahealth.org`?
2. What is the current DKIM status for `bemahealth.org`?
3. What is the current DMARC status and enforcement policy for `bemahealth.org`?
4. Must a postal address appear in the outbound email?
5. How will the shared password be distributed to board members?
6. How often will the shared password be rotated, and who can rotate it?
7. Is a free text notes field wanted despite the risk that someone could enter health information?
8. What are the approved rate limits and retention period?
9. Should the board member receive a success receipt, and if so, should that receipt contain any prospective member details?
10. Which plan records are approved for launch, and who controls the active flag?
11. What is the approved checkout integration or Stripe link for each plan?
