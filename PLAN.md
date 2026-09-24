# Maintenance recovery plan

## Status and execution gate

Audit completed on 2026 September 20. C1 through C4 completed on 2026 September 24. This file is the source of truth for resuming work. Existing untracked implementation files were preserved until their approved task was completed.

Current branch: `overnight-maintenance`.

Current HEAD before C5: `32f84eb`.

Main baseline: `be96937d9d454b839876397ae95b084f9fcab934`.

Separate privacy draft: `f70beecead669f5d8bdd0210a94004de08aebbb7`. Its policy is not present on this maintenance branch. Do not merge it without separate approval.

Starting recovery status, verified by running it:

```text
On branch overnight-maintenance
Untracked files:
  (use "git add <file>..." to include in what will be committed)

        src/components/Sections/AnswerBlock.astro
        src/pages/answer-block-test/

nothing added to commit but untracked files present (use "git add" to track)
```

`git diff` was empty. Untracked files do not appear in that diff. `git log --stat -20` and the branch diff were inspected. No tracked deletion was present.

## Original intent and constraints

The original overnight request is the task specification. README.md and CONTRIBUTING.md provide repository conventions but README.md:28 is stale about form handlers. No existing PLAN, TODO, task notes, docs directory, or applicable AGENTS.md was found. Contributor documents, content metadata, and relevant source were inspected.

Finish T1 through T9, not the earlier broader donation and purchase implementation. T8 and T9 are documents only. T6 must remain unused by production pages. No push or merge. No commits on main or privacy-policy-draft. Stage explicit paths only. Preserve existing member facing copy except the exact original task authorizations. No dependency changes without separate approval. Do not modify analytics code, robots.txt.ts, astro.config.mjs, api handlers, or environment configuration. Do not inspect secrets or Stripe.

New proposed copy must use no dash punctuation, describe BEMA as coordinating access to care, remain Florida specific, and avoid describing its own offering with insurance terminology. Keep contrastive statements that BEMA is not insurance. Use program service fee, Find a Partner Clinic, and Mental Health where relevant. Do not request health or payment details or make HIPAA assertions.

After approval, each checklist item receives its own small commit, an updated checklist entry, and recorded verification. Retain original task numbers in messages where applicable. Stop and ask if implementation is blocked or ambiguous. Do not remove unrelated user changes.

## Project map

| Area | Responsibility |
| --- | --- |
| src/pages | Static routes, forms, reserved routes, and temporary test route |
| src/layouts | Base document and blog article presentation |
| src/components/Global | Header, footer, navigation |
| src/components/Sections | Hero, PageHeader, team, recent posts, unfinished AnswerBlock |
| src/components/UI | SEO metadata, Button, Card, ImagePlaceholder |
| src/content | Blog and team Markdown, site information, collection schema |
| src/utils | Date helpers and new intrinsic image dimension map |
| src/assets/styles | Global Tailwind styles and current Google Fonts import |
| public | Images and other static assets |
| api | Existing Python SMTP form handlers, protected from edits |
| docs | Not yet created; intended location of T8, T9, and final report |

## Every maintenance file changed

Verified by running Git comparisons against main. M means modified, A means added. Temporary work is separately listed.

| File | Status | Task |
| --- | --- | --- |
| src/pages/contact.astro | M | T1 |
| src/pages/get-started.astro | M | T1 |
| src/components/Sections/HeroSection.astro | M | T2 |
| src/components/Sections/PageHeader.astro | M | T2 |
| src/components/Sections/RecentBlogPosts.astro | M | T2 |
| src/components/UI/Card.astro | M | T2 |
| src/layouts/PostLayout.astro | M | T2 |
| src/pages/about.astro | M | T2 |
| src/pages/blog/index.astro | M | T2 |
| src/pages/employers.astro | M | T2 |
| src/pages/index.astro | M | T2 |
| src/pages/providers.astro | M | T2 |
| src/pages/services.astro | M | T2 |
| src/utils/imageDimensions.ts | A | T2 |
| src/components/UI/Seo.astro | M | T3 and T4 |
| src/layouts/BaseLayout.astro | M | T4 prop plumbing only |
| src/pages/events/index.astro | M | T4 |
| src/pages/giving.astro | M | T4 |
| src/pages/sermons/index.astro | M | T4 |
| src/pages/terms.astro | M | T5 |
| src/components/Sections/AnswerBlock.astro | Untracked | T6 partial |
| src/pages/answer-block-test/[mode].astro | Untracked | T6 temporary fixture |
| PLAN.md | New in this audit | Recovery checkpoint |

## Completed and verified working

All items in this section are verified by running the build and targeted assertions against its output, except where explicitly marked inferred from reading.

| Task | Commit | Verified result |
| --- | --- | --- |
| T1 | 469c81f | All three forms render method post. The branch diff changes only their method attributes. |
| T2 | 5f02920 | All 29 rendered images have dimensions matching actual disk image metadata, including the 26 previously missing dimensions. |
| T3 | 3cdeb99 | Three Article blocks have titles without the site suffix, POIEMA Health Group as author, publication date from frontmatter, and corrected publisher name. |
| T4 | c2e99b0 | Reserved Events, Giving, Sermons pages render noindex. No active production page does. Temporary test pages also intentionally render noindex. |
| T5 | 0967e87 | All 13 numbered labels are H2 elements. A source comparison proves all other Terms content is unchanged. |

Inferred from reading: Contact still calls preventDefault and posts JSON to /api/contact at src/pages/contact.astro:97 and :111. Get Started still does the same for /api/get-started at src/pages/get-started.astro:388, :412, and :417. Live email delivery was not tested.

Verified by running comparisons: analytics block, api/contact.py, api/get-started.py, astro.config.mjs, src/pages/robots.txt.ts, package.json, and package-lock.json are unchanged from main. Main and the privacy draft retain their original commit IDs.

## Verification results

| Check run during recovery | Result and limits |
| --- | --- |
| npm run build | PASS, 19 pages, 1.76 seconds. Includes three temporary test pages. |
| npm test -- --run | Unavailable: no test script. No established test suite found. |
| npm run lint | Unavailable: no lint script. |
| npm run typecheck | Unavailable: no typecheck script. |
| npm run check | Unavailable: no check script. |
| Installed TypeScript with --noEmit --incremental false | PASS. File listing confirms it does not typecheck Astro templates. |
| Parent workspace ESLint on src | Exit 0, but not meaningful Astro validation. It inherits a Next.js configuration. |
| Parent workspace ESLint explicitly on AnswerBlock.astro and Seo.astro | FAIL, two parser errors. The inherited parser does not understand Astro syntax. Not evidence that Astro compilation fails. |
| Astro specific type checker | Unavailable: @astrojs/check is not installed. No installation attempted. |
| Targeted generated output assertions | PASS: three form methods, 29 image dimensions, three article schemas, reserved noindex scope, unchanged Terms text, protected sources. |
| Temporary AnswerBlock render assertions | PASS for faq, speakable, none; question heading, 47 word paragraph, three list items, JSON parsing, exact FAQ visible text match, Speakable selector, and no extra schema in none mode. |
| git diff --check | PASS. |

Build warnings: reserved Events and Sermons collections are empty; Browserslist data is old. No dependency upgrade was attempted. No browser layout, accessibility interaction, real SMTP delivery, or production analytics verification was performed. Do not call those checks passed.

## Partial work, risks, and inconsistencies

1. Verified by running it: T6 builds three temporary routes and includes them in sitemap-0.xml. The fixture at src/pages/answer-block-test/[mode].astro:4 must be removed after testing and before committing T6. Expected final HTML page count is 16, not 19.
2. Inferred from reading: AnswerBlock.astro:24 enforces answer length and :27 enforces item count. Invalid input boundaries and escaping still need explicit regression cases. Line 64 reserves a minimum height but does not prove zero CLS with changing font metrics. Its fixed ID requires one instance per page.
3. Inferred from reading: Seo.astro:32 couples metadata lookup to /blog and line 41 splits raw Markdown on delimiter text. This is brittle for future content formats. Line 72 treats every author as an Organization. That matches all three current author values but not a future individual author.
4. Inferred from reading: src/content/config.ts:61 requires pubDate and :63 defaults author. Seo avoids emitting a default author by checking raw frontmatter, but an absent date currently fails collection validation before Seo can omit it. The original omitted date requirement is not supported end to end. Changing that schema exceeds T3's original Seo only scope.
5. Inferred from reading: imageDimensions.ts:2 is a manual map. Replacing an image or adding a new path can make dimensions stale or absent. Current files pass, but future additions need validation.
6. Verified by running it: the temporary routes are in the sitemap despite noindex. Inferred from reading: robots.txt.ts:11 through :13 still disallow the reserved routes, so noindex discovery by crawlers is not established. Changing robots remains prohibited.
7. Inferred from reading: method post prevents the former GET fallback but action remains #. Without JavaScript, a request goes to the static page rather than the JSON API. T1 did not promise functional fallback delivery.
8. Inferred from reading: global.css:1 still has the Google Fonts CSS import. T7 has not started. Browser font timing and appearance comparisons remain necessary.
9. Verified by running Git: the privacy draft is separate. Inferred from reading: this branch retains old privacy assertions at privacy-policy.astro:28, :31, :33, :40, an age threshold at :44, and a placeholder contact at :49. Do not copy the previous audit's draft policy metadata into T8. Do not silently merge or rewrite legal copy.
10. Inferred from reading: README.md:28 incorrectly implies no handler exists. HeroSection.astro:19 and :33 put placeholder text in the active hero alt attribute. Header.astro:13 and Footer.astro:25 retain operational TODO comments. Footer registration is not populated.
11. Inferred from reading: reserved routes intentionally retain placeholder copy and empty getStaticPaths functions. Team Markdown files retain unused profile body and image fallback placeholders. siteInfo/site.md:11 and :12 retain future social placeholders. Terms.astro:48 and privacy-policy.astro:49 have placeholder contact text. CODE_OF_CONDUCT.md retains its conduct contact placeholder. Blog and team filenames still contain placeholder even where their visible content is populated.
12. Verified by running the scan: no empty tracked files. No explicit FIXME, mock function, or commented implementation block was identified; reserved route stubs and descriptive comments remain. Existing hardcoded values include analytics IDs, image dimensions, contact details, legal assertions, footer year, and host fallbacks. None was silently replaced.

## Prioritized remaining checklist

### 1. Finish and contain T6

- [x] Size: medium. C1 removed the temporary fixture and C2 committed the unused component.
- Files: src/components/Sections/AnswerBlock.astro; src/pages/answer-block-test/[mode].astro; PLAN.md; optionally a reusable verification script under scripts.
- Add verification for answer boundaries 39, 40, 60, 61 words; item counts 2, 3, 5, 6; both headings; both list types; all schema modes; plain text escaping and script closing text; invalid options; paragraph and schema text parity.
- Verify responsive display and opening sentence emphasis in a browser. Record font related CLS limits rather than claiming an unmeasured guarantee. Keep rendering static with no client loading or height animation.
- Remove only the temporary test source created for T6 after its checks. Rebuild and verify all three temporary URLs disappear from output and sitemap, page count is 16, and no production page imports AnswerBlock.
- Acceptance: checks passed before fixture removal; no fixture is present or committed, component is committed unused, and no new dependencies or page copy changes were made. C1: `59f33c3`. C2: `5eea355`.

### 2. Review T3 edge cases within approved scope

- [x] Size: small. C3 changed article author schema type from Organization to Person. Content schema was not changed per approval.
- Files: src/components/UI/Seo.astro; PLAN.md; only with explicit expanded approval, src/content/config.ts and relevant fixtures.
- Acceptance: current three article schemas remain correct; explicit author absence is tested without invented metadata; frontmatter extraction boundary cases are documented or fixed within Seo. Preserve NGO, nonprofitStatus, and existing schema types.
- Decision resolved: do not change the content schema. Current valid blog frontmatter emits Person author and datePublished. Missing pubDate remains a schema validation limitation. C3: `5d204ba`.

### 3. Complete T7 font loading

- [x] Size: medium. Exact Google Fonts families, weights, display mode, and fallback stacks were preserved. C4: `32f84eb`.
- Files: src/assets/styles/global.css; src/layouts/BaseLayout.astro outside analytics; PLAN.md.
- Move the exact Google Fonts URL from CSS import to a head stylesheet link. Add appropriate preconnect hints. Preserve Inter weights 400, 500, 600, 700; Playfair Display weight 700; display=swap; all fallbacks and existing styles.
- Acceptance: build passed; no Google Fonts import remains in built CSS; the exact stylesheet link and two preconnects are emitted; Inter and Playfair Display remain in compiled font rules; analytics code is unchanged. Browser visual comparison was not performed, so only source and generated output equivalence was verified. C4: `32f84eb`.
- Preserve the analytics block byte for byte. Record result and T7 commit if completed.

### 4. Complete T8 proposal document

- [ ] Size: medium. Not started by instruction; no page copy or proposal document was created.
- Files: docs/seo-geo-analysis.md; PLAN.md. No page edits.
- Acceptance: all 13 active pages have current title, description, H1, counted main content words, intent, proposed conversational question, a validated 40 to 60 word answer, and 3 to 5 list items. Include current versus proposed metadata and internal links. Use this branch's actual privacy page.
- Explicitly note the three articles currently link only back to the blog index in their main content. List every proposal changing member facing claims for founder approval. Discuss missing production FAQPage, BreadcrumbList, and Speakable; unused component support does not mean those schemas are active.
- New proposed copy follows all original wording constraints. Existing metadata quotations remain exact. Build, update this plan, and commit T8.

### 5. Complete T9 specification only

- [ ] Size: medium. Not started by instruction; no plan page implementation or specification was created.
- Files: docs/plan-page-spec.md; PLAN.md. Build no checkout, onboarding, donation route, or payment integration.
- Acceptance: document proposed data shape and storage, route pattern, exclusion from header and inclusion in footer, checkout to onboarding sequence, and at least two plan identity options. Explain URL and event exposure to both GA4 and Clarity, distinguish a plan hint from verified payment, and recommend an option with tradeoffs.
- Specify permitted onboarding fields and the existing form notice. Describe FDACS disclosure placement on pages providing online contribution processing and its visible rendering, referencing Footer.astro:25. Treat exact compliance wording as requiring David's supplied letter rather than verified legal advice.
- Include a section titled What David must supply: integration or Stripe link per tier, names, program service fee amounts, inclusions, FDACS registration number, and exact disclosure wording. Also identify operational choices needed for payment verification, recipients, redirects, and any individual versus employer differences. Do not access Stripe or secrets.
- Build, update this plan, and commit T9.

### 6. Final regression and original overnight report

- [ ] Size: medium. Depends on items 1 through 5 being completed or explicitly deferred.
- Files: docs/overnight-run-report.md; PLAN.md; any approved verification script only.
- Acceptance: full build and available checks pass; 16 intended HTML pages remain; image, form, schema, heading, noindex, font and protected source assertions pass. No temporary routes, unapproved copy edits, dependency changes, or unrelated changes. State unavailable checks plainly.
- Report the original overnight starting status on privacy-policy-draft, branch creation from main, every task's status, files, commit hash, commit message, and build result. Include the T1 before and after tags and T2 file/image/dimension table requested originally. Distinguish original observations from recovery checks.
- Include findings outside scope, confirmation that main and the privacy draft were not modified, and no push or merge during this work. Update this plan before committing the final report last. A report cannot contain its own eventual commit hash without a self reference problem; print that hash after the report commit instead.
- Finish with git log --oneline main..HEAD and final git status. List manual checks still needed. Never push or merge.

## Optional work requiring separate approval

- [ ] Full Astro lint and type checking: medium. package.json, package-lock.json, and new tooling configuration. Would require approved direct dev dependencies such as @astrojs/check and an Astro aware ESLint setup; possibly a direct TypeScript declaration. This conflicts with the original no dependency changes rule, so do not install anything by default. Existing parent Next.js ESLint is not suitable.
- [ ] Privacy policy integration and legal copy corrections: separate task and approval. Preserve the existing privacy-policy-draft branch; no merge authorized.
- [ ] Operational placeholders, hero alt copy, future image metadata automation, robots crawl policy, production canonical configuration, stronger API validation and a functional no JavaScript submission path: separate scope. Do not change protected files or copy during maintenance.

## Resume protocol

Read this file and git status before acting. Preserve unrecognized changes. Obtain approval for the core checklist and explicit direction on optional scope decisions before their work. After each completed item, mark its checkbox, add its commit and actual verification results, and make a small scoped commit. Keep blocked items unchecked with the reason. Do not turn inferred findings into claims of tested behavior.
