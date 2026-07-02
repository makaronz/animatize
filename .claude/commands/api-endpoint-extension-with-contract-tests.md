---
name: api-endpoint-extension-with-contract-tests
description: Workflow command scaffold for api-endpoint-extension-with-contract-tests in animatize.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /api-endpoint-extension-with-contract-tests

Use this workflow when working on **api-endpoint-extension-with-contract-tests** in `animatize`.

## Goal

Extends an existing API endpoint with new metadata or features, ensuring backward compatibility and adding/adjusting integration or contract tests.

## Common Files

- `src/web/app.py`
- `tests/integration/test_*.py`
- `.gitignore`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Modify the API implementation file to add new fields or logic.
- Update or add integration/contract test files to cover the new behavior.
- Optionally update .gitignore to handle new artifacts if needed.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.