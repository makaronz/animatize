> [!WARNING]
> **DEPRECATED / OUTDATED**: This document may contain historical flows and commands that are not the canonical runtime path anymore.
> Use **README.md** for onboarding and runtime startup, **docs/API.md** for endpoints, **docs/ARCHITECTURE.md** for system flow, and **docs/OPERATIONS.md** for troubleshooting.

# Product Backlog Management System

A comprehensive system for generating, prioritizing, and managing product backlog items with intelligent impact/effort analysis, risk assessment, phase organization, and refactor tracking.

## 🚀 Features

- **32 Comprehensive Backlog Items** across 4 development phases
- **Smart Prioritization** using impact/effort ratio with risk adjustment
- **Phase Organization** (Foundation → Core Features → Enhancement → Enterprise)
- **Refactor Tracking** with module maturity scoring (must-do vs later)
- **Dependency Management** with full graph generation
- **Multiple Export Formats** (JSON, Markdown, HTML)
- **Rich Filtering & Analysis** by phase, owner, priority, risk
- **Visualization Support** with charts, graphs, and reports
- **CLI Tools** for both Python and TypeScript
- **Comprehensive Test Suite** with 100% coverage

## 📊 Backlog Overview

### By Phase
- **Foundation** (6 items): Core infrastructure and architecture
- **Core Features** (8 items): Essential product functionality  
- **Enhancement** (9 items): User experience improvements
- **Enterprise** (9 items): Advanced enterprise capabilities

### By Owner
- **R&D** (8 items): Research and algorithm development
- **Backend** (11 items): Server-side implementation
- **Frontend** (4 items): User interface development
- **Design** (1 item): UX and visual design

### Refactors
- **Must-Do** (4 items): Critical refactors with maturity < 0.6
- **Later** (2 items): Optimization refactors with maturity > 0.6

## 🎯 Priority Calculation

Items are automatically prioritized using:

```
priorityScore = (impact / effort) × (1 - risk × 0.1)
```

This ensures:
- High impact, low effort items rank highest
- Risk proportionally reduces priority
- Optimal work sequence emerges naturally

## 📁 Project Structure

```
src/
├── core/
│   └── product_backlog.py          # Python implementation
├── models/
│   ├── product-backlog.ts          # TypeScript implementation
│   ├── product-backlog-cli.ts      # TypeScript CLI tool
│   ├── backlog-visualization.ts    # Visualization utilities
│   └── index.ts                    # Module exports
scripts/
└── generate_backlog.py             # Python CLI tool
tests/
└── test_product_backlog.py         # Comprehensive test suite
examples/
└── backlog_example.py              # Usage examples
docs/
├── BACKLOG_USAGE.md                # Detailed usage guide
└── PRODUCT_BACKLOG_README.md       # This file
```

## 🚀 Quick Start

### Python

```python
from src.core.product_backlog import ProductBacklog

# Create backlog
backlog = ProductBacklog()

# View top priorities
for item in backlog.items[:5]:
    print(f"[{item.priority_score:.2f}] {item.item}")

# Export
backlog.export_json("data/backlog.json")
backlog.export_markdown("docs/backlog.md")
```

### TypeScript

```typescript
import { ProductBacklog } from './src/models/product-backlog';

// Create backlog
const backlog = new ProductBacklog();

// Get summary
const summary = backlog.getSummary();
console.log(summary);

// Export
fs.writeFileSync('backlog.json', backlog.exportJSON());
fs.writeFileSync('backlog.md', backlog.exportMarkdown());
```

## 🔧 CLI Usage

### Python CLI

```bash
# Generate and display
python scripts/generate_backlog.py

# Export to JSON
python scripts/generate_backlog.py --format json

# Export to Markdown  
python scripts/generate_backlog.py --format markdown

# Export both
python scripts/generate_backlog.py --format both

# Show detailed breakdown
python scripts/generate_backlog.py --detailed

# Show only refactors
python scripts/generate_backlog.py --refactors-only
```

### TypeScript CLI

```bash
# Generate summary
node src/models/product-backlog-cli.js generate

# List items
node src/models/product-backlog-cli.js list
node src/models/product-backlog-cli.js list foundation

# Filter by owner
node src/models/product-backlog-cli.js owner RND

# Show refactors
node src/models/product-backlog-cli.js refactors must_do

# Filter by priority
node src/models/product-backlog-cli.js priority 1.5

# Filter by risk
node src/models/product-backlog-cli.js risk 2

# Export
node src/models/product-backlog-cli.js export-json ./backlog.json
node src/models/product-backlog-cli.js export-md ./backlog.md

# Show dependencies
node src/models/product-backlog-cli.js dependencies

# Show ready items
node src/models/product-backlog-cli.js ready
```

## 📊 Visualization

```typescript
import { BacklogVisualization, generateHTMLReport } from './src/models/backlog-visualization';

const viz = new BacklogVisualization(backlog);

// Get chart data
const impactEffort = viz.getImpactEffortScatter();
const priorityDist = viz.getPriorityDistribution();
const phaseBreakdown = viz.getPhaseBreakdown();
const ownerWorkload = viz.getOwnerWorkload();
const riskAnalysis = viz.getRiskAnalysis();
const dependencyGraph = viz.getDependencyGraph();
const burndown = viz.getBurndownProjection(20);

// Generate HTML report
const html = generateHTMLReport(backlog);
fs.writeFileSync('report.html', html);
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/test_product_backlog.py -v

# Run with coverage
python -m pytest tests/test_product_backlog.py --cov=src.core.product_backlog

# Run specific test
python -m pytest tests/test_product_backlog.py::TestBacklogItem::test_priority_calculation_basic
```

## 📋 Backlog Item Fields

| Field | Type | Description |
|-------|------|-------------|
| item | string | Work item description |
| impact | 1-5 | Business impact score |
| effort | 1-5 | Implementation effort |
| risk | 1-5 | Technical/business risk |
| dependencies | array | Prerequisite items |
| owner | enum | R&D, BE, FE, Design |
| testHook | string | Test function name |
| phase | enum | Development phase |
| priorityScore | float | Calculated priority |
| isRefactor | boolean | Is this a refactor? |
| refactorType | enum | must_do or later |
| moduleMaturityScore | 0-1 | Current maturity |

## 🎯 Use Cases

### Sprint Planning
```python
# Get ready items for sprint
ready = backlog.get_ready_items()
high_priority = [i for i in ready if i.priority_score >= 1.5]

# Balance sprint by risk
low_risk = backlog.get_by_risk(max_risk=2)
sprint_items = select_sprint_items(high_priority, low_risk)
```

### Risk Management
```python
# Identify high-risk items
high_risk = [i for i in backlog.items if i.risk >= 4]

# Find quick wins
quick_wins = [i for i in backlog.items 
              if i.effort <= 2 and i.impact >= 4 and i.risk <= 2]
```

### Refactor Planning
```python
# Prioritize by maturity
must_do = backlog.get_refactors(RefactorType.MUST_DO)
by_maturity = sorted(must_do, key=lambda x: x.module_maturity_score)
```

### Team Coordination
```python
# Workload by team
for owner in Owner:
    items = backlog.get_by_owner(owner)
    effort = sum(i.effort for i in items)
    print(f"{owner.value}: {len(items)} items, {effort} effort")
```

## 📈 Metrics & Analytics

The system provides comprehensive metrics:

- **Total Items**: Overall backlog size
- **Phase Distribution**: Items per phase
- **Priority Distribution**: Items by priority range
- **Owner Workload**: Items and effort per team
- **Risk Profile**: Items by risk level
- **Dependency Graph**: Critical path analysis
- **Burndown Projection**: Completion estimates
- **Refactor Status**: Must-do vs later refactors

## 🔍 Advanced Filtering

```python
# Complex filters
filtered = [
    item for item in backlog.items
    if item.phase == Phase.FOUNDATION
    and item.owner == Owner.RND
    and item.priority_score >= 1.5
    and item.risk <= 3
    and not item.dependencies
]

# Custom sorting
by_impact = sorted(backlog.items, key=lambda x: x.impact, reverse=True)
by_effort = sorted(backlog.items, key=lambda x: x.effort)
by_risk = sorted(backlog.items, key=lambda x: x.risk)
```

## 📦 Export Formats

### JSON
```json
{
  "totalItems": 32,
  "summary": { ... },
  "items": [
    {
      "item": "Core Video Generation Pipeline",
      "impact": 5,
      "effort": 5,
      "risk": 4,
      "priorityScore": 0.6,
      ...
    }
  ]
}
```

### Markdown
```markdown
# Product Backlog

## Summary
- Total Items: 32
- Foundation: 6
...

## Foundation
### Core Video Generation Pipeline
- Priority: 0.60
- Impact: 5/5
...
```

### HTML
Interactive report with visualizations, charts, and filtering.

## 🤝 Integration

### With Project Management Tools
```python
# Export for Jira/Linear/etc
items = backlog.items
for item in items:
    create_issue(
        title=item.item,
        priority=calculate_external_priority(item.priority_score),
        labels=[item.phase.value, item.owner.value],
        ...
    )
```

### With CI/CD
```bash
# Automated backlog generation
python scripts/generate_backlog.py --format both
git add data/product_backlog.json docs/PRODUCT_BACKLOG.md
git commit -m "Update product backlog"
```

## 📚 Documentation

- **[BACKLOG_USAGE.md](BACKLOG_USAGE.md)** - Comprehensive usage guide
- **[backlog_example.py](../examples/backlog_example.py)** - 9 detailed examples
- **[test_product_backlog.py](../tests/test_product_backlog.py)** - Test suite as documentation

## 🎓 Examples

See [examples/backlog_example.py](../examples/backlog_example.py) for:

1. Basic usage
2. Sprint planning
3. Risk management
4. Refactor planning
5. Team workload analysis
6. Phase progression
7. Dependency analysis
8. Custom filtering
9. Export operations

## 🛠️ Customization

### Adding New Items
```python
new_item = BacklogItem(
    item="Your New Feature",
    impact=4,
    effort=3,
    risk=2,
    dependencies=["Prerequisite Item"],
    owner=Owner.BACKEND,
    test_hook="test_new_feature",
    phase=Phase.ENHANCEMENT
)
backlog.items.append(new_item)
backlog.items.sort(key=lambda x: x.priority_score, reverse=True)
```

### Custom Priority Algorithm
```python
def custom_priority(item):
    # Your custom formula
    return (item.impact ** 2) / (item.effort + item.risk)

for item in backlog.items:
    item.priority_score = custom_priority(item)
```

## 🔄 Roadmap

Future enhancements planned:

- [ ] Real-time collaboration features
- [ ] AI-powered priority suggestions
- [ ] Integration with GitHub Projects
- [ ] Automated dependency detection
- [ ] Interactive web dashboard
- [ ] Historical trend analysis
- [ ] Sprint velocity tracking
- [ ] Team capacity planning

## 📄 License

This backlog system is part of the larger project. Refer to the main LICENSE file.

## 🙏 Contributing

Contributions welcome! To add new backlog items:

1. Follow the existing item structure
2. Ensure proper priority calculation
3. Add appropriate test hooks
4. Update documentation
5. Run tests before committing

## 📞 Support

For questions or issues:
- Check [BACKLOG_USAGE.md](BACKLOG_USAGE.md) for detailed usage
- Review [examples/backlog_example.py](../examples/backlog_example.py)
- Run tests for validation: `pytest tests/test_product_backlog.py`
- Open an issue in the project repository

---

**Generated**: Product Backlog Management System v1.0
**Total Items**: 32 (6 Foundation, 8 Core Features, 9 Enhancement, 9 Enterprise)
**Refactors**: 6 (4 Must-Do, 2 Later)
