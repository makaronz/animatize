"""
Unit tests for Product Backlog Management System
"""

import unittest
import json
import os
import tempfile
from src.core.product_backlog import (
    ProductBacklog,
    BacklogItem,
    Owner,
    Phase,
    RefactorType
)


class TestBacklogItem(unittest.TestCase):
    """Test BacklogItem class"""
    
    def test_priority_calculation_basic(self):
        """Test basic priority score calculation"""
        item = BacklogItem(
            item="Test Item",
            impact=4,
            effort=2,
            risk=1,
            dependencies=[],
            owner=Owner.RND,
            test_hook="test_hook"
        )
        expected = (4 / 2) * (1 - 0.1)
        self.assertAlmostEqual(item.priority_score, expected, places=2)
    
    def test_priority_calculation_zero_effort(self):
        """Test priority calculation with zero effort"""
        item = BacklogItem(
            item="Test Item",
            impact=5,
            effort=0,
            risk=1,
            dependencies=[],
            owner=Owner.BACKEND,
            test_hook="test_hook"
        )
        self.assertEqual(item.priority_score, 50)
    
    def test_priority_calculation_high_risk(self):
        """Test priority calculation with high risk"""
        item = BacklogItem(
            item="Test Item",
            impact=5,
            effort=5,
            risk=5,
            dependencies=[],
            owner=Owner.FRONTEND,
            test_hook="test_hook"
        )
        expected = (5 / 5) * (1 - 0.5)
        self.assertAlmostEqual(item.priority_score, expected, places=2)
    
    def test_owner_string_conversion(self):
        """Test owner string to enum conversion"""
        item = BacklogItem(
            item="Test Item",
            impact=3,
            effort=3,
            risk=2,
            dependencies=[],
            owner="RND",
            test_hook="test_hook"
        )
        self.assertEqual(item.owner, Owner.RND)
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        item = BacklogItem(
            item="Test Item",
            impact=4,
            effort=2,
            risk=1,
            dependencies=["dep1"],
            owner=Owner.RND,
            test_hook="test_hook",
            phase=Phase.FOUNDATION,
            is_refactor=True,
            refactor_type=RefactorType.MUST_DO,
            module_maturity_score=0.5
        )
        data = item.to_dict()
        self.assertEqual(data['item'], "Test Item")
        self.assertEqual(data['owner'], "R&D")
        self.assertEqual(data['phase'], "foundation")
        self.assertEqual(data['refactor_type'], "must_do")
        self.assertTrue(data['is_refactor'])


class TestProductBacklog(unittest.TestCase):
    """Test ProductBacklog class"""
    
    def setUp(self):
        """Set up test backlog"""
        self.backlog = ProductBacklog()
    
    def test_backlog_generation(self):
        """Test that backlog generates minimum items"""
        self.assertGreaterEqual(len(self.backlog.items), 25)
    
    def test_backlog_sorted_by_priority(self):
        """Test that backlog is sorted by priority score"""
        for i in range(len(self.backlog.items) - 1):
            self.assertGreaterEqual(
                self.backlog.items[i].priority_score,
                self.backlog.items[i + 1].priority_score
            )
    
    def test_get_by_phase(self):
        """Test filtering by phase"""
        foundation_items = self.backlog.get_by_phase(Phase.FOUNDATION)
        self.assertTrue(all(item.phase == Phase.FOUNDATION for item in foundation_items))
        self.assertGreater(len(foundation_items), 0)
    
    def test_get_by_owner(self):
        """Test filtering by owner"""
        rnd_items = self.backlog.get_by_owner(Owner.RND)
        self.assertTrue(all(item.owner == Owner.RND for item in rnd_items))
        self.assertGreater(len(rnd_items), 0)
    
    def test_get_refactors(self):
        """Test getting refactor items"""
        refactors = self.backlog.get_refactors()
        self.assertTrue(all(item.is_refactor for item in refactors))
        self.assertGreater(len(refactors), 0)
    
    def test_get_refactors_must_do(self):
        """Test getting must-do refactors"""
        must_do = self.backlog.get_refactors(RefactorType.MUST_DO)
        self.assertTrue(all(
            item.is_refactor and item.refactor_type == RefactorType.MUST_DO
            for item in must_do
        ))
        self.assertGreater(len(must_do), 0)
    
    def test_get_refactors_later(self):
        """Test getting later refactors"""
        later = self.backlog.get_refactors(RefactorType.LATER)
        self.assertTrue(all(
            item.is_refactor and item.refactor_type == RefactorType.LATER
            for item in later
        ))
        self.assertGreater(len(later), 0)
    
    def test_get_high_priority(self):
        """Test getting high priority items"""
        high_priority = self.backlog.get_high_priority(threshold=1.0)
        self.assertTrue(all(item.priority_score >= 1.0 for item in high_priority))
        self.assertGreater(len(high_priority), 0)
    
    def test_get_by_risk(self):
        """Test filtering by risk level"""
        low_risk = self.backlog.get_by_risk(max_risk=2)
        self.assertTrue(all(item.risk <= 2 for item in low_risk))
        self.assertGreater(len(low_risk), 0)
    
    def test_get_summary(self):
        """Test summary generation"""
        summary = self.backlog.get_summary()
        self.assertIn('total_items', summary)
        self.assertIn('foundation_items', summary)
        self.assertIn('core_features_items', summary)
        self.assertIn('enhancement_items', summary)
        self.assertIn('enterprise_items', summary)
        self.assertIn('must_do_refactors', summary)
        self.assertIn('later_refactors', summary)
        self.assertEqual(summary['total_items'], len(self.backlog.items))
    
    def test_generate_dependency_graph(self):
        """Test dependency graph generation"""
        graph = self.backlog.generate_dependency_graph()
        self.assertIsInstance(graph, dict)
        self.assertEqual(len(graph), len(self.backlog.items))
    
    def test_get_ready_items(self):
        """Test getting ready items"""
        ready = self.backlog.get_ready_items()
        self.assertGreater(len(ready), 0)
        for item in ready:
            if item.dependencies:
                self.fail(f"Item {item.item} has dependencies but was marked as ready")
    
    def test_export_json(self):
        """Test JSON export"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            self.backlog.export_json(temp_path)
            self.assertTrue(os.path.exists(temp_path))
            
            with open(temp_path, 'r') as f:
                data = json.load(f)
            
            self.assertIn('total_items', data)
            self.assertIn('summary', data)
            self.assertIn('items', data)
            self.assertEqual(data['total_items'], len(self.backlog.items))
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_markdown(self):
        """Test Markdown export"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_path = f.name
        
        try:
            self.backlog.export_markdown(temp_path)
            self.assertTrue(os.path.exists(temp_path))
            
            with open(temp_path, 'r') as f:
                content = f.read()
            
            self.assertIn('# Product Backlog', content)
            self.assertIn('## Summary', content)
            self.assertIn('Foundation', content)
            self.assertIn('Core Features', content)
            self.assertIn('Enhancement', content)
            self.assertIn('Enterprise', content)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_all_phases_present(self):
        """Test that all phases are represented"""
        for phase in Phase:
            phase_items = self.backlog.get_by_phase(phase)
            self.assertGreater(
                len(phase_items), 0,
                f"Phase {phase.value} has no items"
            )
    
    def test_all_owners_present(self):
        """Test that all owners are represented"""
        for owner in Owner:
            owner_items = self.backlog.get_by_owner(owner)
            self.assertGreater(
                len(owner_items), 0,
                f"Owner {owner.value} has no items"
            )
    
    def test_refactor_maturity_scores(self):
        """Test that refactors have maturity scores"""
        refactors = self.backlog.get_refactors()
        for refactor in refactors:
            self.assertIsNotNone(
                refactor.module_maturity_score,
                f"Refactor {refactor.item} missing maturity score"
            )
            self.assertGreaterEqual(refactor.module_maturity_score, 0.0)
            self.assertLessEqual(refactor.module_maturity_score, 1.0)
    
    def test_impact_effort_risk_ranges(self):
        """Test that impact, effort, and risk are in valid ranges"""
        for item in self.backlog.items:
            self.assertGreaterEqual(item.impact, 1)
            self.assertLessEqual(item.impact, 5)
            self.assertGreaterEqual(item.effort, 1)
            self.assertLessEqual(item.effort, 5)
            self.assertGreaterEqual(item.risk, 1)
            self.assertLessEqual(item.risk, 5)
    
    def test_all_items_have_test_hooks(self):
        """Test that all items have test hooks"""
        for item in self.backlog.items:
            self.assertIsNotNone(item.test_hook)
            self.assertTrue(len(item.test_hook) > 0)
            self.assertTrue(item.test_hook.startswith("test_"))


if __name__ == '__main__':
    unittest.main()
