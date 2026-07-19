# mcp-server-registry

A community-maintained directory of public MCP (Model Context Protocol) servers. Find one to use, or list yours.

This is the **directory** repo. If you want to build your own MCP server, see [claude-mcp-starter](https://github.com/0xelitesystem/claude-mcp-starter). For the protocol spec itself, see [modelcontextprotocol.io](https://modelcontextprotocol.io).

## What's in this directory

Servers are listed as YAML entries in [`servers/`](./servers), one file per server. Each entry includes:

- Name, maintainer, source repo
- Transport (`stdio`, `sse`, `http`)
- Authentication method (`none`, `oauth`, `api-key`, `bearer-token`)
- Language (Python, Node, Go, Rust, etc.)
- Status (`stable`, `beta`, `alpha`, `unmaintained`)
- Brief description
- Install command

## Browse

See [`SERVERS.md`](./SERVERS.md) for an auto-generated table of all servers, sortable by language, transport, and status.

If a server isn't listed here, it doesn't mean it doesn't exist, it just hasn't been added. PRs welcome.

## Servers in this directory

The initial seed includes the official servers from the MCP project plus a few well-known community servers. The community is encouraged to add more.

- **Filesystem**, read/write/search files (official)
- **GitHub**, search repos, read files, create issues (official)
- **Slack**, read messages, send messages, list channels (official)
- **Postgres**, query Postgres databases (official)
- **SQLite**, query SQLite databases (official)
- **Sequential Thinking**, multi-step reasoning helper (official)
- **Brave Search**, web search via Brave (official)
- **Fetch**, fetch any URL and return its content (official)
- **Memory**, persistent key-value store across conversations (official)
- **Time**, timezone conversions and date math (official)

See [`servers/`](./servers) for full entries.

## Add your server

1. Copy [`TEMPLATE.yaml`](./TEMPLATE.yaml) to `servers/your-server-name.yaml`
2. Fill in all required fields
3. Run `python3 scripts/generate_servers_md.py`
4. Open a PR

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full submission checklist.

## Use a server

Each entry includes an install command. Most stdio-transport servers are installable via:

```bash
# Node-based:
npx -y @some-org/mcp-server-x

# Python-based:
uvx some-mcp-server

# Or by cloning the source repo and following its README
```

After installing, configure your MCP client (Claude Desktop, Cursor, Claude Code, etc.) to use the server. Each client has a config file, see your client's docs.

## What this directory is NOT

- **Not a security audit.** Listings are provided as-is. Inspect any MCP server before connecting it to sensitive data.
- **Not exhaustive.** Many private/internal MCP servers exist that don't belong here. This is for public, reusable ones.
- **Not endorsed by the MCP project.** This is a community catalog, not the official directory.
- **Not a hosted runtime.** This repo only lists servers; it doesn't run them.

## License

MIT. Each server entry is MIT licensed; copying one into your own list is fine.

## Related

- [claude-mcp-starter](https://github.com/0xelitesystem/claude-mcp-starter), start your own MCP server
- [Model Context Protocol](https://modelcontextprotocol.io), the official spec and SDKs
- [Anthropic MCP servers](https://github.com/modelcontextprotocol/servers), the official server collection
