# ANIMAtiZE V1 interface specification (EN)

This document defines a V1 UX concept for ANIMAtiZE, an AI video generation
workflow tool focused on coherence and intent-first creation. The objective is
to help creators move from idea to usable sequence quickly, with clear controls
and minimal friction.

## Scope

This V1 specification covers only the following workflows:
- New sequence creation from image and intent.
- Generation setup and execution.
- Comparing multiple results.
- History, favorites, and one-click regeneration.

This V1 does not include speculative features such as voice control or real-time
collaboration.

## UX principles and constraints

The interface follows these core principles:
- Use progressive disclosure to reduce cognitive load.
- Keep generated content visually central.
- Provide smart defaults and presets.
- Optimize for quick first success.
- Keep controls explicit, predictable, and reversible.

## Information architecture

The app should use a simple, task-oriented navigation model.

## Main navigation

- `Create` (default landing screen)
- `History`
- `Favorites`
- `Presets`
- `Settings`

## Page structure

- `Create`
  - Main creation workspace (center)
  - Parameter panel (right side, collapsible)
  - Generation timeline (bottom drawer)
- `History`
  - Chronological run list with filters
  - Row-level actions: open, compare, regenerate
- `Favorites`
  - Saved output cards with quick compare and regenerate
- `Presets`
  - Curated and custom presets for speed, coherence, and quality
- `Settings`
  - Defaults, accessibility options, and account preferences

## Low-fidelity wireframes (text description)

Each wireframe is intentionally low-fidelity and focused on usability.

## Wireframe 1: Create workspace (empty state)

Layout:
- Top app bar with main navigation and account menu.
- Large central image drop zone (`Drop image or browse`).
- Intent input directly below drop zone with example chips.
- Right parameter panel collapsed to a narrow summary strip.
- Bottom timeline drawer with placeholder (`No generations yet`).

Primary actions:
- Upload image.
- Enter intent.
- Click `Generate` (disabled until required fields are valid).

State behavior:
- Empty guidance copy explains the minimum required steps.
- Smart preset `Cinematic balanced` is preselected.

## Wireframe 2: Setup and execution (loading state)

Layout:
- Uploaded image preview remains in the center.
- Result slots appear as loading cards (default 3 variants).
- Right panel opens in `Basic` mode:
  - Preset
  - Duration
  - Aspect ratio
  - Motion intensity
- `Advanced` section remains collapsed.

Primary actions:
- Start generation.
- Cancel current run.
- Adjust basic parameters and rerun.

State behavior:
- Per-variant progress bars with status text and ETA.
- Current run appears immediately in timeline as `Running`.

## Wireframe 3: Results workspace (success state)

Layout:
- Center area shows generated result cards with preview and metrics.
- Right panel shows parameters used and quick tweak controls.
- Top run summary strip displays run ID, preset, duration, status.
- Bottom timeline keeps latest run pinned for quick reopening.

Primary actions:
- Open result detail.
- Favorite result.
- Compare selected results.
- Regenerate from selected result.

State behavior:
- Success toast confirms output availability.
- Failed variants remain visible with retry action.

## Wireframe 4: Result comparison panel

Layout:
- Side-by-side comparison view (`A | B`, optional `C`).
- Shared scrubber for synchronized playback/scrubbing.
- Metric chips: coherence, intent fidelity, motion quality.
- Parameter-difference rail on the right.

Primary actions:
- Select winner.
- Favorite winner.
- Regenerate winner with minor tweaks.

State behavior:
- Comparison can be launched from Create, History, or Favorites.
- On mobile V1, comparison is limited to two variants.

## Wireframe 5: History and favorites timeline

Layout:
- Left filter rail:
  - Date range
  - Status
  - Preset
  - Favorites only
- Main timeline grouped by day/session.
- Each run row shows thumbnail, intent snippet, settings summary, status.

Primary actions:
- Open run.
- Compare run outputs.
- One-click regenerate.
- Toggle favorite.

State behavior:
- Empty state points users back to `Create`.
- Error rows show clear failure reason and retry option.

## Component inventory

The V1 UI should use a small, reusable component set.

## Inputs and fields

- Image drop zone with click fallback file picker.
- Intent text area with examples and inline validation.
- Optional negative intent field (advanced only).
- Run title inline editor.

## Selectors and controls

- Preset selector.
- Aspect ratio segmented control.
- Duration slider or stepper.
- Variant count selector (default: 3).
- Quality and speed mode selector.

## Cards

- Result card (preview, metrics, actions).
- Run card (history row with status and quick actions).
- Error card (reason, retry path).
- Empty state card (guided onboarding).

## Timeline and compare components

- Bottom generation timeline drawer.
- Full history timeline list.
- Comparison viewer with synchronized scrubber.
- Metric badge chips and parameter delta list.

## Key interaction patterns

The interaction model should minimize friction and preserve context.

1. Drag and drop image upload with keyboard and file-picker fallback.
2. One-click generate from default preset.
3. Progressive disclosure in parameter panel (`Basic` before `Advanced`).
4. One-click regenerate from result cards, history rows, and favorites.
5. Regenerate keeps prior parameters unless explicitly changed.
6. Favorite toggle available in all result surfaces.
7. Compare action available after selecting at least two results.
8. Inline tweak and rerun loop from selected comparison winner.
9. Recoverable error flow with explicit reason and retry action.
10. Keyboard shortcuts for power users (`G`, `C`, `F`, `R`), with visible help.

## Responsive behavior notes

The layout should remain task-first across breakpoints.

- Desktop (`>=1200px`)
  - 3-zone layout: center media, right parameter panel, bottom timeline.
- Tablet (`768px-1199px`)
  - Center-first layout with collapsible side sheet for parameters.
  - Timeline available as bottom tab panel.
- Mobile (`<768px`)
  - Step-based flow: Upload -> Intent -> Generate -> Compare.
  - Bottom sheets for parameters and run actions.
  - Compare mode limited to two results in V1.

Touch and layout rules:
- Minimum touch target: 44x44 px.
- Sticky primary action area for `Generate` and `Regenerate`.
- No horizontal scrolling in primary workflows.

## Accessibility checklist (WCAG AA baseline)

The V1 must satisfy baseline accessibility requirements.

- Text contrast meets WCAG AA thresholds (4.5:1 normal text, 3:1 large text).
- Full keyboard navigation across all major workflows.
- Visible focus indicators on all interactive elements.
- Accessible names and labels for all controls and media actions.
- Drag and drop has a non-pointer alternative.
- Progress and status updates are announced via ARIA live regions.
- Errors are specific, actionable, and associated with fields.
- Status and quality are not conveyed by color alone.
- Motion and animation respect `prefers-reduced-motion`.
- Zoom at 200 percent preserves readability and operability.

## UX risks and mitigations (V1)

The table below focuses on cognitive load and usability risks.

| Risk | Impact | Mitigation |
|---|---|---|
| Parameter overload on first run | Slow onboarding, confusion | Show only 4 basic controls by default. |
| Too many generated options | Decision fatigue | Default to 3 variants, require explicit opt-in for more. |
| Ambiguous quality metrics | Low trust in output | Use plain-language metric labels and tooltip examples. |
| Context loss across surfaces | Rework and navigation friction | Keep persistent run summary and clear return paths. |
| Infinite rerun loop | Time and cost waste | Add winner recommendation and rerun guidance. |
| Hidden cost and duration expectations | User frustration | Show estimated runtime before execution and rerun. |
| Error handling feels opaque | Drop-off after failure | Show cause, fallback behavior, and one-click retry. |
| Compare view overload | Cognitive overload | Cap compare to 3 items desktop, 2 items mobile. |
| History clutter at scale | Retrieval friction | Add grouping, filters, and saved views. |
| Accessibility regression in media-heavy UI | Exclusion and legal risk | Enforce automated and manual accessibility QA gates. |

## V1 success criteria (UX)

These outcomes define whether the V1 UX is working.

- Time to first successful sequence is reduced.
- Users complete primary flow without advanced controls.
- Compare and regenerate loops are discoverable and efficient.
- History and favorites support quick retrieval and reuse.
- Accessibility checks pass without critical issues.

## Next steps

1. Validate the wireflows with 5-8 representative creators.
2. Create clickable low-fidelity prototype and run usability tests.
3. Convert this specification into implementation tickets by workflow.
