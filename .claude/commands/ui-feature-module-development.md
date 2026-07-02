---
name: ui-feature-module-development
description: Workflow command scaffold for ui-feature-module-development in animatize.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /ui-feature-module-development

Use this workflow when working on **ui-feature-module-development** in `animatize`.

## Goal

Implements new UI features or modules, often as ES modules, updating main app files, HTML, and styles, sometimes wiring to new or existing API endpoints.

## Common Files

- `src/web/static/app.js`
- `src/web/static/index.html`
- `src/web/static/styles.css`
- `src/web/static/modules/*.js`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create or update ES module(s) under src/web/static/modules/ for the new feature.
- Update main app.js to import and integrate the new module(s).
- Modify index.html to include new UI elements or containers.
- Update styles.css for new UI components.
- Wire up to backend endpoints if needed.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.