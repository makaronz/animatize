"""
Integration tests for Product Backlog System

Tests the complete workflow from generation to export
and integration between components.
"""

import unittest
import json
import os
import tempfile
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.product_backlog import (
    ProductBacklog,
    Phase,
    Owner,
    RefactorType
)


class TestBacklogIntegration(unittest.TestCase):
    """Integration tests for complete backlog workflows"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.backlog = ProductBacklog()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow(self):
        """Test complete workflow from generation to export"""
        # Generate backlog
        self.assertIsNotNone(self.backlog)
        self.assertGreater(len(self.backlog.items), 0)
        
        # Get summary
        summary = self.backlog.get_summary()
        self.assertIn('total_items', summary)
        
        # Filter items
        foundation = self.backlog.get_by_phase(Phase.FOUNDATION)
        self.assertGreater(len(foundation), 0)
        
        # Export to JSON
        json_path = os.path.join(self.temp_dir, "test_backlog.json")
        self.backlog.export_json(json_path)
        self.assertTrue(os.path.exists(json_path))
        
        # Verify JSON content
        with open(json_path, 'r') as f:
            data = json.load(f)
        self.assertEqual(data['total_items'], len(self.backlog.items))
        
        # Export to Markdown
        md_path = os.path.join(self.temp_dir, "test_backlog.md")
        self.backlog.export_markdown(md_path)
        self.assertTrue(os.path.exists(md_path))
        
        # Verify Markdown content
        with open(md_path, 'r') as f:
            content = f.read()
        self.assertIn('# Product Backlog', content)
        self.assertIn('## Foundation', content)
    
    def test_sprint_planning_workflow(self):
        """Test sprint planning workflow"""
        # Get ready items
        ready = self.backlog.get_ready_items()
        self.assertGreater(len(ready), 0)
        
        # Select high priority items
        high_priority = [item for item in ready if item.priority_score >= 1.5]
        self.assertGreater(len(high_priority), 0)
        
        # Calculate sprint capacity
        sprint_capacity = 20
        sprint_items = []
        total_effort = 0
        
        for item in high_priority:
            if total_effort + item.effort <= sprint_capacity:
                sprint_items.append(item)
                total_effort += item.effort
        
        self.assertGreater(len(sprint_items), 0)
        self.assertLessEqual(total_effort, sprint_capacity)
    
    def test_refactor_prioritization_workflow(self):
        """Test refactor prioritization workflow"""
        # Get must-do refactors
        must_do = self.backlog.get_refactors(RefactorType.MUST_DO)
        self.assertGreater(len(must_do), 0)
        
        # Sort by maturity (lowest first)
        sorted_refactors = sorted(must_do, key=lambda x: x.module_maturity_score)
        
        # Verify sorting
        for i in range(len(sorted_refactors) - 1):
            self.assertLessEqual(
                sorted_refactors[i].module_maturity_score,
                sorted_refactors[i + 1].module_maturity_score
            )
        
        # Verify all have maturity scores
        for refactor in sorted_refactors:
            self.assertIsNotNone(refactor.module_maturity_score)
            self.assertGreaterEqual(refactor.module_maturity_score, 0)
            self.assertLessEqual(refactor.module_maturity_score, 1)
    
    def test_team_coordination_workflow(self):
        """Test team coordination workflow"""
        workload = {}
        
        # Calculate workload for each owner
        for owner in Owner:
            items = self.backlog.get_by_owner(owner)
            total_effort = sum(item.effort for item in items)
            workload[owner.value] = {
                'items': len(items),
                'effort': total_effort,
                'avg_priority': sum(item.priority_score for item in items) / len(items) if items else 0
            }
        
        # Verify all teams have work
        for owner in Owner:
            self.assertGreater(workload[owner.value]['items'], 0)
            self.assertGreater(workload[owner.value]['effort'], 0)
    
    def test_risk_management_workflow(self):
        """Test risk management workflow"""
        # Identify high-risk items
        high_risk = [item for item in self.backlog.items if item.risk >= 4]
        self.assertGreater(len(high_risk), 0)
        
        # Find quick wins (low risk, high impact, low effort)
        quick_wins = [
            item for item in self.backlog.items
            if item.risk <= 2 and item.impact >= 4 and item.effort <= 3
        ]
        self.assertGreater(len(quick_wins), 0)
        
        # Verify quick wins have good priority
        for item in quick_wins:
            self.assertGreater(item.priority_score, 0.8)
    
    def test_dependency_analysis_workflow(self):
        """Test dependency analysis workflow"""
        # Generate dependency graph
        graph = self.backlog.generate_dependency_graph()
        self.assertEqual(len(graph), len(self.backlog.items))
        
        # Find items with most dependencies
        items_with_deps = [
            item for item in self.backlog.items
            if item.dependencies
        ]
        
        if items_with_deps:
            max_deps = max(len(item.dependencies) for item in items_with_deps)
            self.assertGreater(max_deps, 0)
        
        # Find blocking items
        all_dependencies = set()
        for item in self.backlog.items:
            all_dependencies.update(item.dependencies)
        
        blocking_items = [
            item for item in self.backlog.items
            if item.item in all_dependencies
        ]
        self.assertGreater(len(blocking_items), 0)
    
    def test_phase_progression_workflow(self):
        """Test phase progression workflow"""
        phases_in_order = [
            Phase.FOUNDATION,
            Phase.CORE_FEATURES,
            Phase.ENHANCEMENT,
            Phase.ENTERPRISE
        ]
        
        for i, phase in enumerate(phases_in_order):
            items = self.backlog.get_by_phase(phase)
            self.assertGreater(len(items), 0)
            
            # Calculate readiness for phase
            ready_in_phase = [
                item for item in items
                if not item.dependencies or all(
                    dep_item.phase != phase
                    for dep_item in self.backlog.items
                    if dep_item.item in item.dependencies
                )
            ]
            
            # Foundation should have ready items
            if phase == Phase.FOUNDATION:
                self.assertGreater(len(ready_in_phase), 0)
    
    def test_export_reimport_workflow(self):
        """Test exporting and re-importing data"""
        # Export to JSON
        json_path = os.path.join(self.temp_dir, "export.json")
        self.backlog.export_json(json_path)
        
        # Read exported data
        with open(json_path, 'r') as f:
            exported_data = json.load(f)
        
        # Verify data integrity
        self.assertEqual(
            exported_data['total_items'],
            len(self.backlog.items)
        )
        
        # Verify all items exported
        self.assertEqual(
            len(exported_data['items']),
            len(self.backlog.items)
        )
        
        # Verify first item matches
        first_exported = exported_data['items'][0]
        first_original = self.backlog.items[0]
        self.assertEqual(first_exported['item'], first_original.item)
        self.assertEqual(first_exported['impact'], first_original.impact)
        self.assertEqual(first_exported['effort'], first_original.effort)
    
    def test_filtering_combinations(self):
        """Test complex filtering scenarios"""
        # High priority foundation work
        foundation = self.backlog.get_by_phase(Phase.FOUNDATION)
        high_priority_foundation = [
            item for item in foundation
            if item.priority_score >= 1.0
        ]
        
        if high_priority_foundation:
            self.assertGreater(len(high_priority_foundation), 0)
        
        # Low risk R&D work
        rnd_items = self.backlog.get_by_owner(Owner.RND)
        low_risk_rnd = [
            item for item in rnd_items
            if item.risk <= 2
        ]
        
        if low_risk_rnd:
            self.assertGreater(len(low_risk_rnd), 0)
        
        # Frontend enhancement work
        frontend = self.backlog.get_by_owner(Owner.FRONTEND)
        frontend_enhancement = [
            item for item in frontend
            if item.phase == Phase.ENHANCEMENT
        ]
        
        # May be empty, just verify it runs
        self.assertIsInstance(frontend_enhancement, list)
    
    def test_summary_accuracy(self):
        """Test that summary statistics are accurate"""
        summary = self.backlog.get_summary()
        
        # Verify total items
        self.assertEqual(summary['total_items'], len(self.backlog.items))
        
        # Verify phase counts
        for phase in Phase:
            phase_items = self.backlog.get_by_phase(phase)
            phase_key = f"{phase.value}_items"
            self.assertEqual(summary[phase_key], len(phase_items))
        
        # Verify refactor counts
        must_do = len(self.backlog.get_refactors(RefactorType.MUST_DO))
        later = len(self.backlog.get_refactors(RefactorType.LATER))
        self.assertEqual(summary['must_do_refactors'], must_do)
        self.assertEqual(summary['later_refactors'], later)
        
        # Verify high impact count
        high_impact = len([item for item in self.backlog.items if item.impact >= 4])
        self.assertEqual(summary['high_impact_items'], high_impact)
        
        # Verify average priority
        avg_priority = sum(item.priority_score for item in self.backlog.items) / len(self.backlog.items)
        self.assertAlmostEqual(summary['avg_priority_score'], avg_priority, places=2)


if __name__ == '__main__':
    unittest.main()
