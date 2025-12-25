/**
 * Product Backlog Management System (TypeScript)
 * 
 * Generates, prioritizes, and manages comprehensive product backlog items
 * with impact/effort analysis, risk assessment, and phase grouping.
 */

export enum Owner {
  RND = "R&D",
  BACKEND = "BE",
  FRONTEND = "FE",
  DESIGN = "Design"
}

export enum Phase {
  FOUNDATION = "foundation",
  CORE_FEATURES = "core_features",
  ENHANCEMENT = "enhancement",
  ENTERPRISE = "enterprise"
}

export enum RefactorType {
  MUST_DO = "must_do",
  LATER = "later"
}

export interface BacklogItem {
  item: string;
  impact: number; // 1-5 scale
  effort: number; // 1-5 scale
  risk: number; // 1-5 scale
  dependencies: string[];
  owner: Owner;
  testHook: string;
  phase?: Phase;
  priorityScore?: number;
  isRefactor?: boolean;
  refactorType?: RefactorType;
  moduleMaturityScore?: number;
}

export class BacklogItemModel implements BacklogItem {
  item: string;
  impact: number;
  effort: number;
  risk: number;
  dependencies: string[];
  owner: Owner;
  testHook: string;
  phase?: Phase;
  priorityScore: number;
  isRefactor: boolean;
  refactorType?: RefactorType;
  moduleMaturityScore?: number;

  constructor(data: BacklogItem) {
    this.item = data.item;
    this.impact = data.impact;
    this.effort = data.effort;
    this.risk = data.risk;
    this.dependencies = data.dependencies;
    this.owner = data.owner;
    this.testHook = data.testHook;
    this.phase = data.phase;
    this.isRefactor = data.isRefactor || false;
    this.refactorType = data.refactorType;
    this.moduleMaturityScore = data.moduleMaturityScore;
    this.priorityScore = this.calculatePriority();
  }

  calculatePriority(): number {
    if (this.effort === 0) {
      return this.impact * 10;
    }
    const baseScore = this.impact / this.effort;
    const riskAdjustment = 1 - (this.risk * 0.1);
    return baseScore * riskAdjustment;
  }

  toJSON(): Record<string, any> {
    return {
      item: this.item,
      impact: this.impact,
      effort: this.effort,
      risk: this.risk,
      dependencies: this.dependencies,
      owner: this.owner,
      testHook: this.testHook,
      phase: this.phase,
      priorityScore: this.priorityScore,
      isRefactor: this.isRefactor,
      refactorType: this.refactorType,
      moduleMaturityScore: this.moduleMaturityScore
    };
  }
}

export interface BacklogSummary {
  totalItems: number;
  foundationItems: number;
  coreFeaturesItems: number;
  enhancementItems: number;
  enterpriseItems: number;
  mustDoRefactors: number;
  laterRefactors: number;
  highImpactItems: number;
  highRiskItems: number;
  avgPriorityScore: number;
}

export class ProductBacklog {
  private items: BacklogItemModel[] = [];

  constructor() {
    this.generateComprehensiveBacklog();
  }

  private generateComprehensiveBacklog(): void {
    const foundationItems: BacklogItem[] = [
      {
        item: "Core Video Generation Pipeline Architecture",
        impact: 5,
        effort: 5,
        risk: 4,
        dependencies: [],
        owner: Owner.RND,
        testHook: "test_video_pipeline_integration",
        phase: Phase.FOUNDATION
      },
      {
        item: "Refactor: Modularize Video Model Abstraction Layer",
        impact: 4,
        effort: 3,
        risk: 2,
        dependencies: ["Core Video Generation Pipeline Architecture"],
        owner: Owner.BACKEND,
        testHook: "test_model_abstraction_isolation",
        phase: Phase.FOUNDATION,
        isRefactor: true,
        refactorType: RefactorType.MUST_DO,
        moduleMaturityScore: 0.45
      },
      {
        item: "Database Schema Design for Video Projects",
        impact: 5,
        effort: 4,
        risk: 3,
        dependencies: [],
        owner: Owner.BACKEND,
        testHook: "test_database_schema_validation",
        phase: Phase.FOUNDATION
      },
      {
        item: "Authentication and Authorization System",
        impact: 5,
        effort: 4,
        risk: 4,
        dependencies: ["Database Schema Design for Video Projects"],
        owner: Owner.BACKEND,
        testHook: "test_auth_security_compliance",
        phase: Phase.FOUNDATION
      },
      {
        item: "RESTful API Foundation with OpenAPI Spec",
        impact: 5,
        effort: 3,
        risk: 2,
        dependencies: ["Database Schema Design for Video Projects"],
        owner: Owner.BACKEND,
        testHook: "test_api_contract_validation",
        phase: Phase.FOUNDATION
      },
      {
        item: "Refactor: Decouple Prompt Expansion Logic from Core Engine",
        impact: 4,
        effort: 2,
        risk: 1,
        dependencies: ["Core Video Generation Pipeline Architecture"],
        owner: Owner.RND,
        testHook: "test_prompt_expander_modularity",
        phase: Phase.FOUNDATION,
        isRefactor: true,
        refactorType: RefactorType.MUST_DO,
        moduleMaturityScore: 0.52
      }
    ];

    const coreFeaturesItems: BacklogItem[] = [
      {
        item: "Director UX Interface Implementation",
        impact: 5,
        effort: 5,
        risk: 3,
        dependencies: ["RESTful API Foundation with OpenAPI Spec"],
        owner: Owner.FRONTEND,
        testHook: "test_director_ux_workflows",
        phase: Phase.CORE_FEATURES
      },
      {
        item: "Scene Analyzer with AI Detection",
        impact: 5,
        effort: 4,
        risk: 3,
        dependencies: ["Core Video Generation Pipeline Architecture"],
        owner: Owner.RND,
        testHook: "test_scene_analyzer_accuracy",
        phase: Phase.CORE_FEATURES
      },
      {
        item: "Movement Prediction Engine",
        impact: 5,
        effort: 5,
        risk: 4,
        dependencies: ["Scene Analyzer with AI Detection"],
        owner: Owner.RND,
        testHook: "test_movement_prediction_precision",
        phase: Phase.CORE_FEATURES
      },
      {
        item: "Consistency Engine for Frame Coherence",
        impact: 5,
        effort: 5,
        risk: 5,
        dependencies: ["Movement Prediction Engine", "Scene Analyzer with AI Detection"],
        owner: Owner.RND,
        testHook: "test_consistency_engine_validation",
        phase: Phase.CORE_FEATURES
      },
      {
        item: "Film Grammar Rule System",
        impact: 4,
        effort: 4,
        risk: 3,
        dependencies: ["Director UX Interface Implementation"],
        owner: Owner.RND,
        testHook: "test_film_grammar_rules_application",
        phase: Phase.CORE_FEATURES
      },
      {
        item: "Multi-Model Video Generation Support",
        impact: 5,
        effort: 4,
        risk: 3,
        dependencies: ["Core Video Generation Pipeline Architecture"],
        owner: Owner.BACKEND,
        testHook: "test_multi_model_generation",
        phase: Phase.CORE_FEATURES
      },
      {
        item: "Real-time Video Preview System",
        impact: 4,
        effort: 5,
        risk: 4,
        dependencies: ["Director UX Interface Implementation"],
        owner: Owner.FRONTEND,
        testHook: "test_realtime_preview_performance",
        phase: Phase.CORE_FEATURES
      },
      {
        item: "Refactor: Extract Image Generator into Standalone Service",
        impact: 3,
        effort: 3,
        risk: 2,
        dependencies: ["Core Video Generation Pipeline Architecture"],
        owner: Owner.BACKEND,
        testHook: "test_image_generator_service_isolation",
        phase: Phase.CORE_FEATURES,
        isRefactor: true,
        refactorType: RefactorType.MUST_DO,
        moduleMaturityScore: 0.48
      }
    ];

    const enhancementItems: BacklogItem[] = [
      {
        item: "Advanced Quality Assurance Metrics",
        impact: 4,
        effort: 3,
        risk: 2,
        dependencies: ["Consistency Engine for Frame Coherence"],
        owner: Owner.RND,
        testHook: "test_qa_metrics_accuracy",
        phase: Phase.ENHANCEMENT
      },
      {
        item: "Evaluation Harness for Model Performance",
        impact: 4,
        effort: 4,
        risk: 3,
        dependencies: ["Multi-Model Video Generation Support"],
        owner: Owner.RND,
        testHook: "test_evaluation_harness_reliability",
        phase: Phase.ENHANCEMENT
      },
      {
        item: "Video Prompt Catalog with Template Library",
        impact: 4,
        effort: 3,
        risk: 2,
        dependencies: ["Film Grammar Rule System"],
        owner: Owner.DESIGN,
        testHook: "test_prompt_catalog_coverage",
        phase: Phase.ENHANCEMENT
      },
      {
        item: "Batch Video Generation Processing",
        impact: 4,
        effort: 3,
        risk: 2,
        dependencies: ["Multi-Model Video Generation Support"],
        owner: Owner.BACKEND,
        testHook: "test_batch_processing_throughput",
        phase: Phase.ENHANCEMENT
      },
      {
        item: "Adaptive Motion Detection Algorithms",
        impact: 4,
        effort: 4,
        risk: 3,
        dependencies: ["Movement Prediction Engine"],
        owner: Owner.RND,
        testHook: "test_motion_detection_adaptability",
        phase: Phase.ENHANCEMENT
      },
      {
        item: "User Feedback Collection and Analysis System",
        impact: 3,
        effort: 2,
        risk: 1,
        dependencies: ["Director UX Interface Implementation"],
        owner: Owner.FRONTEND,
        testHook: "test_feedback_collection_pipeline",
        phase: Phase.ENHANCEMENT
      },
      {
        item: "Asset Library Management System",
        impact: 4,
        effort: 4,
        risk: 2,
        dependencies: ["Database Schema Design for Video Projects"],
        owner: Owner.BACKEND,
        testHook: "test_asset_library_crud_operations",
        phase: Phase.ENHANCEMENT
      },
      {
        item: "Refactor: Optimize Analyzer Pipeline for Performance",
        impact: 3,
        effort: 2,
        risk: 1,
        dependencies: ["Scene Analyzer with AI Detection"],
        owner: Owner.RND,
        testHook: "test_analyzer_performance_benchmarks",
        phase: Phase.ENHANCEMENT,
        isRefactor: true,
        refactorType: RefactorType.LATER,
        moduleMaturityScore: 0.68
      },
      {
        item: "Export Formats and Codec Support",
        impact: 3,
        effort: 3,
        risk: 2,
        dependencies: ["Core Video Generation Pipeline Architecture"],
        owner: Owner.BACKEND,
        testHook: "test_export_format_compatibility",
        phase: Phase.ENHANCEMENT
      }
    ];

    const enterpriseItems: BacklogItem[] = [
      {
        item: "Multi-Tenant Architecture Support",
        impact: 5,
        effort: 5,
        risk: 4,
        dependencies: ["Authentication and Authorization System", "Database Schema Design for Video Projects"],
        owner: Owner.BACKEND,
        testHook: "test_multi_tenant_isolation",
        phase: Phase.ENTERPRISE
      },
      {
        item: "Advanced Analytics Dashboard",
        impact: 4,
        effort: 4,
        risk: 2,
        dependencies: ["Evaluation Harness for Model Performance"],
        owner: Owner.FRONTEND,
        testHook: "test_analytics_dashboard_accuracy",
        phase: Phase.ENTERPRISE
      },
      {
        item: "Collaboration and Team Workspace Features",
        impact: 4,
        effort: 5,
        risk: 3,
        dependencies: ["Multi-Tenant Architecture Support"],
        owner: Owner.FRONTEND,
        testHook: "test_collaboration_features_sync",
        phase: Phase.ENTERPRISE
      },
      {
        item: "API Rate Limiting and Quota Management",
        impact: 4,
        effort: 3,
        risk: 2,
        dependencies: ["RESTful API Foundation with OpenAPI Spec"],
        owner: Owner.BACKEND,
        testHook: "test_rate_limiting_enforcement",
        phase: Phase.ENTERPRISE
      },
      {
        item: "Webhook System for External Integrations",
        impact: 3,
        effort: 3,
        risk: 2,
        dependencies: ["RESTful API Foundation with OpenAPI Spec"],
        owner: Owner.BACKEND,
        testHook: "test_webhook_delivery_reliability",
        phase: Phase.ENTERPRISE
      },
      {
        item: "Enterprise SSO Integration (SAML, OAuth)",
        impact: 4,
        effort: 4,
        risk: 3,
        dependencies: ["Authentication and Authorization System"],
        owner: Owner.BACKEND,
        testHook: "test_sso_integration_protocols",
        phase: Phase.ENTERPRISE
      },
      {
        item: "Audit Logging and Compliance Reporting",
        impact: 4,
        effort: 3,
        risk: 2,
        dependencies: ["Multi-Tenant Architecture Support"],
        owner: Owner.BACKEND,
        testHook: "test_audit_log_completeness",
        phase: Phase.ENTERPRISE
      },
      {
        item: "Custom Model Training Pipeline for Enterprise",
        impact: 5,
        effort: 5,
        risk: 5,
        dependencies: ["Multi-Model Video Generation Support"],
        owner: Owner.RND,
        testHook: "test_custom_model_training_pipeline",
        phase: Phase.ENTERPRISE
      },
      {
        item: "Refactor: Migrate to Microservices Architecture",
        impact: 4,
        effort: 5,
        risk: 5,
        dependencies: ["Multi-Tenant Architecture Support"],
        owner: Owner.BACKEND,
        testHook: "test_microservices_communication",
        phase: Phase.ENTERPRISE,
        isRefactor: true,
        refactorType: RefactorType.LATER,
        moduleMaturityScore: 0.72
      }
    ];

    const allItems = [
      ...foundationItems,
      ...coreFeaturesItems,
      ...enhancementItems,
      ...enterpriseItems
    ];

    this.items = allItems.map(item => new BacklogItemModel(item));
    this.items.sort((a, b) => b.priorityScore - a.priorityScore);
  }

  getByPhase(phase: Phase): BacklogItemModel[] {
    return this.items.filter(item => item.phase === phase);
  }

  getByOwner(owner: Owner): BacklogItemModel[] {
    return this.items.filter(item => item.owner === owner);
  }

  getRefactors(refactorType?: RefactorType): BacklogItemModel[] {
    let refactors = this.items.filter(item => item.isRefactor);
    if (refactorType) {
      refactors = refactors.filter(item => item.refactorType === refactorType);
    }
    return refactors;
  }

  getHighPriority(threshold: number = 1.0): BacklogItemModel[] {
    return this.items.filter(item => item.priorityScore >= threshold);
  }

  getByRisk(maxRisk: number): BacklogItemModel[] {
    return this.items.filter(item => item.risk <= maxRisk);
  }

  getSummary(): BacklogSummary {
    const mustDoRefactors = this.getRefactors(RefactorType.MUST_DO).length;
    const laterRefactors = this.getRefactors(RefactorType.LATER).length;
    const highImpactItems = this.items.filter(item => item.impact >= 4).length;
    const highRiskItems = this.items.filter(item => item.risk >= 4).length;
    const avgPriorityScore = this.items.reduce((sum, item) => sum + item.priorityScore, 0) / this.items.length;

    return {
      totalItems: this.items.length,
      foundationItems: this.getByPhase(Phase.FOUNDATION).length,
      coreFeaturesItems: this.getByPhase(Phase.CORE_FEATURES).length,
      enhancementItems: this.getByPhase(Phase.ENHANCEMENT).length,
      enterpriseItems: this.getByPhase(Phase.ENTERPRISE).length,
      mustDoRefactors,
      laterRefactors,
      highImpactItems,
      highRiskItems,
      avgPriorityScore
    };
  }

  generateDependencyGraph(): Record<string, string[]> {
    const graph: Record<string, string[]> = {};
    this.items.forEach(item => {
      graph[item.item] = item.dependencies;
    });
    return graph;
  }

  getReadyItems(): BacklogItemModel[] {
    const completed = new Set<string>();
    const ready: BacklogItemModel[] = [];

    for (const item of this.items) {
      if (item.dependencies.length === 0) {
        ready.push(item);
      } else if (item.dependencies.every(dep => completed.has(dep))) {
        ready.push(item);
      }
    }

    return ready;
  }

  getAllItems(): BacklogItemModel[] {
    return this.items;
  }

  exportJSON(): string {
    return JSON.stringify({
      totalItems: this.items.length,
      summary: this.getSummary(),
      items: this.items.map(item => item.toJSON())
    }, null, 2);
  }

  exportMarkdown(): string {
    let md = "# Product Backlog\n\n";
    md += `**Total Items:** ${this.items.length}\n\n`;

    const summary = this.getSummary();
    md += "## Summary\n\n";
    Object.entries(summary).forEach(([key, value]) => {
      const formattedKey = key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
      md += `- **${formattedKey}:** ${typeof value === 'number' ? value.toFixed(2) : value}\n`;
    });
    md += "\n";

    Object.values(Phase).forEach(phase => {
      const phaseItems = this.getByPhase(phase);
      if (phaseItems.length > 0) {
        md += `## ${phase.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}\n\n`;
        phaseItems.forEach(item => {
          md += `### ${item.item}\n\n`;
          md += `- **Priority Score:** ${item.priorityScore.toFixed(2)}\n`;
          md += `- **Impact:** ${item.impact}/5\n`;
          md += `- **Effort:** ${item.effort}/5\n`;
          md += `- **Risk:** ${item.risk}/5\n`;
          md += `- **Owner:** ${item.owner}\n`;
          md += `- **Test Hook:** \`${item.testHook}\`\n`;
          if (item.dependencies.length > 0) {
            md += `- **Dependencies:** ${item.dependencies.join(', ')}\n`;
          }
          if (item.isRefactor) {
            md += `- **Refactor Type:** ${item.refactorType}\n`;
            md += `- **Module Maturity Score:** ${item.moduleMaturityScore}\n`;
          }
          md += "\n";
        });
      }
    });

    return md;
  }
}

export function generateProductBacklog(): ProductBacklog {
  return new ProductBacklog();
}
