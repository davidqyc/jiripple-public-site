# JiRiPPLE Public Site

This repository is the public static-web source for JiRiPPLE / related product public pages.

It is intentionally separate from private product repositories so public deployment artifacts can remain narrow, auditable and free of private product source, secrets and internal data.

## Scope

Appropriate content includes low-complexity public static surfaces such as:

```text
product privacy policies
product support/contact pages
product terms/legal notices
company/public legal notices
small static product landing pages
```

Current product paths may live under product-specific directories such as:

```text
reliablereader/
```

Do not create a new `*-site` repository for every product when a simple static page fits this shared public surface.

## Promotion boundary

This repository should remain a simple static public delivery surface. If a future website grows into an independently engineered product with a CMS, authenticated backend, dynamic application state, complex deployment or a substantial independent roadmap, promote that website to its own repository rather than turning this repo into a catch-all application monolith.

## Public-source safety boundary

**This repository is public.** Pages/Jekyll exclusions affect website publication, not GitHub source visibility.

Therefore new commits must not contain:

- credentials, tokens, cookies, API keys or private certificates;
- private account/resource identifiers;
- identity documents or personal contact data;
- private provider endpoints;
- internal operational logs or raw filing/account screenshots;
- private product source/data that is not intentionally public.

Historical `ops/` files predate this boundary. Do not add new private operational records there by default. Any decision to remove historical files, change repository visibility or rewrite history is a separate explicit governance/privacy action.

## Hosting/DNS principles

The repository contains the public-site source and domain configuration artifacts appropriate for static hosting. DNS/email infrastructure must not be modified as a side effect of ordinary content edits.

When changing hosting or DNS, verify current provider documentation and preserve unrelated mail/security records. Hosting migration, ICP/public-security filing operations and other provider-specific execution require their own authorized runbook; this repository does not grant those permissions merely because it contains public site files.

## Governance

See `AGENTS.md` before substantive maintenance.
