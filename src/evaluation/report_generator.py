"""
Automated Comparison Report Generator
Generates detailed HTML and PDF reports comparing models and versions
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import base64


class ReportGenerator:
    """Generates comparison reports in various formats"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_html_report(
        self,
        comparison_data: Dict[str, Any],
        report_title: str,
        output_filename: str = "comparison_report.html"
    ) -> str:
        """
        Generate HTML comparison report
        
        Args:
            comparison_data: Comparison results data
            report_title: Title of the report
            output_filename: Output filename
        
        Returns:
            Path to generated report
        """
        html_content = self._build_html_report(comparison_data, report_title)
        
        output_path = self.output_dir / output_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)
    
    def _build_html_report(
        self,
        data: Dict[str, Any],
        title: str
    ) -> str:
        """Build HTML report content"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .summary {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .metric-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}
        .status-pass {{
            color: #28a745;
        }}
        .status-fail {{
            color: #dc3545;
        }}
        .status-degraded {{
            color: #ffc107;
        }}
        .comparison-table {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .delta-positive {{
            color: #28a745;
        }}
        .delta-negative {{
            color: #dc3545;
        }}
        .delta-neutral {{
            color: #6c757d;
        }}
        .chart-container {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
"""
        
        # Add summary section
        if "summary" in data:
            html += self._build_summary_section(data["summary"])
        
        # Add comparison details
        if "comparisons" in data:
            html += self._build_comparisons_section(data["comparisons"])
        
        # Add regression results
        if "results" in data:
            html += self._build_regression_results_section(data["results"])
        
        html += """
    <div class="footer">
        <p>Video Generation Evaluation System</p>
    </div>
</body>
</html>
"""
        
        return html
    
    def _build_summary_section(self, summary: Dict[str, Any]) -> str:
        """Build summary section HTML"""
        html = '<div class="summary">\n<h2>Summary</h2>\n<div class="summary-grid">\n'
        
        # Determine status class
        status_class = "status-pass"
        if "overall_status" in summary:
            status = summary["overall_status"]
            if status == "FAIL":
                status_class = "status-fail"
            elif status == "DEGRADED":
                status_class = "status-degraded"
        
        # Add metric cards
        metrics = [
            ("Total Tests", summary.get("total_tests", 0), ""),
            ("Passed", summary.get("passed", 0), "status-pass"),
            ("Failed", summary.get("failed", 0), "status-fail"),
            ("Pass Rate", f"{summary.get('pass_rate', 0):.1f}%", status_class)
        ]
        
        for label, value, status_cls in metrics:
            html += f'''
<div class="metric-card">
    <h3>{label}</h3>
    <div class="metric-value {status_cls}">{value}</div>
</div>
'''
        
        html += '</div>\n</div>\n'
        return html
    
    def _build_comparisons_section(self, comparisons: Dict[str, Any]) -> str:
        """Build comparisons section HTML"""
        html = '<div class="comparison-table">\n<h2>Detailed Comparisons</h2>\n'
        html += '<table>\n<thead>\n<tr>\n'
        html += '<th>Scenario</th><th>Metric</th><th>Baseline</th><th>Test</th><th>Delta</th><th>Status</th>\n'
        html += '</tr>\n</thead>\n<tbody>\n'
        
        for scenario_id, scenario_data in comparisons.items():
            scenario_name = scenario_data.get("scenario_name", scenario_id)
            metrics = scenario_data.get("metrics", {})
            
            for metric_name, metric_data in metrics.items():
                baseline = metric_data.get("baseline_score", 0)
                test = metric_data.get("test_score", 0)
                delta = metric_data.get("delta", 0)
                winner = metric_data.get("winner", "tie")
                
                delta_class = "delta-neutral"
                if delta > 0:
                    delta_class = "delta-positive"
                    delta_str = f"+{delta:.3f}"
                elif delta < 0:
                    delta_class = "delta-negative"
                    delta_str = f"{delta:.3f}"
                else:
                    delta_str = "0.000"
                
                status = "✅" if winner == "test" else ("❌" if winner == "baseline" else "➖")
                
                html += f'''<tr>
    <td>{scenario_name}</td>
    <td>{metric_name.replace("_", " ").title()}</td>
    <td>{baseline:.3f}</td>
    <td>{test:.3f}</td>
    <td class="{delta_class}">{delta_str}</td>
    <td>{status}</td>
</tr>\n'''
        
        html += '</tbody>\n</table>\n</div>\n'
        return html
    
    def _build_regression_results_section(self, results: List[Dict[str, Any]]) -> str:
        """Build regression results section HTML"""
        html = '<div class="comparison-table">\n<h2>Regression Test Results</h2>\n'
        html += '<table>\n<thead>\n<tr>\n'
        html += '<th>Scenario ID</th><th>Status</th><th>Delta</th><th>Failed Metrics</th><th>Degraded Metrics</th>\n'
        html += '</tr>\n</thead>\n<tbody>\n'
        
        for result in results:
            scenario_id = result.get("scenario_id", "unknown")
            status = result.get("status", "unknown")
            delta_pct = result.get("delta_percentage", 0)
            failing = ", ".join(result.get("failing_metrics", []))
            degraded = ", ".join(result.get("degraded_metrics", []))
            
            status_class = "status-pass"
            status_icon = "✅"
            if status == "fail":
                status_class = "status-fail"
                status_icon = "❌"
            elif status == "degraded":
                status_class = "status-degraded"
                status_icon = "⚠️"
            
            delta_class = "delta-positive" if delta_pct > 0 else ("delta-negative" if delta_pct < 0 else "delta-neutral")
            
            html += f'''<tr>
    <td>{scenario_id}</td>
    <td class="{status_class}">{status_icon} {status.upper()}</td>
    <td class="{delta_class}">{delta_pct:+.2f}%</td>
    <td>{failing or "-"}</td>
    <td>{degraded or "-"}</td>
</tr>\n'''
        
        html += '</tbody>\n</table>\n</div>\n'
        return html
    
    def generate_markdown_report(
        self,
        comparison_data: Dict[str, Any],
        report_title: str,
        output_filename: str = "comparison_report.md"
    ) -> str:
        """Generate Markdown comparison report"""
        md = f"# {report_title}\n\n"
        md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Summary
        if "summary" in comparison_data:
            md += "## Summary\n\n"
            summary = comparison_data["summary"]
            md += f"- **Total Tests:** {summary.get('total_tests', 0)}\n"
            md += f"- **Passed:** {summary.get('passed', 0)}\n"
            md += f"- **Failed:** {summary.get('failed', 0)}\n"
            md += f"- **Pass Rate:** {summary.get('pass_rate', 0):.1f}%\n\n"
        
        # Comparisons
        if "comparisons" in comparison_data:
            md += "## Detailed Comparisons\n\n"
            for scenario_id, scenario_data in comparison_data["comparisons"].items():
                scenario_name = scenario_data.get("scenario_name", scenario_id)
                md += f"### {scenario_name}\n\n"
                md += "| Metric | Baseline | Test | Delta | Winner |\n"
                md += "|--------|----------|------|-------|--------|\n"
                
                for metric_name, metric_data in scenario_data.get("metrics", {}).items():
                    baseline = metric_data.get("baseline_score", 0)
                    test = metric_data.get("test_score", 0)
                    delta = metric_data.get("delta", 0)
                    winner = metric_data.get("winner", "tie")
                    
                    md += f"| {metric_name} | {baseline:.3f} | {test:.3f} | {delta:+.3f} | {winner} |\n"
                
                md += "\n"
        
        output_path = self.output_dir / output_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)
        
        return str(output_path)
    
    def generate_json_report(
        self,
        comparison_data: Dict[str, Any],
        output_filename: str = "comparison_report.json"
    ) -> str:
        """Generate JSON comparison report"""
        output_path = self.output_dir / output_filename
        
        with open(output_path, 'w') as f:
            json.dump(comparison_data, f, indent=2)
        
        return str(output_path)


def generate_all_reports(
    comparison_data: Dict[str, Any],
    title: str,
    output_dir: str = "reports"
) -> Dict[str, str]:
    """
    Generate reports in all formats
    
    Returns:
        Dictionary mapping format to file path
    """
    generator = ReportGenerator(output_dir=output_dir)
    
    reports = {
        "html": generator.generate_html_report(
            comparison_data, title, "comparison_report.html"
        ),
        "markdown": generator.generate_markdown_report(
            comparison_data, title, "comparison_report.md"
        ),
        "json": generator.generate_json_report(
            comparison_data, "comparison_report.json"
        )
    }
    
    return reports
