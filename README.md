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
xiaoheiniao/
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

Legacy private-oriented `ops/` notes were removed from the current public tree on 2026-08-22. Their historical commits remain in Git history for audit; no history rewrite was performed because no credential/private-key exposure was identified. New operational/compliance notes that are not intentionally public must live in the correct private authority rather than this repository.

## Hosting/DNS principles

The repository contains the public-site source and non-secret hosting configuration appropriate for the static site. DNS/email infrastructure must not be modified as a side effect of ordinary content edits.

When changing hosting or DNS, verify current provider documentation and preserve unrelated mail/security records. Hosting migration, ICP/public-security filing operations and other provider-specific execution require their own authorized runbook; this repository does not grant those permissions merely because it contains public site files.

## Current production deployment: Tencent SCF

`https://www.jiripple.com/` is currently served through a Tencent SCF web-function deployment. **A GitHub merge does not automatically update the production SCF code package.**

The production static runtime now lives with the canonical site source in this repository:

```text
scf/server.py
scf/scf_bootstrap
scripts/build_scf_package.py
```

Build the deployable ZIP from the current checked-out `main`:

```bash
python3 scripts/build_scf_package.py
```

The command writes a Git-ignored package under `dist/` and prints its SHA-256. It fails closed if the SCF route allowlist and package contents drift apart.

Every public HTML file entering the SCF production package must statically contain the ICP and public-security filing footer; `scripts/build_scf_package.py` validates this fail closed.

The runtime intentionally serves only the public static surfaces packaged by the builder, including:

```text
/
/reliablereader/
/reliablereader/privacy/
/xiaoheiniao/
/xiaoheiniao/context.md
/llms.txt
/robots.txt
/sitemap.xml
```

Repository/admin files such as `AGENTS.md`, `README.md`, `scf/`, and `scripts/` are not web routes in the SCF runtime.

After building, deployment still requires the authorized Tencent Cloud SCF operation: upload the generated ZIP to the existing production function and deploy it. Do not change DNS, certificates, mail records, function identity, or unrelated cloud settings as part of a routine static-content publish.

## Governance

See `AGENTS.md` before substantive maintenance.
