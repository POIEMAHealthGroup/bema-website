# Contributing to the BEMA Website

This repository contains the production Astro website for BEMA Incorporated.

## Local Setup

```sh
npm install
npm run dev
```

## Before Opening a Change

- Keep changes scoped to the requested route, component, or content collection.
- Preserve the BEMA brand tokens in `tailwind.config.cjs`.
- Keep placeholder content in bracketed descriptor format until approved.
- Use `Find a Partner Clinic` for links to `/providers`.
- Do not add intake forms, payment flows, member portals, scheduling flows, or live directory data unless a later requirements document explicitly asks for them.

## Verification

Run the build before handoff:

```sh
npm run build
```

For copy changes, also scan rendered content for restricted terminology and confirm that the contact form disclaimer remains present.
