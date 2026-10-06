# Privacy policy referral addendum proposal

This is proposed copy based on the current `src/pages/privacy-policy.astro` and the implemented board referral flow. It does not change the published policy.

## Page subtitle

The current subtitle refers only to information "you provide" when visiting the site or contacting BEMA. It does not describe information a board member submits about another person.

Proposed replacement:

> This policy describes how BEMA Health Incorporated collects, uses, and protects information submitted through this site, including information a board member provides about a person who asked to receive membership information.

## Section 2. Information We Collect

The first paragraph names only the contact form and the visitor's own details. The paragraph about personal health information names only the contact form. Neither describes the internal referral form, its third party recipient details, or the data used to limit password attempts.

Proposed replacement for Section 2:

> We collect information submitted through our contact and get started forms, including the contact details and inquiry information entered in those forms. A board member may also submit a referral for a person who has asked BEMA to contact them about membership. The referral form collects that person's first and last name, email address, optional phone number, selected membership plan, and Family Membership Add-On quantity when applicable. It also collects the board member's name, a statement that the person asked to be contacted, and an access password used to validate the referral. The referral function reads the client IP address from the request header to limit failed password attempts.
>
> We do not collect Social Security Numbers through this website or through any form made available for public disclosure, in accordance with IRS guidelines for tax exempt organizations.
>
> Our forms ask users not to include personal health information. The board referral form does not ask for Mental Health details or a Partner Clinic selection. BEMA Health Incorporated coordinates access to care.
>
> We may collect standard technical data through our web hosting provider, including browser type, pages visited, and time spent on pages.

## Section 3. How We Use Your Information

The first paragraph says form information is used solely to respond to the submitter's inquiry. A board referral sends plan details to another person and a copy to the support mailbox, so that description does not cover the flow.

Proposed replacement for Section 3:

> Information submitted through our contact and get started forms is used to respond to inquiries and provide information about BEMA Health Incorporated's programs. A board referral is used to send the person named in the form an email about the selected membership plan, its program service fee, and a checkout link. For employer plans, the email also includes the enrollment setup fee and its payment link. A copy of the referral email is sent to support@bemahealth.org. The board member's access password is used to validate the submission. The referral function checks failed password timestamps against a 15 minute window and send timestamps against a one hour window. These timestamps remain in process memory until pruned by a later request or reset on a cold start. The function does not write referral records to a database or file.
>
> We do not use contact information submitted through these forms for commercial marketing purposes. We do not sell, lease, or otherwise transfer personal information to third parties for their own use. Donor information, where collected, is used solely to process contributions and communicate with donors about BEMA's mission. Donor lists are never sold or used for private gain, in accordance with IRS standards governing tax exempt organizations.

## Section 9. Children's Privacy

The current section says BEMA does not knowingly collect personal information from children. The referral form offers a Child Individual Membership plan and does not ask for the recipient's age, so it cannot verify that statement for referrals.

Proposed replacement for Section 9:

> This website is not directed at children under the age of 13. The board referral form may be used to request information about a Child Individual Membership, but it does not ask for the recipient's age. If you believe information about a child was submitted through this site, please contact us using the address in Section 11.
