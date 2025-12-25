# Product Backlog Management System - Usage Guide

## Overview

The Product Backlog Management System generates, prioritizes, and manages comprehensive product backlog items with impact/effort analysis, risk assessment, and phase grouping. It includes 25+ carefully crafted backlog items across four phases: Foundation, Core Features, Enhancement, and Enterprise.

## Features

- **25+ Comprehensive Backlog Items**: Covering all aspects of the video generation platform
- **Smart Prioritization**: Automatically calculates priority based on impact/effort ratio with risk adjustment
- **Phase Organization**: Items grouped into Foundation, Core Features, Enhancement, and Enterprise phases
- **Refactor Tracking**: Identifies must-do vs later refactors with module maturity scoring
- **Multiple Export Formats**: JSON, Markdown, and HTML reports
- **Rich Filtering**: Filter by phase, owner, risk, priority, and more
- **Dependency Tracking**: Full dependency graph generation
- **Visualization Support**: Data export for charts and graphs

## Python Usage

### Basic Usage

```python
from src.core.product_backlog import ProductBacklog

# Create backlog
backlog = ProductBacklog()

# Get summary
summary = backlog.get_summary()
print(f"Total items: {summary['total_items']}")

# Get top priority items
for item in backlog.items[:10]:
    print(f"[{item.priority_score:.2f}] {item.item}")
```

### Filtering Items

```python
from src.core.product_backlog import Phase, Owner, RefactorType

# Get items by phase
foundation_items = backlog.get_by_phase(Phase.FOUNDATION)
core_items = backlog.get_by_phase(Phase.CORE_FEATURES)

# Get items by owner
rnd_items = backlog.get_by_owner(Owner.RND)
frontend_items = backlog.get_by_owner(Owner.FRONTEND)

# Get refactors
must_do_refactors = backlog.get_refactors(RefactorType.MUST_DO)
later_refactors = backlog.get_refactors(RefactorType.LATER)

# Get high priority items
high_priority = backlog.get_high_priority(threshold=1.5)

# Get low risk items
low_risk = backlog.get_by_risk(max_risk=2)
```

### Exporting Data

```python
# Export to JSON
backlog.export_json("data/product_backlog.json")

# Export to Markdown
backlog.export_markdown("docs/PRODUCT_BACKLOG.md")

# Generate dependency graph
graph = backlog.generate_dependency_graph()

# Get ready items (no dependencies)
ready = backlog.get_ready_items()
```

### Command Line Script

```bash
# Generate and display backlog
python scripts/generate_backlog.py

# Export to JSON
python scripts/generate_backlog.py --format json

# Export to Markdown
python scripts/generate_backlog.py --format markdown

# Export both formats
python scripts/generate_backlog.py --format both

# Show detailed breakdown
python scripts/generate_backlog.py --detailed

# Show only refactors
python scripts/generate_backlog.py --refactors-only
```

### Running Tests

```bash
# Run all backlog tests
python -m pytest tests/test_product_backlog.py -v

# Run specific test
python -m pytest tests/test_product_backlog.py::TestBacklogItem::test_priority_calculation_basic -v
```

## TypeScript Usage

### Basic Usage

```typescript
import { ProductBacklog } from './src/models/product-backlog';

// Create backlog
const backlog = new ProductBacklog();

// Get summary
const summary = backlog.getSummary();
console.log(`Total items: ${summary.totalItems}`);

// Get all items
const items = backlog.getAllItems();
```

### Filtering Items

```typescript
import { Phase, Owner, RefactorType } from './src/models/product-backlog';

// Get items by phase
const foundationItems = backlog.getByPhase(Phase.FOUNDATION);
const coreItems = backlog.getByPhase(Phase.CORE_FEATURES);

// Get items by owner
const rndItems = backlog.getByOwner(Owner.RND);
const frontendItems = backlog.getByOwner(Owner.FRONTEND);

// Get refactors
const mustDoRefactors = backlog.getRefactors(RefactorType.MUST_DO);
const laterRefactors = backlog.getRefactors(RefactorType.LATER);

// Get high priority items
const highPriority = backlog.getHighPriority(1.5);

// Get low risk items
const lowRisk = backlog.getByRisk(2);
```

### Exporting Data

```typescript
// Export to JSON string
const jsonData = backlog.exportJSON();
fs.writeFileSync('backlog.json', jsonData);

// Export to Markdown string
const markdown = backlog.exportMarkdown();
fs.writeFileSync('backlog.md', markdown);

// Generate dependency graph
const graph = backlog.generateDependencyGraph();

// Get ready items
const ready = backlog.getReadyItems();
```

### Visualization

```typescript
import { BacklogVisualization, generateHTMLReport } from './src/models/backlog-visualization';

// Create visualization helper
const viz = new BacklogVisualization(backlog);

// Get various chart data
const impactEffort = viz.getImpactEffortScatter();
const priorityDist = viz.getPriorityDistribution();
const phaseBreakdown = viz.getPhaseBreakdown();
const ownerWorkload = viz.getOwnerWorkload();
const riskAnalysis = viz.getRiskAnalysis();
const dependencyGraph = viz.getDependencyGraph();
const refactorMatrix = viz.getRefactorMatrix();
const timeline = viz.getTimelineView();
const burndown = viz.getBurndownProjection(velocityPerSprint: 20);

// Export all visualization data
const vizData = viz.exportVisualizationData();

// Generate HTML report
const htmlReport = generateHTMLReport(backlog);
fs.writeFileSync('backlog-report.html', htmlReport);
```

### Command Line Interface

```bash
# Run TypeScript CLI
node src/models/product-backlog-cli.js generate
node src/models/product-backlog-cli.js list
node src/models/product-backlog-cli.js list foundation
node src/models/product-backlog-cli.js owner RND
node src/models/product-backlog-cli.js refactors must_do
node src/models/product-backlog-cli.js priority 1.5
node src/models/product-backlog-cli.js risk 2
node src/models/product-backlog-cli.js export-json ./backlog.json
node src/models/product-backlog-cli.js export-md ./backlog.md
node src/models/product-backlog-cli.js summary
node src/models/product-backlog-cli.js dependencies
node src/models/product-backlog-cli.js ready
```

## Backlog Item Fields

Each backlog item includes:

- **item**: Description of the work item
- **impact**: Business impact score (1-5, higher is more impactful)
- **effort**: Implementation effort score (1-5, higher is more effort)
- **risk**: Technical/business risk score (1-5, higher is riskier)
- **dependencies**: List of prerequisite items
- **owner**: Responsible team (R&D, BE, FE, Design)
- **testHook**: Associated test function name
- **phase**: Development phase (foundation, core_features, enhancement, enterprise)
- **priorityScore**: Calculated priority = (impact/effort) * (1 - risk*0.1)
- **isRefactor**: Whether this is a refactoring item
- **refactorType**: must_do or later (for refactors only)
- **moduleMaturityScore**: Current module maturity (0-1, for refactors only)

## Priority Calculation

Priority score is calculated using the formula:

```
priorityScore = (impact / effort) * (1 - risk * 0.1)
```

This ensures:
- High impact, low effort items get highest priority
- Risk reduces priority proportionally
- Items are automatically sorted by priority

## Phase Organization

### Foundation (6 items)
Core infrastructure and architecture that everything else depends on.

### Core Features (8 items)
Essential features that define the product's core value proposition.

### Enhancement (9 items)
Additional features that improve user experience and capabilities.

### Enterprise (9 items)
Advanced features for enterprise customers and scalability.

## Refactor Items

The system tracks refactor items with maturity scores:

### Must-Do Refactors (4 items)
Critical refactors with low maturity scores (<0.6) that should be prioritized:
- Modularize Video Model Abstraction Layer (0.45)
- Decouple Prompt Expansion Logic (0.52)
- Extract Image Generator into Standalone Service (0.48)

### Later Refactors (2 items)
Optimization refactors with decent maturity (>0.6) that can be deferred:
- Optimize Analyzer Pipeline for Performance (0.68)
- Migrate to Microservices Architecture (0.72)

## Owner Distribution

- **R&D**: Research and algorithm development (8 items)
- **Backend (BE)**: Server-side implementation (11 items)
- **Frontend (FE)**: User interface development (4 items)
- **Design**: UX and visual design (1 item)

## Integration with Development Workflow

### Sprint Planning
```python
# Get ready items for sprint planning
ready_items = backlog.get_ready_items()

# Filter by team capacity
rnd_capacity = backlog.get_by_owner(Owner.RND)
high_priority_rnd = [item for item in rnd_capacity if item.priority_score >= 1.5]
```

### Risk Management
```python
# Identify high-risk items requiring extra attention
high_risk = [item for item in backlog.items if item.risk >= 4]

# Balance risk with low-risk quick wins
quick_wins = backlog.get_by_risk(max_risk=2)
quick_wins = backlog.get_high_priority(threshold=1.5)
```

### Refactor Planning
```python
# Prioritize must-do refactors
must_refactor = backlog.get_refactors(RefactorType.MUST_DO)
sorted_refactors = sorted(must_refactor, key=lambda x: x.module_maturity_score)
```

## Best Practices

1. **Review Priority Regularly**: Recalculate priorities as business needs change
2. **Update Dependencies**: Keep dependency graph current as items complete
3. **Track Maturity**: Monitor module maturity scores for refactor candidates
4. **Balance Risk**: Mix high-risk and low-risk items in each sprint
5. **Cross-Team Coordination**: Use owner filtering for capacity planning
6. **Export for Stakeholders**: Generate reports for different audiences
7. **Test Coverage**: Ensure all items have associated test hooks

## Examples

### Find Quick Wins
```python
quick_wins = [
    item for item in backlog.items
    if item.impact >= 4 and item.effort <= 2 and item.risk <= 2
]
```

### Critical Path Analysis
```python
foundation = backlog.get_by_phase(Phase.FOUNDATION)
critical_path = sorted(foundation, key=lambda x: len(x.dependencies), reverse=True)
```

### Team Workload Balance
```python
for owner in Owner:
    items = backlog.get_by_owner(owner)
    total_effort = sum(item.effort for item in items)
    print(f"{owner.value}: {len(items)} items, {total_effort} effort points")
```

### Sprint Velocity Tracking
```typescript
const viz = new BacklogVisualization(backlog);
const projection = viz.getBurndownProjection(velocityPerSprint: 25);
console.log(`Estimated completion: ${projection[projection.length - 1].sprint} sprints`);
```

## Support

For issues or questions about the backlog system:
- Review this documentation
- Check the test files for usage examples
- Examine the generated exports (JSON/Markdown)
- Consult the visualization data for insights
