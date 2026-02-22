# MVDS design system (as-built)

This document defines the Minimum Viable Design System (MVDS) currently used by
the V1 UI in `src/web/static/styles.css`.

The stylesheet is token-first and uses three token layers:

1. `--mvds-ref-*` (reference tokens),
2. `--mvds-sem-*` (semantic tokens),
3. `--mvds-cmp-*` (component tokens).

## Source of truth

All design tokens live in one place:

- `src/web/static/styles.css` under the root `:root` block.

If you need to change visual language, update tokens first, then component
rules.

## Token layers

## Reference tokens (`--mvds-ref-*`)

Reference tokens capture raw design primitives:

- colors,
- typography families, sizes, weights,
- spacing scale,
- radius scale,
- shadows,
- breakpoint constants.

Examples:

- `--mvds-ref-color-neutral-900`
- `--mvds-ref-space-4`
- `--mvds-ref-font-size-500`
- `--mvds-ref-breakpoint-md`

## Semantic tokens (`--mvds-sem-*`)

Semantic tokens map primitives to intent:

- surface/background,
- text roles,
- border roles,
- status roles,
- subtle state backgrounds.

Examples:

- `--mvds-sem-bg-surface`
- `--mvds-sem-text-muted`
- `--mvds-sem-status-failed-bg`

## Component tokens (`--mvds-cmp-*`)

Component tokens map semantic styles to concrete UI elements:

- button styles,
- input styles,
- card styles,
- chip styles,
- badge styles,
- alert styles,
- skeleton styles.

Examples:

- `--mvds-cmp-button-primary-bg`
- `--mvds-cmp-input-padding-x`
- `--mvds-cmp-alert-error-border`

## Component-to-token mapping

| Component | Primary selectors | Token families used |
|---|---|---|
| Button | `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-small` | `--mvds-cmp-button-*`, `--mvds-cmp-badge-*`, semantic text/border tokens |
| Input | `textarea`, `select`, `input[type="number"]`, `input[type="range"]` | `--mvds-cmp-input-*`, semantic text/background tokens |
| Card | `.creation-stage`, `.parameter-panel`, `.result-card`, `.list-card` | `--mvds-cmp-card-*`, reference shadow/radius |
| Chip | `.chip` | `--mvds-cmp-chip-*` |
| Badge | `.metric-badge`, `.status` | `--mvds-cmp-badge-*`, semantic status tokens |
| Alert | `.alert`, `.alert-error` | `--mvds-cmp-alert-*` |
| Skeleton | `.skeleton`, `.skeleton::after` | `--mvds-cmp-skeleton-*` |

## Breakpoints

Breakpoint values are defined as reference tokens:

- `--mvds-ref-breakpoint-lg`
- `--mvds-ref-breakpoint-md`
- `--mvds-ref-breakpoint-sm`

Media queries mirror these values in `rem` constants in the same file.
Keep both in sync when updating responsive behavior.

## Rules for adding new components

Use this process every time:

1. Define or reuse `ref` token(s) only if a new primitive is needed.
2. Map visual intent through `sem` token(s).
3. Add `cmp` token(s) for component-specific values.
4. Build component styles using only semantic/component tokens in selectors.
5. Avoid hardcoded color, spacing, typography, and radius values in component
   blocks.

## Anti-patterns (do not use)

- Hardcoded hex values inside component blocks.
- Direct `rgba(...)` in component blocks when semantic/component tokens can be
  used.
- Adding one-off component values without tokenizing.
- Duplicating breakpoint values in multiple files.

## Verification checklist

When reviewing a UI change:

1. Confirm the component uses `--mvds-*` variables for visual properties.
2. Confirm no fake visual state is represented as generated content.
3. Confirm status badges and alerts use explicit runtime statuses from backend.
4. Confirm responsive behavior still aligns with MVDS breakpoint constants.
