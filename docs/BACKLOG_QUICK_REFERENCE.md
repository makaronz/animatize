> [!WARNING]
> **DEPRECATED / OUTDATED**: This document may contain historical flows and commands that are not the canonical runtime path anymore.
> Use **README.md** for onboarding and runtime startup, **docs/API.md** for endpoints, **docs/ARCHITECTURE.md** for system flow, and **docs/OPERATIONS.md** for troubleshooting.

# Product Backlog Quick Reference

## Import & Setup

### Python
```python
from src.core.product_backlog import ProductBacklog, Phase, Owner, RefactorType
backlog = ProductBacklog()
```

### TypeScript
```typescript
import { ProductBacklog, Phase, Owner, RefactorType } from './src/models/product-backlog';
const backlog = new ProductBacklog();
```

## Common Operations

### Get Items
```python
all_items = backlog.items                           # All items (sorted by priority)
foundation = backlog.get_by_phase(Phase.FOUNDATION) # By phase
rnd_items = backlog.get_by_owner(Owner.RND)         # By owner
refactors = backlog.get_refactors()                 # All refactors
must_do = backlog.get_refactors(RefactorType.MUST_DO) # Must-do refactors
high_pri = backlog.get_high_priority(1.5)           # Priority >= 1.5
low_risk = backlog.get_by_risk(2)                   # Risk <= 2
ready = backlog.get_ready_items()                   # No dependencies
```

### Export
```python
backlog.export_json("data/backlog.json")
backlog.export_markdown("docs/backlog.md")
summary = backlog.get_summary()
graph = backlog.generate_dependency_graph()
```

## CLI Commands

### Python
```bash
python scripts/generate_backlog.py                    # Display summary
python scripts/generate_backlog.py --format json      # Export JSON
python scripts/generate_backlog.py --format markdown  # Export Markdown
python scripts/generate_backlog.py --format both      # Export both
python scripts/generate_backlog.py --detailed         # Show detailed breakdown
python scripts/generate_backlog.py --refactors-only   # Show only refactors
```

### TypeScript
```bash
node src/models/product-backlog-cli.js generate       # Summary
node src/models/product-backlog-cli.js list           # All items
node src/models/product-backlog-cli.js list foundation # By phase
node src/models/product-backlog-cli.js owner RND      # By owner
node src/models/product-backlog-cli.js refactors must_do # Refactors
node src/models/product-backlog-cli.js priority 1.5   # By priority
node src/models/product-backlog-cli.js risk 2         # By risk
node src/models/product-backlog-cli.js export-json ./backlog.json
node src/models/product-backlog-cli.js export-md ./backlog.md
node src/models/product-backlog-cli.js dependencies   # Dependency graph
node src/models/product-backlog-cli.js ready          # Ready items
```

## Enums

### Phase
- `Phase.FOUNDATION`
- `Phase.CORE_FEATURES`
- `Phase.ENHANCEMENT`
- `Phase.ENTERPRISE`

### Owner
- `Owner.RND` (R&D)
- `Owner.BACKEND` (BE)
- `Owner.FRONTEND` (FE)
- `Owner.DESIGN`

### RefactorType
- `RefactorType.MUST_DO`
- `RefactorType.LATER`

## Item Fields

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| item | string | - | Description |
| impact | int | 1-5 | Business impact |
| effort | int | 1-5 | Implementation effort |
| risk | int | 1-5 | Technical/business risk |
| dependencies | list | - | Prerequisite items |
| owner | Owner | - | Responsible team |
| testHook | string | - | Test function name |
| phase | Phase | - | Development phase |
| priorityScore | float | - | Calculated priority |
| isRefactor | bool | - | Is refactor? |
| refactorType | RefactorType | - | Must-do or later |
| moduleMaturityScore | float | 0-1 | Current maturity |

## Priority Formula

```
priorityScore = (impact / effort) × (1 - risk × 0.1)
```

## Filtering Patterns

### Sprint Planning
```python
ready = backlog.get_ready_items()
sprint = [i for i in ready if i.priority_score >= 1.5][:5]
```

### Quick Wins
```python
wins = [i for i in backlog.items if i.effort <= 2 and i.impact >= 4 and i.risk <= 2]
```

### Critical Refactors
```python
critical = sorted(
    backlog.get_refactors(RefactorType.MUST_DO),
    key=lambda x: x.module_maturity_score
)
```

### Team Workload
```python
for owner in Owner:
    items = backlog.get_by_owner(owner)
    effort = sum(i.effort for i in items)
    print(f"{owner.value}: {len(items)} items, {effort} points")
```

### High-Impact Foundation
```python
foundation = backlog.get_by_phase(Phase.FOUNDATION)
high_impact = [i for i in foundation if i.impact >= 4]
```

## Summary Fields

- `total_items`: Total backlog items
- `foundation_items`: Foundation phase count
- `core_features_items`: Core features count
- `enhancement_items`: Enhancement count
- `enterprise_items`: Enterprise count
- `must_do_refactors`: Must-do refactor count
- `later_refactors`: Later refactor count
- `high_impact_items`: Items with impact >= 4
- `high_risk_items`: Items with risk >= 4
- `avg_priority_score`: Average priority

## Visualization (TypeScript)

```typescript
import { BacklogVisualization, generateHTMLReport } from './src/models/backlog-visualization';

const viz = new BacklogVisualization(backlog);

// Get chart data
viz.getImpactEffortScatter()      // Scatter plot
viz.getPriorityDistribution()     // Distribution chart
viz.getPhaseBreakdown()           // Phase pie chart
viz.getOwnerWorkload()            // Team workload
viz.getRiskAnalysis()             // Risk breakdown
viz.getDependencyGraph()          // Graph nodes/edges
viz.getRefactorMatrix()           // Refactor analysis
viz.getTimelineView()             // Timeline data
viz.getBurndownProjection(20)     // Burndown (velocity=20)

// Generate report
const html = generateHTMLReport(backlog);
fs.writeFileSync('report.html', html);
```

## Test Hooks

All items have test hooks following this pattern:
```
test_<feature>_<aspect>
```

Examples:
- `test_video_pipeline_integration`
- `test_model_abstraction_isolation`
- `test_auth_security_compliance`
- `test_scene_analyzer_accuracy`
- `test_movement_prediction_precision`

## Examples

Run examples:
```bash
python examples/backlog_example.py
```

Includes:
1. Basic usage
2. Sprint planning
3. Risk management
4. Refactor planning
5. Team workload
6. Phase progression
7. Dependency analysis
8. Custom filtering
9. Export operations

## Tests

Run tests:
```bash
python -m pytest tests/test_product_backlog.py -v
python -m pytest tests/test_product_backlog.py --cov
```

## Documentation

- **README**: `docs/PRODUCT_BACKLOG_README.md`
- **Usage Guide**: `docs/BACKLOG_USAGE.md`
- **Implementation**: `docs/BACKLOG_IMPLEMENTATION_SUMMARY.md`
- **Quick Ref**: `docs/BACKLOG_QUICK_REFERENCE.md` (this file)

## Key Numbers

- **Total Items**: 32
- **Phases**: 4 (Foundation, Core Features, Enhancement, Enterprise)
- **Teams**: 4 (R&D, Backend, Frontend, Design)
- **Refactors**: 6 (4 must-do, 2 later)
- **Avg Priority**: ~0.85
- **Total Effort**: 122 points

## Common Issues

### Import Error
```python
# Add to path if needed
import sys
sys.path.insert(0, 'path/to/repo')
from src.core.product_backlog import ProductBacklog
```

### File Not Found
```python
# Create directories
import os
os.makedirs('data', exist_ok=True)
os.makedirs('docs', exist_ok=True)
```

### Priority Recalculation
```python
# Manually recalculate if fields change
for item in backlog.items:
    item.calculate_priority()
backlog.items.sort(key=lambda x: x.priority_score, reverse=True)
```
