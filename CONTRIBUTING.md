# Contributing a Server Entry

## Submission

1. Copy `TEMPLATE.yaml` to `servers/your-server-slug.yaml`
2. Fill in all required fields (see template comments)
3. Run `python3 scripts/generate_servers_md.py`
4. Open a PR

The slug must be lowercase, use single hyphens between words, and match
`^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$`.

Before opening the PR, verify the generated index is current:

```bash
python3 scripts/generate_servers_md.py --check
python3 -m unittest discover -s tests -v
```

## Required for acceptance

- [ ] Source repo URL is reachable
- [ ] Install command actually works (verified by you, today)
- [ ] `last_verified` date is set to today
- [ ] License is open source (MIT, Apache 2.0, BSD, MPL, GPL, anything OSI-approved)
- [ ] Description is one paragraph, no marketing language
- [ ] Categories chosen from the existing list (or open an issue to add a new category first)
- [ ] Status is honest: `stable` means production-ready, `beta` means works but rough, `alpha` means experimental, `unmaintained` means the maintainer abandoned it

## What gets rejected

- **Closed-source servers.** This directory is for code people can read and audit.
- **Hosted-only services with no source.** If the server is a SaaS wrapper without source, it doesn't belong here.
- **Servers that haven't shipped working tools.** Vapor doesn't get listed.
- **Duplicate listings.** If a similar server exists, justify why this is meaningfully different.
- **Marketing copy.** "The best MCP server for X" is not a description. Describe what it does.
- **Servers that look like demos.** A 30-line script that calls one API doesn't justify a registry entry.

## Updating an existing entry

Same flow. Title format: `update server: slug`. Bump `last_verified` to today after re-testing.

## Removing an entry

Open an issue first explaining why. Reasons:
- Source repo deleted
- Server hasn't worked in 6+ months
- Maintainer asked for removal
- Security concern not fixed

## Reporting issues with a listed server

If a listed server is broken, malicious, or abandoned, open an issue with the server slug in the title. Don't open a PR to delete it without discussion.

## Verification cadence

Entries should be re-verified at least every 6 months. Volunteers periodically test entries and bump `last_verified`. If you'd like to help verify, comment on the verification issue.

## Adding a new category

If your server doesn't fit existing categories, open an issue first proposing the new category and at least 2 servers that would use it. Categories with only one entry get folded into "other."
