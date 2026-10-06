# Servers

Auto-generated table from `servers/*.yaml`. To regenerate after adding entries:

```bash
# Run scripts/generate_servers_md.py (community-contributed; see issues for status)
```

(Until the generator script is contributed, this table is maintained manually as part of each PR.)

| Server | Lang | Transport | Auth | Status | Categories |
|---|---|---|---|---|---|
| [Filesystem](servers/filesystem.yaml) | TypeScript | stdio | none | stable | filesystem, development |
| [GitHub](servers/github.yaml) | TypeScript | stdio | bearer-token | stable | version-control, development |
| [Postgres](servers/postgres.yaml) | TypeScript | stdio | api-key | stable | database, data |
| [SQLite](servers/sqlite.yaml) | Python | stdio | none | stable | database, data |
| [Sequential Thinking](servers/sequential-thinking.yaml) | TypeScript | stdio | none | stable | reasoning, ai |
| [Fetch](servers/fetch.yaml) | Python | stdio | none | stable | web, search |
| [Brave Search](servers/brave-search.yaml) | TypeScript | stdio | api-key | stable | search, web |
| [Hyperconsciousness](servers/hyperconsciousness.yaml) | Rust | stdio | custom | alpha | database, search, productivity |
| [Memory](servers/memory.yaml) | TypeScript | stdio | none | stable | data, productivity |
| [Time](servers/time.yaml) | Python | stdio | none | stable | productivity, other |
| [Slack](servers/slack.yaml) | TypeScript | stdio | bearer-token | stable | communication, productivity |

## Categories

- **database**, query and manipulate databases
- **filesystem**, read/write local files
- **version-control**, git, GitHub, GitLab, etc.
- **communication**, Slack, email, chat platforms
- **search**, web search, code search
- **productivity**, calendars, notes, task managers
- **development**, dev tooling, CI, deployment
- **reasoning**, meta-tools for structured AI thinking
- **web**, fetch URLs, scrape, browse
- **ai**, wraps other AI services
- **data**, data warehouses, analytics, formats
- **finance**, banking, payments, accounting
- **other**, utilities that don't fit elsewhere

## Filters

To filter by attribute, search this file:

- All Python servers: search "Python"
- All servers requiring auth: search "api-key" OR "bearer-token" OR "oauth"
- All search-related: search "search,"
