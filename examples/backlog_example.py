#!/usr/bin/env python3
"""
Example usage of Product Backlog Management System

This demonstrates various ways to use the backlog system
for sprint planning, risk management, and team coordination.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.product_backlog import ProductBacklog, Phase, Owner, RefactorType


def example_basic_usage():
    """Example 1: Basic backlog usage"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Backlog Usage")
    print("="*70 + "\n")
    
    backlog = ProductBacklog()
    
    print(f"Total backlog items: {len(backlog.items)}")
    print("\nTop 5 priority items:")
    for i, item in enumerate(backlog.items[:5], 1):
        print(f"{i}. [{item.priority_score:.2f}] {item.item}")
        print(f"   Impact: {item.impact}, Effort: {item.effort}, Risk: {item.risk}")


def example_sprint_planning():
    """Example 2: Sprint planning scenario"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Sprint Planning")
    print("="*70 + "\n")
    
    backlog = ProductBacklog()
    
    # Define sprint capacity
    SPRINT_CAPACITY = 20  # effort points
    
    # Get ready items (no dependencies blocking)
    ready_items = backlog.get_ready_items()
    print(f"Items ready to start: {len(ready_items)}")
    
    # Select items for sprint
    sprint_items = []
    total_effort = 0
    
    for item in ready_items:
        if total_effort + item.effort <= SPRINT_CAPACITY:
            sprint_items.append(item)
            total_effort += item.effort
    
    print(f"\nSprint backlog ({total_effort}/{SPRINT_CAPACITY} effort points):")
    for item in sprint_items:
        print(f"  • [{item.priority_score:.2f}] {item.item}")
        print(f"    Effort: {item.effort}, Owner: {item.owner.value}")


def example_risk_management():
    """Example 3: Risk management and mitigation"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Risk Management")
    print("="*70 + "\n")
    
    backlog = ProductBacklog()
    
    # Identify high-risk items
    high_risk = [item for item in backlog.items if item.risk >= 4]
    print(f"High-risk items (risk >= 4): {len(high_risk)}")
    for item in high_risk:
        print(f"  • [{item.risk}/5] {item.item}")
        print(f"    Phase: {item.phase.value}, Priority: {item.priority_score:.2f}")
    
    # Find low-risk quick wins
    print("\nLow-risk quick wins (risk <= 2, effort <= 3, impact >= 4):")
    quick_wins = [
        item for item in backlog.items
        if item.risk <= 2 and item.effort <= 3 and item.impact >= 4
    ]
    for item in quick_wins[:5]:
        print(f"  • {item.item}")
        print(f"    Priority: {item.priority_score:.2f}, Effort: {item.effort}")


def example_refactor_planning():
    """Example 4: Refactor prioritization"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Refactor Planning")
    print("="*70 + "\n")
    
    backlog = ProductBacklog()
    
    # Must-do refactors
    must_do = backlog.get_refactors(RefactorType.MUST_DO)
    print(f"Must-do refactors: {len(must_do)}")
    print("(Sorted by module maturity - lowest first)")
    
    sorted_refactors = sorted(must_do, key=lambda x: x.module_maturity_score)
    for item in sorted_refactors:
        print(f"  • {item.item}")
        print(f"    Maturity: {item.module_maturity_score:.2f}, "
              f"Priority: {item.priority_score:.2f}")
        print(f"    Phase: {item.phase.value}")
    
    # Later refactors
    later = backlog.get_refactors(RefactorType.LATER)
    print(f"\nLater refactors: {len(later)}")
    for item in later:
        print(f"  • {item.item}")
        print(f"    Maturity: {item.module_maturity_score:.2f}, "
              f"Priority: {item.priority_score:.2f}")


def example_team_workload():
    """Example 5: Team workload distribution"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Team Workload Analysis")
    print("="*70 + "\n")
    
    backlog = ProductBacklog()
    
    print("Workload by team:\n")
    for owner in Owner:
        items = backlog.get_by_owner(owner)
        total_effort = sum(item.effort for item in items)
        avg_priority = sum(item.priority_score for item in items) / len(items)
        
        print(f"{owner.value}:")
        print(f"  Items: {len(items)}")
        print(f"  Total Effort: {total_effort} points")
        print(f"  Avg Priority: {avg_priority:.2f}")
        print(f"  Top Item: {items[0].item if items else 'N/A'}")
        print()


def example_phase_progression():
    """Example 6: Phase-based development progression"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Phase Progression")
    print("="*70 + "\n")
    
    backlog = ProductBacklog()
    
    for phase in Phase:
        items = backlog.get_by_phase(phase)
        total_effort = sum(item.effort for item in items)
        avg_impact = sum(item.impact for item in items) / len(items)
        
        print(f"{phase.value.upper().replace('_', ' ')}:")
        print(f"  Items: {len(items)}")
        print(f"  Total Effort: {total_effort} points")
        print(f"  Avg Impact: {avg_impact:.1f}/5")
        print(f"  Ready to start: {len([i for i in items if not i.dependencies])}")
        print()


def example_dependency_analysis():
    """Example 7: Dependency graph analysis"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Dependency Analysis")
    print("="*70 + "\n")
    
    backlog = ProductBacklog()
    
    # Find items with most dependencies
    items_with_deps = [item for item in backlog.items if item.dependencies]
    sorted_by_deps = sorted(items_with_deps, key=lambda x: len(x.dependencies), reverse=True)
    
    print("Items with most dependencies (critical path candidates):\n")
    for item in sorted_by_deps[:5]:
        print(f"• {item.item}")
        print(f"  Dependencies: {len(item.dependencies)}")
        print(f"  Depends on: {', '.join(item.dependencies[:3])}")
        if len(item.dependencies) > 3:
            print(f"  ... and {len(item.dependencies) - 3} more")
        print()
    
    # Items that other items depend on
    graph = backlog.generate_dependency_graph()
    dependency_count = {}
    for item_name, deps in graph.items():
        for dep in deps:
            dependency_count[dep] = dependency_count.get(dep, 0) + 1
    
    if dependency_count:
        print("\nMost critical items (blocking other work):\n")
        sorted_critical = sorted(dependency_count.items(), key=lambda x: x[1], reverse=True)
        for item_name, count in sorted_critical[:5]:
            print(f"• {item_name}")
            print(f"  Blocks {count} other item(s)")


def example_custom_filtering():
    """Example 8: Custom filtering scenarios"""
    print("\n" + "="*70)
    print("EXAMPLE 8: Custom Filtering")
    print("="*70 + "\n")
    
    backlog = ProductBacklog()
    
    # High-impact foundation work
    print("High-impact foundation work (impact >= 4, foundation phase):")
    foundation = backlog.get_by_phase(Phase.FOUNDATION)
    high_impact_foundation = [item for item in foundation if item.impact >= 4]
    for item in high_impact_foundation:
        print(f"  • {item.item}")
        print(f"    Priority: {item.priority_score:.2f}, Owner: {item.owner.value}")
    
    # Frontend items in enhancement phase
    print("\nFrontend enhancement work:")
    frontend = backlog.get_by_owner(Owner.FRONTEND)
    enhancement = backlog.get_by_phase(Phase.ENHANCEMENT)
    frontend_enhancement = [item for item in frontend if item in enhancement]
    for item in frontend_enhancement:
        print(f"  • {item.item}")
        print(f"    Priority: {item.priority_score:.2f}")
    
    # Items with no dependencies and high priority
    print("\nQuick high-priority wins (no deps, priority >= 1.5):")
    no_deps = [item for item in backlog.items if not item.dependencies]
    quick_high_priority = [item for item in no_deps if item.priority_score >= 1.5]
    for item in quick_high_priority[:5]:
        print(f"  • [{item.priority_score:.2f}] {item.item}")
        print(f"    Owner: {item.owner.value}, Effort: {item.effort}")


def example_export_usage():
    """Example 9: Exporting backlog data"""
    print("\n" + "="*70)
    print("EXAMPLE 9: Export Operations")
    print("="*70 + "\n")
    
    backlog = ProductBacklog()
    
    # Create directories if they don't exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    
    # Export to JSON
    backlog.export_json("data/backlog_example.json")
    print("✓ Exported to data/backlog_example.json")
    
    # Export to Markdown
    backlog.export_markdown("docs/backlog_example.md")
    print("✓ Exported to docs/backlog_example.md")
    
    # Get summary for reporting
    summary = backlog.get_summary()
    print("\nBacklog Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("PRODUCT BACKLOG MANAGEMENT SYSTEM - EXAMPLES")
    print("="*70)
    
    examples = [
        example_basic_usage,
        example_sprint_planning,
        example_risk_management,
        example_refactor_planning,
        example_team_workload,
        example_phase_progression,
        example_dependency_analysis,
        example_custom_filtering,
        example_export_usage
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
