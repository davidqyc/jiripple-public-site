# ReliableReader Public Site Candidate

This directory is a candidate GitHub Pages site root for publishing ReliableReader public pages.

When publishing through an independent GitHub Pages repository, place every file inside `public-site/` at the repository root. The root should include:

```text
CNAME
README.md
reliablereader/privacy/index.html
```

## Candidate URL

Target privacy policy URL:

```text
https://jiripple.com/reliablereader/privacy/
```

Candidate file:

```text
public-site/reliablereader/privacy/index.html
```

## Recommended Hosting Path

Use a simple static host. GitHub Pages is a practical first choice if a dedicated static-site repository will be created for `jiripple.com`.

Suggested GitHub Pages settings:

```text
Source: Deploy from a branch
Branch: main
Folder: / (root)
```

The `CNAME` file in this directory contains:

```text
jiripple.com
```

This directory is not deployed yet. Before publishing, the owner still needs to:

1. Create or choose the static-site repository.
2. Copy all files inside `public-site/` to that repository root.
3. Enable GitHub Pages with the settings above, or configure another static host.
4. Configure DNS for the website after checking the host's current official documentation.
5. Verify that `https://jiripple.com/reliablereader/privacy/` returns the privacy policy page.

## DNS Principles

The domain currently has email-related DNS records for Tencent Enterprise Mail / WeCom-style mail service. Website setup should not disrupt mail.

When setting up hosting:

- Add only the website records required for the selected host, such as A / AAAA / CNAME records.
- Do not change MX records.
- Do not remove or overwrite Tencent / WeCom mail TXT records.
- Do not remove or overwrite SPF, DKIM, or DMARC records.
- Do not replace nameservers.

This README does not list concrete DNS IP addresses because those should be checked against the selected host's current official documentation before configuration.

## Current Limitation

These files cannot be published directly from this repository without a chosen hosting path. No DNS, GitHub Pages, cloud hosting, upload, or deployment has been configured by this candidate.
