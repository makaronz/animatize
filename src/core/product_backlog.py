"""
Product Backlog Management System

Generates, prioritizes, and manages comprehensive product backlog items
with impact/effort analysis, risk assessment, and phase grouping.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json


class Owner(Enum):
    RND = "R&D"
    BACKEND = "BE"
    FRONTEND = "FE"
    DESIGN = "Design"


class Phase(Enum):
    FOUNDATION = "foundation"
    CORE_FEATURES = "core_features"
    ENHANCEMENT = "enhancement"
    ENTERPRISE = "enterprise"


class RefactorType(Enum):
    MUST_DO = "must_do"
    LATER = "later"


@dataclass
class BacklogItem:
    item: str
    impact: int  # 1-5 scale
    effort: int  # 1-5 scale
    risk: int  # 1-5 scale
    dependencies: List[str]
    owner: Owner
    test_hook: str
    phase: Optional[Phase] = None
    priority_score: float = 0.0
    is_refactor: bool = False
    refactor_type: Optional[RefactorType] = None
    module_maturity_score: Optional[float] = None
    
    def __post_init__(self):
        if isinstance(self.owner, str):
            self.owner = Owner[self.owner.upper().replace("&", "")]
        if isinstance(self.phase, str):
            self.phase = Phase(self.phase)
        if isinstance(self.refactor_type, str):
            self.refactor_type = RefactorType(self.refactor_type)
        self.calculate_priority()
    
    def calculate_priority(self):
        """Calculate priority score based on impact/effort ratio with risk adjustment"""
        if self.effort == 0:
            self.priority_score = self.impact * 10
        else:
            base_score = self.impact / self.effort
            risk_adjustment = 1 - (self.risk * 0.1)
            self.priority_score = base_score * risk_adjustment
    
    def to_dict(self) -> Dict:
        """Convert backlog item to dictionary"""
        data = asdict(self)
        data['owner'] = self.owner.value
        if self.phase:
            data['phase'] = self.phase.value
        if self.refactor_type:
            data['refactor_type'] = self.refactor_type.value
        return data


class ProductBacklog:
    """Manages product backlog with comprehensive prioritization and grouping"""
    
    def __init__(self):
        self.items: List[BacklogItem] = []
        self._generate_comprehensive_backlog()
    
    def _generate_comprehensive_backlog(self):
        """Generate 25+ comprehensive backlog items"""
        
        # Foundation Phase Items
        foundation_items = [
            BacklogItem(
                item="Core Video Generation Pipeline Architecture",
                impact=5,
                effort=5,
                risk=4,
                dependencies=[],
                owner=Owner.RND,
                test_hook="test_video_pipeline_integration",
                phase=Phase.FOUNDATION
            ),
            BacklogItem(
                item="Refactor: Modularize Video Model Abstraction Layer",
                impact=4,
                effort=3,
                risk=2,
                dependencies=["Core Video Generation Pipeline Architecture"],
                owner=Owner.BACKEND,
                test_hook="test_model_abstraction_isolation",
                phase=Phase.FOUNDATION,
                is_refactor=True,
                refactor_type=RefactorType.MUST_DO,
                module_maturity_score=0.45
            ),
            BacklogItem(
                item="Database Schema Design for Video Projects",
                impact=5,
                effort=4,
                risk=3,
                dependencies=[],
                owner=Owner.BACKEND,
                test_hook="test_database_schema_validation",
                phase=Phase.FOUNDATION
            ),
            BacklogItem(
                item="Authentication and Authorization System",
                impact=5,
                effort=4,
                risk=4,
                dependencies=["Database Schema Design for Video Projects"],
                owner=Owner.BACKEND,
                test_hook="test_auth_security_compliance",
                phase=Phase.FOUNDATION
            ),
            BacklogItem(
                item="RESTful API Foundation with OpenAPI Spec",
                impact=5,
                effort=3,
                risk=2,
                dependencies=["Database Schema Design for Video Projects"],
                owner=Owner.BACKEND,
                test_hook="test_api_contract_validation",
                phase=Phase.FOUNDATION
            ),
            BacklogItem(
                item="Refactor: Decouple Prompt Expansion Logic from Core Engine",
                impact=4,
                effort=2,
                risk=1,
                dependencies=["Core Video Generation Pipeline Architecture"],
                owner=Owner.RND,
                test_hook="test_prompt_expander_modularity",
                phase=Phase.FOUNDATION,
                is_refactor=True,
                refactor_type=RefactorType.MUST_DO,
                module_maturity_score=0.52
            ),
        ]
        
        # Core Features Phase Items
        core_features_items = [
            BacklogItem(
                item="Director UX Interface Implementation",
                impact=5,
                effort=5,
                risk=3,
                dependencies=["RESTful API Foundation with OpenAPI Spec"],
                owner=Owner.FRONTEND,
                test_hook="test_director_ux_workflows",
                phase=Phase.CORE_FEATURES
            ),
            BacklogItem(
                item="Scene Analyzer with AI Detection",
                impact=5,
                effort=4,
                risk=3,
                dependencies=["Core Video Generation Pipeline Architecture"],
                owner=Owner.RND,
                test_hook="test_scene_analyzer_accuracy",
                phase=Phase.CORE_FEATURES
            ),
            BacklogItem(
                item="Movement Prediction Engine",
                impact=5,
                effort=5,
                risk=4,
                dependencies=["Scene Analyzer with AI Detection"],
                owner=Owner.RND,
                test_hook="test_movement_prediction_precision",
                phase=Phase.CORE_FEATURES
            ),
            BacklogItem(
                item="Consistency Engine for Frame Coherence",
                impact=5,
                effort=5,
                risk=5,
                dependencies=["Movement Prediction Engine", "Scene Analyzer with AI Detection"],
                owner=Owner.RND,
                test_hook="test_consistency_engine_validation",
                phase=Phase.CORE_FEATURES
            ),
            BacklogItem(
                item="Film Grammar Rule System",
                impact=4,
                effort=4,
                risk=3,
                dependencies=["Director UX Interface Implementation"],
                owner=Owner.RND,
                test_hook="test_film_grammar_rules_application",
                phase=Phase.CORE_FEATURES
            ),
            BacklogItem(
                item="Multi-Model Video Generation Support",
                impact=5,
                effort=4,
                risk=3,
                dependencies=["Core Video Generation Pipeline Architecture"],
                owner=Owner.BACKEND,
                test_hook="test_multi_model_generation",
                phase=Phase.CORE_FEATURES
            ),
            BacklogItem(
                item="Real-time Video Preview System",
                impact=4,
                effort=5,
                risk=4,
                dependencies=["Director UX Interface Implementation"],
                owner=Owner.FRONTEND,
                test_hook="test_realtime_preview_performance",
                phase=Phase.CORE_FEATURES
            ),
            BacklogItem(
                item="Refactor: Extract Image Generator into Standalone Service",
                impact=3,
                effort=3,
                risk=2,
                dependencies=["Core Video Generation Pipeline Architecture"],
                owner=Owner.BACKEND,
                test_hook="test_image_generator_service_isolation",
                phase=Phase.CORE_FEATURES,
                is_refactor=True,
                refactor_type=RefactorType.MUST_DO,
                module_maturity_score=0.48
            ),
        ]
        
        # Enhancement Phase Items
        enhancement_items = [
            BacklogItem(
                item="Advanced Quality Assurance Metrics",
                impact=4,
                effort=3,
                risk=2,
                dependencies=["Consistency Engine for Frame Coherence"],
                owner=Owner.RND,
                test_hook="test_qa_metrics_accuracy",
                phase=Phase.ENHANCEMENT
            ),
            BacklogItem(
                item="Evaluation Harness for Model Performance",
                impact=4,
                effort=4,
                risk=3,
                dependencies=["Multi-Model Video Generation Support"],
                owner=Owner.RND,
                test_hook="test_evaluation_harness_reliability",
                phase=Phase.ENHANCEMENT
            ),
            BacklogItem(
                item="Video Prompt Catalog with Template Library",
                impact=4,
                effort=3,
                risk=2,
                dependencies=["Film Grammar Rule System"],
                owner=Owner.DESIGN,
                test_hook="test_prompt_catalog_coverage",
                phase=Phase.ENHANCEMENT
            ),
            BacklogItem(
                item="Batch Video Generation Processing",
                impact=4,
                effort=3,
                risk=2,
                dependencies=["Multi-Model Video Generation Support"],
                owner=Owner.BACKEND,
                test_hook="test_batch_processing_throughput",
                phase=Phase.ENHANCEMENT
            ),
            BacklogItem(
                item="Adaptive Motion Detection Algorithms",
                impact=4,
                effort=4,
                risk=3,
                dependencies=["Movement Prediction Engine"],
                owner=Owner.RND,
                test_hook="test_motion_detection_adaptability",
                phase=Phase.ENHANCEMENT
            ),
            BacklogItem(
                item="User Feedback Collection and Analysis System",
                impact=3,
                effort=2,
                risk=1,
                dependencies=["Director UX Interface Implementation"],
                owner=Owner.FRONTEND,
                test_hook="test_feedback_collection_pipeline",
                phase=Phase.ENHANCEMENT
            ),
            BacklogItem(
                item="Asset Library Management System",
                impact=4,
                effort=4,
                risk=2,
                dependencies=["Database Schema Design for Video Projects"],
                owner=Owner.BACKEND,
                test_hook="test_asset_library_crud_operations",
                phase=Phase.ENHANCEMENT
            ),
            BacklogItem(
                item="Refactor: Optimize Analyzer Pipeline for Performance",
                impact=3,
                effort=2,
                risk=1,
                dependencies=["Scene Analyzer with AI Detection"],
                owner=Owner.RND,
                test_hook="test_analyzer_performance_benchmarks",
                phase=Phase.ENHANCEMENT,
                is_refactor=True,
                refactor_type=RefactorType.LATER,
                module_maturity_score=0.68
            ),
            BacklogItem(
                item="Export Formats and Codec Support",
                impact=3,
                effort=3,
                risk=2,
                dependencies=["Core Video Generation Pipeline Architecture"],
                owner=Owner.BACKEND,
                test_hook="test_export_format_compatibility",
                phase=Phase.ENHANCEMENT
            ),
        ]
        
        # Enterprise Phase Items
        enterprise_items = [
            BacklogItem(
                item="Multi-Tenant Architecture Support",
                impact=5,
                effort=5,
                risk=4,
                dependencies=["Authentication and Authorization System", "Database Schema Design for Video Projects"],
                owner=Owner.BACKEND,
                test_hook="test_multi_tenant_isolation",
                phase=Phase.ENTERPRISE
            ),
            BacklogItem(
                item="Advanced Analytics Dashboard",
                impact=4,
                effort=4,
                risk=2,
                dependencies=["Evaluation Harness for Model Performance"],
                owner=Owner.FRONTEND,
                test_hook="test_analytics_dashboard_accuracy",
                phase=Phase.ENTERPRISE
            ),
            BacklogItem(
                item="Collaboration and Team Workspace Features",
                impact=4,
                effort=5,
                risk=3,
                dependencies=["Multi-Tenant Architecture Support"],
                owner=Owner.FRONTEND,
                test_hook="test_collaboration_features_sync",
                phase=Phase.ENTERPRISE
            ),
            BacklogItem(
                item="API Rate Limiting and Quota Management",
                impact=4,
                effort=3,
                risk=2,
                dependencies=["RESTful API Foundation with OpenAPI Spec"],
                owner=Owner.BACKEND,
                test_hook="test_rate_limiting_enforcement",
                phase=Phase.ENTERPRISE
            ),
            BacklogItem(
                item="Webhook System for External Integrations",
                impact=3,
                effort=3,
                risk=2,
                dependencies=["RESTful API Foundation with OpenAPI Spec"],
                owner=Owner.BACKEND,
                test_hook="test_webhook_delivery_reliability",
                phase=Phase.ENTERPRISE
            ),
            BacklogItem(
                item="Enterprise SSO Integration (SAML, OAuth)",
                impact=4,
                effort=4,
                risk=3,
                dependencies=["Authentication and Authorization System"],
                owner=Owner.BACKEND,
                test_hook="test_sso_integration_protocols",
                phase=Phase.ENTERPRISE
            ),
            BacklogItem(
                item="Audit Logging and Compliance Reporting",
                impact=4,
                effort=3,
                risk=2,
                dependencies=["Multi-Tenant Architecture Support"],
                owner=Owner.BACKEND,
                test_hook="test_audit_log_completeness",
                phase=Phase.ENTERPRISE
            ),
            BacklogItem(
                item="Custom Model Training Pipeline for Enterprise",
                impact=5,
                effort=5,
                risk=5,
                dependencies=["Multi-Model Video Generation Support"],
                owner=Owner.RND,
                test_hook="test_custom_model_training_pipeline",
                phase=Phase.ENTERPRISE
            ),
            BacklogItem(
                item="Refactor: Migrate to Microservices Architecture",
                impact=4,
                effort=5,
                risk=5,
                dependencies=["Multi-Tenant Architecture Support"],
                owner=Owner.BACKEND,
                test_hook="test_microservices_communication",
                phase=Phase.ENTERPRISE,
                is_refactor=True,
                refactor_type=RefactorType.LATER,
                module_maturity_score=0.72
            ),
        ]
        
        # Combine all items
        self.items.extend(foundation_items)
        self.items.extend(core_features_items)
        self.items.extend(enhancement_items)
        self.items.extend(enterprise_items)
        
        # Sort by priority score
        self.items.sort(key=lambda x: x.priority_score, reverse=True)
    
    def get_by_phase(self, phase: Phase) -> List[BacklogItem]:
        """Get all items for a specific phase"""
        return [item for item in self.items if item.phase == phase]
    
    def get_by_owner(self, owner: Owner) -> List[BacklogItem]:
        """Get all items for a specific owner"""
        return [item for item in self.items if item.owner == owner]
    
    def get_refactors(self, refactor_type: Optional[RefactorType] = None) -> List[BacklogItem]:
        """Get all refactor items, optionally filtered by type"""
        refactors = [item for item in self.items if item.is_refactor]
        if refactor_type:
            refactors = [item for item in refactors if item.refactor_type == refactor_type]
        return refactors
    
    def get_high_priority(self, threshold: float = 1.0) -> List[BacklogItem]:
        """Get high priority items above threshold"""
        return [item for item in self.items if item.priority_score >= threshold]
    
    def get_by_risk(self, max_risk: int) -> List[BacklogItem]:
        """Get items with risk level at or below max_risk"""
        return [item for item in self.items if item.risk <= max_risk]
    
    def export_json(self, filepath: str):
        """Export backlog to JSON file"""
        data = {
            "total_items": len(self.items),
            "summary": self.get_summary(),
            "items": [item.to_dict() for item in self.items]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def export_markdown(self, filepath: str):
        """Export backlog to markdown format"""
        with open(filepath, 'w') as f:
            f.write("# Product Backlog\n\n")
            f.write(f"**Total Items:** {len(self.items)}\n\n")
            
            summary = self.get_summary()
            f.write("## Summary\n\n")
            for key, value in summary.items():
                f.write(f"- **{key}:** {value}\n")
            f.write("\n")
            
            # Group by phase
            for phase in Phase:
                phase_items = self.get_by_phase(phase)
                if phase_items:
                    f.write(f"## {phase.value.replace('_', ' ').title()}\n\n")
                    for item in phase_items:
                        f.write(f"### {item.item}\n\n")
                        f.write(f"- **Priority Score:** {item.priority_score:.2f}\n")
                        f.write(f"- **Impact:** {item.impact}/5\n")
                        f.write(f"- **Effort:** {item.effort}/5\n")
                        f.write(f"- **Risk:** {item.risk}/5\n")
                        f.write(f"- **Owner:** {item.owner.value}\n")
                        f.write(f"- **Test Hook:** `{item.test_hook}`\n")
                        if item.dependencies:
                            f.write(f"- **Dependencies:** {', '.join(item.dependencies)}\n")
                        if item.is_refactor:
                            f.write(f"- **Refactor Type:** {item.refactor_type.value}\n")
                            f.write(f"- **Module Maturity Score:** {item.module_maturity_score}\n")
                        f.write("\n")
    
    def get_summary(self) -> Dict:
        """Generate summary statistics"""
        return {
            "total_items": len(self.items),
            "foundation_items": len(self.get_by_phase(Phase.FOUNDATION)),
            "core_features_items": len(self.get_by_phase(Phase.CORE_FEATURES)),
            "enhancement_items": len(self.get_by_phase(Phase.ENHANCEMENT)),
            "enterprise_items": len(self.get_by_phase(Phase.ENTERPRISE)),
            "must_do_refactors": len([r for r in self.get_refactors() if r.refactor_type == RefactorType.MUST_DO]),
            "later_refactors": len([r for r in self.get_refactors() if r.refactor_type == RefactorType.LATER]),
            "high_impact_items": len([item for item in self.items if item.impact >= 4]),
            "high_risk_items": len([item for item in self.items if item.risk >= 4]),
            "avg_priority_score": sum(item.priority_score for item in self.items) / len(self.items),
        }
    
    def generate_dependency_graph(self) -> Dict[str, List[str]]:
        """Generate dependency graph for visualization"""
        graph = {}
        for item in self.items:
            graph[item.item] = item.dependencies
        return graph
    
    def get_ready_items(self) -> List[BacklogItem]:
        """Get items with all dependencies completed (no dependencies)"""
        completed = set()
        ready = []
        
        for item in self.items:
            if not item.dependencies:
                ready.append(item)
            elif all(dep in completed for dep in item.dependencies):
                ready.append(item)
        
        return ready


def main():
    """Generate and export comprehensive product backlog"""
    backlog = ProductBacklog()
    
    print(f"Generated {len(backlog.items)} backlog items\n")
    
    summary = backlog.get_summary()
    print("=== Backlog Summary ===")
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    print("\n=== Top 10 Priority Items ===")
    for i, item in enumerate(backlog.items[:10], 1):
        print(f"{i}. [{item.priority_score:.2f}] {item.item} ({item.owner.value})")
    
    print("\n=== Must-Do Refactors ===")
    must_do_refactors = backlog.get_refactors(RefactorType.MUST_DO)
    for item in must_do_refactors:
        print(f"- {item.item} (Maturity: {item.module_maturity_score})")
    
    # Export to files
    backlog.export_json("data/product_backlog.json")
    backlog.export_markdown("docs/PRODUCT_BACKLOG.md")
    
    print("\n✓ Exported to data/product_backlog.json")
    print("✓ Exported to docs/PRODUCT_BACKLOG.md")


if __name__ == "__main__":
    main()
