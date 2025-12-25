#!/usr/bin/env python3
"""
Script to generate and export product backlog

Usage:
    python scripts/generate_backlog.py
    python scripts/generate_backlog.py --format json
    python scripts/generate_backlog.py --format markdown
    python scripts/generate_backlog.py --format both
"""

import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.product_backlog import ProductBacklog, Phase, Owner, RefactorType


def display_summary(backlog: ProductBacklog):
    """Display backlog summary to console"""
    summary = backlog.get_summary()
    
    print("\n" + "="*60)
    print("PRODUCT BACKLOG SUMMARY")
    print("="*60 + "\n")
    
    print(f"Total Items: {summary['total_items']}")
    print(f"Foundation Items: {summary['foundation_items']}")
    print(f"Core Features Items: {summary['core_features_items']}")
    print(f"Enhancement Items: {summary['enhancement_items']}")
    print(f"Enterprise Items: {summary['enterprise_items']}")
    print(f"Must-Do Refactors: {summary['must_do_refactors']}")
    print(f"Later Refactors: {summary['later_refactors']}")
    print(f"High Impact Items (4+): {summary['high_impact_items']}")
    print(f"High Risk Items (4+): {summary['high_risk_items']}")
    print(f"Avg Priority Score: {summary['avg_priority_score']:.2f}")


def display_top_items(backlog: ProductBacklog, count: int = 10):
    """Display top priority items"""
    print("\n" + "="*60)
    print(f"TOP {count} PRIORITY ITEMS")
    print("="*60 + "\n")
    
    for i, item in enumerate(backlog.items[:count], 1):
        print(f"{i}. [{item.priority_score:.2f}] {item.item}")
        print(f"   Owner: {item.owner.value} | "
              f"Impact: {item.impact}/5 | "
              f"Effort: {item.effort}/5 | "
              f"Risk: {item.risk}/5")
        if item.is_refactor:
            print(f"   Refactor: {item.refactor_type.value} | "
                  f"Maturity: {item.module_maturity_score}")
        print()


def display_refactors(backlog: ProductBacklog):
    """Display refactor items grouped by type"""
    print("\n" + "="*60)
    print("REFACTOR ITEMS")
    print("="*60 + "\n")
    
    must_do = backlog.get_refactors(RefactorType.MUST_DO)
    print(f"MUST-DO REFACTORS ({len(must_do)} items):")
    for item in must_do:
        print(f"  • {item.item}")
        print(f"    Maturity: {item.module_maturity_score} | "
              f"Priority: {item.priority_score:.2f} | "
              f"Phase: {item.phase.value}")
    
    print()
    later = backlog.get_refactors(RefactorType.LATER)
    print(f"LATER REFACTORS ({len(later)} items):")
    for item in later:
        print(f"  • {item.item}")
        print(f"    Maturity: {item.module_maturity_score} | "
              f"Priority: {item.priority_score:.2f} | "
              f"Phase: {item.phase.value}")


def display_by_phase(backlog: ProductBacklog):
    """Display items grouped by phase"""
    print("\n" + "="*60)
    print("ITEMS BY PHASE")
    print("="*60 + "\n")
    
    for phase in Phase:
        items = backlog.get_by_phase(phase)
        print(f"{phase.value.upper().replace('_', ' ')} ({len(items)} items):")
        for item in items:
            marker = "⚙️" if item.is_refactor else "📋"
            print(f"  {marker} [{item.priority_score:.2f}] {item.item}")
        print()


def display_by_owner(backlog: ProductBacklog):
    """Display items grouped by owner"""
    print("\n" + "="*60)
    print("ITEMS BY OWNER")
    print("="*60 + "\n")
    
    for owner in Owner:
        items = backlog.get_by_owner(owner)
        print(f"{owner.value} ({len(items)} items):")
        for item in items:
            print(f"  • [{item.priority_score:.2f}] {item.item} - {item.phase.value}")
        print()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Generate and export product backlog'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'markdown', 'both', 'console'],
        default='console',
        help='Export format (default: console)'
    )
    parser.add_argument(
        '--json-path',
        default='data/product_backlog.json',
        help='Path for JSON export'
    )
    parser.add_argument(
        '--md-path',
        default='docs/PRODUCT_BACKLOG.md',
        help='Path for Markdown export'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed breakdown by phase and owner'
    )
    parser.add_argument(
        '--refactors-only',
        action='store_true',
        help='Show only refactor items'
    )
    
    args = parser.parse_args()
    
    # Generate backlog
    print("Generating product backlog...")
    backlog = ProductBacklog()
    
    # Display to console
    if args.format == 'console' or args.format == 'both':
        display_summary(backlog)
        
        if args.refactors_only:
            display_refactors(backlog)
        else:
            display_top_items(backlog)
            display_refactors(backlog)
            
            if args.detailed:
                display_by_phase(backlog)
                display_by_owner(backlog)
    
    # Export to JSON
    if args.format in ['json', 'both']:
        # Ensure directory exists
        os.makedirs(os.path.dirname(args.json_path), exist_ok=True)
        backlog.export_json(args.json_path)
        print(f"\n✓ Exported to {args.json_path}")
    
    # Export to Markdown
    if args.format in ['markdown', 'both']:
        # Ensure directory exists
        os.makedirs(os.path.dirname(args.md_path), exist_ok=True)
        backlog.export_markdown(args.md_path)
        print(f"✓ Exported to {args.md_path}")
    
    print("\nBacklog generation complete!")


if __name__ == "__main__":
    main()
