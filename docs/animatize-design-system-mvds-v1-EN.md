# ANIMAtiZE minimum viable design system v1 (EN)

This document defines the minimum viable design system (MVDS) for ANIMAtiZE.
It translates the UX specification into an adoptable system for design and
engineering, with clear ownership, measurable outcomes, and an evolution path.

The document is aligned with:
- `/Users/arkadiuszfudali/Git/animatize/docs/animatize-v1-ux-spec-EN.md`
- `/Users/arkadiuszfudali/Git/animatize/docs/animatize-product-vision-prfaq-EN.md`

## 1) Why this system now

ANIMAtiZE already has enough repeated UX patterns to justify a focused design
system investment. The objective for V1 is not visual perfection. The objective
is predictable delivery speed, coherent UI behavior, and reduced cognitive load.

## 2) V1 scope and non-goals

### In scope

- Token foundation for color, typography, spacing, radius, shadow, motion,
  breakpoints, and z-index.
- Core component library for the four V1 workflows.
- Accessibility and state contracts shared across all components.
- Governance, release policy, and adoption metrics.

### Out of scope

- A full enterprise-grade multi-brand platform.
- Deep brand experimentation without product impact.
- Complex variable engines beyond V1 token needs.

## 3) System principles

1. Intent-first clarity over configuration complexity.
2. Generated content remains visually central on every screen.
3. Progressive disclosure by default.
4. Components should teach usage by structure and defaults.
5. System decisions must optimize both consistency and speed.

## 4) Token architecture

The MVDS uses a three-layer token model.

### 4.1 Token layers

- `reference` tokens: raw scales and primitives.
- `semantic` tokens: role-based mapping for UX meaning.
- `component` tokens: local aliases for component-level overrides.

### 4.2 Naming convention

Use dot notation with stable hierarchy:
- `ref.<category>.<scale>`
- `sem.<domain>.<role>`
- `cmp.<component>.<slot>.<state>`

Examples:
- `ref.color.neutral.900`
- `sem.text.primary`
- `cmp.button.primary.bg.default`

### 4.3 Core token sets (V1)

| Category | Token examples | V1 requirement |
|---|---|---|
| Color | `ref.color.*`, `sem.bg.*`, `sem.text.*`, `sem.border.*` | Required |
| Typography | `ref.type.size.*`, `ref.type.weight.*`, `sem.type.*` | Required |
| Spacing | `ref.space.0` to `ref.space.12` | Required |
| Radius | `ref.radius.none/sm/md/lg/xl/pill` | Required |
| Shadow | `ref.shadow.xs/sm/md/lg` | Required |
| Motion | `ref.motion.duration.*`, `ref.motion.easing.*` | Required |
| Breakpoints | `ref.bp.sm/md/lg/xl` | Required |
| Z-index | `ref.z.base/overlay/modal/toast` | Required |

### 4.4 Recommended base scales

Spacing scale (px): `0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64`

Type scale (size/line-height):
- `12/16`, `14/20`, `16/24`, `18/26`, `20/28`, `24/32`, `30/38`

Motion duration (ms):
- `80` (micro), `140` (default), `220` (complex), `320` (panel transitions)

Breakpoints:
- `sm: 640`, `md: 768`, `lg: 1200`, `xl: 1440`

### 4.5 Token format example

```json
{
  "ref": {
    "color": {
      "neutral": { "0": "#FFFFFF", "900": "#0B1020" },
      "brand": { "500": "#3B82F6", "600": "#2563EB" },
      "success": { "500": "#16A34A" },
      "danger": { "500": "#DC2626" }
    },
    "space": { "0": 0, "1": 2, "2": 4, "3": 8, "4": 12, "5": 16 }
  },
  "sem": {
    "bg": { "canvas": "{ref.color.neutral.0}", "panel": "#F7F9FC" },
    "text": { "primary": "{ref.color.neutral.900}", "muted": "#4B5563" },
    "border": { "default": "#D1D5DB", "focus": "{ref.color.brand.500}" }
  }
}
```

## 5) Visual direction and theming

ANIMAtiZE V1 should avoid flat and generic execution. The interface should feel
precise, cinematic, and dimensional, without reducing clarity.

### V1 visual rules

- Keep high contrast between content stage and control surfaces.
- Use subtle depth (shadow + layer hierarchy) to separate workspace areas.
- Reserve saturated brand color for primary actions and key states.
- Use motion to communicate state change, not decoration.

### Theme strategy

- Ship light theme first.
- Add dark theme only after token parity and accessibility parity.

## 6) V1 component library contract

The table below defines V1 system-owned components and contract minimums.

| Component | Purpose | Required variants | Required states | Accessibility minimum |
|---|---|---|---|---|
| `AppShell` | Global layout frame | Desktop, tablet, mobile | Default | Landmarks, skip link |
| `TopNav` | Main navigation | Standard, compact | Default, focus | Keyboard nav, active page |
| `SidePanel` | Parameter area | Collapsed, expanded | Default, loading | Focus trap when modalized |
| `BottomDrawer` | Timeline container | Collapsed, expanded | Default, dragging | Keyboard open and close |
| `DropZone` | Image upload | Idle, drag-over | Empty, error, success | Non-pointer upload path |
| `IntentInput` | Intent authoring | Single-line, multi-line | Default, error | Label, helper, error linkage |
| `PresetSelector` | Preset selection | List, segmented | Default, disabled | Arrow-key navigation |
| `SegmentedControl` | Aspect and mode switches | 2-4 options | Selected, disabled | `aria-pressed` semantics |
| `DurationControl` | Duration input | Slider, stepper | Default, error | Keyboard step controls |
| `ResultCard` | Output preview and actions | Compact, full | Loading, success, failed, favorited | Action labels, focus order |
| `RunCard` | History row | Compact, detailed | Running, failed, success | Status announcement |
| `StatusBadge` | State labeling | Neutral, success, warning, error | Default | Color and text redundancy |
| `Timeline` | Run chronology | Grouped, flat | Empty, loading | Logical reading order |
| `CompareViewer` | Side-by-side analysis | 2-up, 3-up | Loading, ready | Keyboard scrub support |
| `MetricChip` | Quality indicators | Info, positive, warning | Default | Icon plus text |
| `Toast` | Transient feedback | Info, success, warning, error | Enter, exit | Live region, dismiss action |

## 7) Shared state matrix

All V1 components must support the shared state model.

| State | Visual treatment | Interaction behavior | Required semantics |
|---|---|---|---|
| Empty | Guided placeholder | Primary CTA visible | Instructional copy |
| Loading | Skeleton or progress | Secondary actions limited | Progress announced |
| Success | Positive confirmation | Next-step action visible | Success label |
| Error | Clear error surface | Recovery path visible | Error role and field mapping |
| Disabled | Reduced emphasis | No interaction | Programmatically disabled |
| Focused | High-contrast ring | Keyboard-visible focus | Focus indicator required |

## 8) Interaction and motion primitives

### Core interaction primitives

- Drag and drop with explicit click fallback.
- One-click regenerate preserving prior settings.
- Progressive disclosure for advanced controls.
- Context-preserving transitions between Create, Compare, History.

### Motion primitives

- Micro feedback: `80-140ms`.
- Panel and drawer transitions: `220-320ms`.
- Easing defaults:
  - Enter: `ease-out`.
  - Exit: `ease-in`.
- Respect `prefers-reduced-motion` and provide non-motion alternatives.

## 9) Accessibility baseline and QA gates

### Accessibility baseline (WCAG AA)

- Text contrast >=4.5:1 for body text.
- Full keyboard operability in all key workflows.
- Screen reader labels for all actionable controls.
- Status communication not dependent on color only.
- Zoom to 200 percent with no functionality loss.

### Required QA gates before release

1. Automated a11y scan with no critical issues.
2. Manual keyboard walkthrough for Create, Compare, History.
3. Screen reader smoke test on status and error flows.
4. Responsive checks on desktop, tablet, mobile breakpoints.

## 10) Governance and operating model

### Ownership

- Design system product owner: Product Design lead.
- Design system engineering owner: Frontend lead.
- Accessibility owner: QA or UX quality lead.

### Contribution workflow

1. Open design system proposal issue.
2. Attach usage evidence from workflow screens.
3. Approve through design and frontend review.
4. Implement token and component updates.
5. Publish release notes and migration guidance.

### Release policy

- Use semantic versioning for component contracts.
- Patch: visual or bug fixes without API change.
- Minor: additive variants and backward-compatible features.
- Major: breaking contract changes with migration plan.

### Deprecation policy

- Mark deprecated components for two minor versions.
- Provide codemod or migration guide before removal.

## 11) Adoption model and success metrics

Adoption must be measurable and tied to delivery speed and quality.

| Metric | Definition | Baseline | 90-day target |
|---|---|---:|---:|
| Component reuse rate | New screens built with MVDS components | To measure | >=80% |
| Token usage compliance | Styles mapped to tokens vs raw values | To measure | >=90% |
| UI inconsistency defects | Defects linked to style or behavior drift | To measure | -40% |
| Time to build workflow screen | End-to-end implementation time | To measure | -25% |
| A11y critical defects | Critical accessibility findings | To measure | 0 |
| First-pass UX QA pass rate | Screens passing QA without rework | To measure | >=75% |

## 12) Rollout plan

### Phase 0 (week 1): setup

- Finalize token naming and scales.
- Create repository structure for tokens and docs.
- Assign ownership and review process.

### Phase 1 (weeks 2-3): foundations

- Implement base token set.
- Build `AppShell`, `TopNav`, `SidePanel`, `BottomDrawer`.
- Validate responsive and accessibility baselines.

### Phase 2 (weeks 4-6): workflow components

- Build Create workflow components.
- Build ResultCard, Timeline, CompareViewer.
- Integrate with History and Favorites screens.

### Phase 3 (weeks 7-8): hardening

- Run usability and accessibility regression.
- Measure adoption KPIs and defect trends.
- Publish `v1.0.0` MVDS release and usage guide.

## 13) Definition of done for MVDS components

A component is done only when all requirements below are met.

- Tokenized visual properties only.
- Required variants and states implemented.
- Accessibility requirements verified.
- Keyboard behavior documented and tested.
- Usage examples and anti-patterns documented.
- Changelog entry and version tag published.

## 14) Immediate next steps

1. Approve this MVDS scope and ownership.
2. Create the token package and starter component package.
3. Prioritize P0 components for the first implementation sprint.
