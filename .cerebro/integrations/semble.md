# Semble — Semantic Code Search

Semble is installed as an MCP server. Nightcrawler should prefer it over grep for natural-language queries.

## MCP Tools

- `search(query, repo)` — natural-language or identifier search; `repo` is a local path or git URL; defaults to the current working directory.
- `find_related(file_path, line, repo)` — find chunks semantically similar to the code at a given file location.

## When to Use Semble

- Conceptual / natural-language queries → `search`
- "Find code similar to X" → `find_related`
- Exhaustive exact-string or regex matching → use `grep` (semble is not a text matcher)

## Indexing for Repeated Searches

Index once for faster repeated queries:
```bash
semble index . -o .cerebro/semble-index
```
Pass `--index .cerebro/semble-index` to searches. Reindex if the codebase changes significantly.
