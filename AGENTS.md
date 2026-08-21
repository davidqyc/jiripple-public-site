# JiRiPPLE Public Web Collaboration Contract

This is a **public repository** and a shared static public-web surface.

## Default rule

Treat every committed byte as intentionally public, even when the file is excluded from GitHub Pages/Jekyll output.

## Allowed scope

- static public HTML/CSS/assets;
- privacy/support/terms/legal pages;
- small public product/company landing surfaces;
- non-secret hosting configuration required by the static site.

## Not allowed

Do not commit:

- credentials/tokens/cookies/API keys/private keys;
- identity documents/private personal data;
- private account/resource IDs or private endpoint values;
- internal raw logs/provider exports;
- private product source or database contents;
- operational notes that are only safe because they are hidden from the rendered website.

Historical `ops/` content is legacy. Do not expand it with private operational data. Pages exclusion is not a privacy mechanism.

## Repository role

Use this repository as a strict superset of its original public-page role so multiple JiRiPPLE products can share one simple static surface. Do not merge private product repositories into it.

If the web surface becomes a dynamic/independent application with its own backend, CMS, auth, deployment lifecycle or substantial roadmap, promote that future web application to its own repo.

## Change safety

Ordinary content edits do not authorize DNS, hosting-provider, certificate, ICP/public-security filing, account, or Cloud mutations. Those require their own current authority and explicit execution boundary.

Before changing `CNAME`, hosting configuration or domain-related behavior, read the current public-site state and relevant live provider authority; do not rely on old ops notes as current provider truth.
