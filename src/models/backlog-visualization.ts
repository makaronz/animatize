/**
 * Product Backlog Visualization Utilities
 * 
 * Provides data transformation and formatting for backlog visualization
 */

import { ProductBacklog, BacklogItemModel, Phase, Owner, RefactorType } from './product-backlog';

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface ScatterDataPoint {
  x: number;
  y: number;
  label: string;
  size?: number;
  color?: string;
}

export interface DependencyNode {
  id: string;
  label: string;
  level: number;
  phase: Phase;
  priority: number;
}

export interface DependencyEdge {
  source: string;
  target: string;
}

export class BacklogVisualization {
  constructor(private backlog: ProductBacklog) {}

  /**
   * Generate data for impact/effort scatter plot
   */
  getImpactEffortScatter(): ScatterDataPoint[] {
    return this.backlog.getAllItems().map(item => ({
      x: item.effort,
      y: item.impact,
      label: item.item,
      size: item.risk * 10,
      color: this.getPhaseColor(item.phase!)
    }));
  }

  /**
   * Generate data for priority distribution chart
   */
  getPriorityDistribution(): ChartDataPoint[] {
    const ranges = [
      { label: 'Very High (2.0+)', min: 2.0, max: Infinity },
      { label: 'High (1.5-2.0)', min: 1.5, max: 2.0 },
      { label: 'Medium (1.0-1.5)', min: 1.0, max: 1.5 },
      { label: 'Low (0.5-1.0)', min: 0.5, max: 1.0 },
      { label: 'Very Low (<0.5)', min: 0, max: 0.5 }
    ];

    return ranges.map(range => ({
      label: range.label,
      value: this.backlog.getAllItems().filter(
        item => item.priorityScore >= range.min && item.priorityScore < range.max
      ).length,
      color: this.getPriorityColor(range.min)
    }));
  }

  /**
   * Generate data for phase breakdown
   */
  getPhaseBreakdown(): ChartDataPoint[] {
    return Object.values(Phase).map(phase => ({
      label: this.formatPhaseLabel(phase),
      value: this.backlog.getByPhase(phase).length,
      color: this.getPhaseColor(phase)
    }));
  }

  /**
   * Generate data for owner workload
   */
  getOwnerWorkload(): ChartDataPoint[] {
    return Object.values(Owner).map(owner => ({
      label: owner,
      value: this.backlog.getByOwner(owner).length,
      color: this.getOwnerColor(owner)
    }));
  }

  /**
   * Generate data for effort distribution by owner
   */
  getOwnerEffortDistribution(): Record<string, number> {
    const distribution: Record<string, number> = {};
    
    Object.values(Owner).forEach(owner => {
      const items = this.backlog.getByOwner(owner);
      distribution[owner] = items.reduce((sum, item) => sum + item.effort, 0);
    });
    
    return distribution;
  }

  /**
   * Generate data for risk analysis
   */
  getRiskAnalysis(): ChartDataPoint[] {
    const risks = [1, 2, 3, 4, 5];
    return risks.map(risk => ({
      label: `Risk ${risk}`,
      value: this.backlog.getAllItems().filter(item => item.risk === risk).length,
      color: this.getRiskColor(risk)
    }));
  }

  /**
   * Generate dependency graph nodes and edges
   */
  getDependencyGraph(): { nodes: DependencyNode[], edges: DependencyEdge[] } {
    const items = this.backlog.getAllItems();
    const nodes: DependencyNode[] = items.map(item => ({
      id: item.item,
      label: this.truncateLabel(item.item, 30),
      level: this.calculateNodeLevel(item.item, items),
      phase: item.phase!,
      priority: item.priorityScore
    }));

    const edges: DependencyEdge[] = [];
    items.forEach(item => {
      item.dependencies.forEach(dep => {
        edges.push({
          source: dep,
          target: item.item
        });
      });
    });

    return { nodes, edges };
  }

  /**
   * Generate refactor priority matrix
   */
  getRefactorMatrix(): Array<{
    item: string;
    maturityScore: number;
    priorityScore: number;
    type: RefactorType;
    phase: Phase;
  }> {
    return this.backlog.getRefactors().map(item => ({
      item: item.item,
      maturityScore: item.moduleMaturityScore || 0,
      priorityScore: item.priorityScore,
      type: item.refactorType!,
      phase: item.phase!
    }));
  }

  /**
   * Generate timeline view data by phase
   */
  getTimelineView(): Array<{
    phase: Phase;
    items: Array<{
      name: string;
      priority: number;
      effort: number;
      dependencies: string[];
    }>;
  }> {
    return Object.values(Phase).map(phase => ({
      phase,
      items: this.backlog.getByPhase(phase).map(item => ({
        name: item.item,
        priority: item.priorityScore,
        effort: item.effort,
        dependencies: item.dependencies
      }))
    }));
  }

  /**
   * Generate burndown projection
   */
  getBurndownProjection(velocityPerSprint: number = 20): Array<{
    sprint: number;
    remainingEffort: number;
    completedItems: number;
  }> {
    const sortedItems = [...this.backlog.getAllItems()].sort(
      (a, b) => b.priorityScore - a.priorityScore
    );
    
    let totalEffort = sortedItems.reduce((sum, item) => sum + item.effort, 0);
    let completedItems = 0;
    let sprint = 0;
    const projection = [];

    projection.push({ sprint: 0, remainingEffort: totalEffort, completedItems: 0 });

    let currentVelocity = 0;
    for (const item of sortedItems) {
      if (currentVelocity + item.effort > velocityPerSprint) {
        sprint++;
        projection.push({
          sprint,
          remainingEffort: totalEffort - currentVelocity,
          completedItems
        });
        currentVelocity = 0;
      }
      
      currentVelocity += item.effort;
      completedItems++;
      totalEffort -= item.effort;
    }

    if (currentVelocity > 0) {
      sprint++;
      projection.push({ sprint, remainingEffort: 0, completedItems });
    }

    return projection;
  }

  /**
   * Get color for phase
   */
  private getPhaseColor(phase: Phase): string {
    const colors = {
      [Phase.FOUNDATION]: '#3B82F6',
      [Phase.CORE_FEATURES]: '#10B981',
      [Phase.ENHANCEMENT]: '#F59E0B',
      [Phase.ENTERPRISE]: '#8B5CF6'
    };
    return colors[phase] || '#6B7280';
  }

  /**
   * Get color for owner
   */
  private getOwnerColor(owner: Owner): string {
    const colors = {
      [Owner.RND]: '#EF4444',
      [Owner.BACKEND]: '#3B82F6',
      [Owner.FRONTEND]: '#10B981',
      [Owner.DESIGN]: '#F59E0B'
    };
    return colors[owner] || '#6B7280';
  }

  /**
   * Get color for priority
   */
  private getPriorityColor(priority: number): string {
    if (priority >= 2.0) return '#10B981';
    if (priority >= 1.5) return '#3B82F6';
    if (priority >= 1.0) return '#F59E0B';
    if (priority >= 0.5) return '#EF4444';
    return '#6B7280';
  }

  /**
   * Get color for risk
   */
  private getRiskColor(risk: number): string {
    const colors = ['#10B981', '#3B82F6', '#F59E0B', '#F97316', '#EF4444'];
    return colors[risk - 1] || '#6B7280';
  }

  /**
   * Format phase label for display
   */
  private formatPhaseLabel(phase: Phase): string {
    return phase.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  /**
   * Truncate label to max length
   */
  private truncateLabel(label: string, maxLength: number): string {
    return label.length > maxLength
      ? label.substring(0, maxLength - 3) + '...'
      : label;
  }

  /**
   * Calculate node level in dependency graph
   */
  private calculateNodeLevel(itemName: string, allItems: BacklogItemModel[]): number {
    const item = allItems.find(i => i.item === itemName);
    if (!item || item.dependencies.length === 0) {
      return 0;
    }

    const depLevels = item.dependencies.map(dep =>
      this.calculateNodeLevel(dep, allItems)
    );
    return Math.max(...depLevels) + 1;
  }

  /**
   * Export visualization data as JSON
   */
  exportVisualizationData(): string {
    return JSON.stringify({
      impactEffortScatter: this.getImpactEffortScatter(),
      priorityDistribution: this.getPriorityDistribution(),
      phaseBreakdown: this.getPhaseBreakdown(),
      ownerWorkload: this.getOwnerWorkload(),
      ownerEffortDistribution: this.getOwnerEffortDistribution(),
      riskAnalysis: this.getRiskAnalysis(),
      dependencyGraph: this.getDependencyGraph(),
      refactorMatrix: this.getRefactorMatrix(),
      timelineView: this.getTimelineView(),
      burndownProjection: this.getBurndownProjection()
    }, null, 2);
  }
}

/**
 * Generate HTML report with visualizations
 */
export function generateHTMLReport(backlog: ProductBacklog): string {
  const viz = new BacklogVisualization(backlog);
  const summary = backlog.getSummary();

  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Backlog Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .section {
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h2 {
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .item {
            padding: 15px;
            margin: 10px 0;
            background: #f9f9f9;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }
        .item-title {
            font-weight: bold;
            color: #333;
        }
        .item-meta {
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            margin-right: 5px;
        }
        .badge-high { background: #10B981; color: white; }
        .badge-medium { background: #F59E0B; color: white; }
        .badge-low { background: #EF4444; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Product Backlog Report</h1>
        <p>Comprehensive analysis of ${summary.totalItems} backlog items</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">${summary.totalItems}</div>
            <div class="stat-label">Total Items</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${summary.mustDoRefactors}</div>
            <div class="stat-label">Must-Do Refactors</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${summary.highImpactItems}</div>
            <div class="stat-label">High Impact Items</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${summary.avgPriorityScore.toFixed(2)}</div>
            <div class="stat-label">Avg Priority Score</div>
        </div>
    </div>

    <div class="section">
        <h2>Top Priority Items</h2>
        ${backlog.getAllItems().slice(0, 10).map(item => `
            <div class="item">
                <div class="item-title">${item.item}</div>
                <div class="item-meta">
                    <span class="badge ${item.priorityScore >= 1.5 ? 'badge-high' : item.priorityScore >= 1.0 ? 'badge-medium' : 'badge-low'}">
                        Priority: ${item.priorityScore.toFixed(2)}
                    </span>
                    <span class="badge badge-medium">Impact: ${item.impact}/5</span>
                    <span class="badge badge-medium">Effort: ${item.effort}/5</span>
                    <span class="badge badge-medium">Risk: ${item.risk}/5</span>
                    <span class="badge badge-medium">${item.owner}</span>
                </div>
            </div>
        `).join('')}
    </div>

    <div class="section">
        <h2>Phase Distribution</h2>
        ${viz.getPhaseBreakdown().map(phase => `
            <div style="margin: 10px 0;">
                <strong>${phase.label}:</strong> ${phase.value} items
                <div style="background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden; margin-top: 5px;">
                    <div style="background: ${phase.color}; width: ${(phase.value / summary.totalItems * 100)}%; height: 100%;"></div>
                </div>
            </div>
        `).join('')}
    </div>

    <div class="section">
        <h2>Refactor Items</h2>
        <h3>Must-Do Refactors</h3>
        ${backlog.getRefactors(RefactorType.MUST_DO).map(item => `
            <div class="item">
                <div class="item-title">${item.item}</div>
                <div class="item-meta">
                    Maturity Score: ${item.moduleMaturityScore} | 
                    Priority: ${item.priorityScore.toFixed(2)} | 
                    Phase: ${item.phase}
                </div>
            </div>
        `).join('')}
    </div>

    <script>
        const vizData = ${viz.exportVisualizationData()};
        console.log('Visualization Data:', vizData);
    </script>
</body>
</html>
`;
}
