# MCP server — `trust-gate`

**The same perimeter, for any MCP client.** v0.2 ships `mcp/server.py`: a
dependency-free stdio MCP server that exposes the Nambikkai engine to anything that
speaks MCP — other harnesses, other agents, your own scripts. It imports the *same*
`patterns.py` the hooks use and is tested against the *same* `corpus/cases.json`
(`tests/test_mcp.py`). A surface that doesn't pass the golden file doesn't ship.

## Register it

Any MCP client config; for Claude Code:

```json
{
  "mcpServers": {
    "nambikkai": {
      "command": "python3",
      "args": ["/path/to/nambikkai/mcp/server.py"]
    }
  }
}
```

No dependencies to install — stdlib only, same as the hooks.

## Tools

| Tool | In | Out | The catch |
|---|---|---|---|
| `check` | `text` | findings as `kind` + **masked** span + index, `clean`, `blocking` kinds | never returns a raw value — `check` cannot become the leak |
| `redact` | `text` | the text, every finding partial-masked in place | same masks as the gate |
| `tag_fact` | `fact`, `src`, `tier`, `date?`, `ttl?` | the fact with a `[src \| date \| tier \| ttl]` receipt appended | **gates its own input** — a fact carrying a raw blocking identifier is refused with a pointer hint, not stamped |
| `lint` | `text` (markdown) | counts + line numbers for untagged / stale / malformed receipts | line numbers only, content never echoed; the `provenance-lint` skill remains the judgment layer — this is the mechanical net |

`tag_fact` validates tier (`firm`/`stated`/`inferred`/`hunch`) and TTL shape
(`evergreen` · `permanent` · `expired` · `<N>mo` · `<N>d` · `review:YYYY-MM`) per
[the receipts convention](../concepts/receipts.md).

## Placement, honestly

The hooks remain the stronger placement: a `PreToolUse` block is enforcement the
model cannot skip, while an MCP tool is one the calling agent must *choose* to use.
The server exists for surfaces where hooks can't reach — treat it as a checkpoint
you wire into your pipeline, not a perimeter that wires itself.
