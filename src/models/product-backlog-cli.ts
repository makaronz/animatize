#!/usr/bin/env node
/**
 * Product Backlog CLI Tool
 * 
 * Command-line interface for managing and exporting product backlog
 */

import { ProductBacklog, Phase, Owner, RefactorType } from './product-backlog';
import * as fs from 'fs';
import * as path from 'path';

interface CLIOptions {
  command: string;
  args: string[];
}

function parseArgs(): CLIOptions {
  const args = process.argv.slice(2);
  return {
    command: args[0] || 'help',
    args: args.slice(1)
  };
}

function displayHelp(): void {
  console.log(`
Product Backlog Management CLI

Usage: node product-backlog-cli.js [command] [options]

Commands:
  generate         Generate and display backlog summary
  list [phase]     List all items or filter by phase (foundation|core_features|enhancement|enterprise)
  owner [owner]    Filter items by owner (RND|BE|FE|Design)
  refactors [type] Show refactor items (must_do|later)
  priority [score] Show items with priority >= score
  risk [max]       Show items with risk <= max
  export-json [path]    Export backlog to JSON file
  export-md [path]      Export backlog to Markdown file
  summary          Show detailed summary statistics
  dependencies     Show dependency graph
  ready            Show items ready to be started
  help             Show this help message

Examples:
  node product-backlog-cli.js generate
  node product-backlog-cli.js list foundation
  node product-backlog-cli.js owner RND
  node product-backlog-cli.js refactors must_do
  node product-backlog-cli.js priority 1.5
  node product-backlog-cli.js export-json ./backlog.json
  node product-backlog-cli.js export-md ./backlog.md
`);
}

function displaySummary(backlog: ProductBacklog): void {
  const summary = backlog.getSummary();
  console.log('\n=== Product Backlog Summary ===\n');
  console.log(`Total Items: ${summary.totalItems}`);
  console.log(`Foundation Items: ${summary.foundationItems}`);
  console.log(`Core Features Items: ${summary.coreFeaturesItems}`);
  console.log(`Enhancement Items: ${summary.enhancementItems}`);
  console.log(`Enterprise Items: ${summary.enterpriseItems}`);
  console.log(`Must-Do Refactors: ${summary.mustDoRefactors}`);
  console.log(`Later Refactors: ${summary.laterRefactors}`);
  console.log(`High Impact Items (4+): ${summary.highImpactItems}`);
  console.log(`High Risk Items (4+): ${summary.highRiskItems}`);
  console.log(`Avg Priority Score: ${summary.avgPriorityScore.toFixed(2)}`);
  console.log();
}

function displayItems(items: any[], title: string): void {
  console.log(`\n=== ${title} ===\n`);
  if (items.length === 0) {
    console.log('No items found.');
    return;
  }
  
  items.forEach((item, index) => {
    console.log(`${index + 1}. [${item.priorityScore.toFixed(2)}] ${item.item}`);
    console.log(`   Owner: ${item.owner} | Impact: ${item.impact}/5 | Effort: ${item.effort}/5 | Risk: ${item.risk}/5`);
    console.log(`   Phase: ${item.phase} | Test: ${item.testHook}`);
    if (item.dependencies.length > 0) {
      console.log(`   Dependencies: ${item.dependencies.join(', ')}`);
    }
    if (item.isRefactor) {
      console.log(`   Refactor Type: ${item.refactorType} | Maturity: ${item.moduleMaturityScore}`);
    }
    console.log();
  });
}

function main(): void {
  const { command, args } = parseArgs();
  const backlog = new ProductBacklog();

  switch (command) {
    case 'generate':
      displaySummary(backlog);
      console.log('=== Top 10 Priority Items ===\n');
      backlog.getAllItems().slice(0, 10).forEach((item, i) => {
        console.log(`${i + 1}. [${item.priorityScore.toFixed(2)}] ${item.item} (${item.owner})`);
      });
      console.log();
      break;

    case 'list':
      if (args.length === 0) {
        displayItems(backlog.getAllItems(), 'All Backlog Items');
      } else {
        const phase = args[0].toUpperCase() as keyof typeof Phase;
        if (Phase[phase]) {
          const items = backlog.getByPhase(Phase[phase]);
          displayItems(items, `${phase} Phase Items`);
        } else {
          console.error(`Invalid phase: ${args[0]}`);
          console.log('Valid phases: foundation, core_features, enhancement, enterprise');
        }
      }
      break;

    case 'owner':
      if (args.length === 0) {
        console.error('Please specify an owner: RND, BE, FE, or Design');
      } else {
        const ownerKey = args[0].toUpperCase().replace('&', '') as keyof typeof Owner;
        if (Owner[ownerKey]) {
          const items = backlog.getByOwner(Owner[ownerKey]);
          displayItems(items, `${args[0]} Owner Items`);
        } else {
          console.error(`Invalid owner: ${args[0]}`);
          console.log('Valid owners: RND, BE, FE, Design');
        }
      }
      break;

    case 'refactors':
      if (args.length === 0) {
        displayItems(backlog.getRefactors(), 'All Refactor Items');
      } else {
        const type = args[0].toUpperCase() as keyof typeof RefactorType;
        if (RefactorType[type]) {
          const items = backlog.getRefactors(RefactorType[type]);
          displayItems(items, `${args[0]} Refactor Items`);
        } else {
          console.error(`Invalid refactor type: ${args[0]}`);
          console.log('Valid types: must_do, later');
        }
      }
      break;

    case 'priority':
      if (args.length === 0) {
        console.error('Please specify a priority score threshold');
      } else {
        const threshold = parseFloat(args[0]);
        if (!isNaN(threshold)) {
          const items = backlog.getHighPriority(threshold);
          displayItems(items, `High Priority Items (>= ${threshold})`);
        } else {
          console.error('Invalid priority score');
        }
      }
      break;

    case 'risk':
      if (args.length === 0) {
        console.error('Please specify a maximum risk level (1-5)');
      } else {
        const maxRisk = parseInt(args[0]);
        if (!isNaN(maxRisk) && maxRisk >= 1 && maxRisk <= 5) {
          const items = backlog.getByRisk(maxRisk);
          displayItems(items, `Items with Risk <= ${maxRisk}`);
        } else {
          console.error('Invalid risk level (must be 1-5)');
        }
      }
      break;

    case 'export-json':
      const jsonPath = args[0] || './data/product_backlog.json';
      try {
        const dir = path.dirname(jsonPath);
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }
        fs.writeFileSync(jsonPath, backlog.exportJSON());
        console.log(`✓ Exported backlog to ${jsonPath}`);
      } catch (error) {
        console.error(`Error exporting to JSON: ${error}`);
      }
      break;

    case 'export-md':
      const mdPath = args[0] || './docs/PRODUCT_BACKLOG.md';
      try {
        const dir = path.dirname(mdPath);
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }
        fs.writeFileSync(mdPath, backlog.exportMarkdown());
        console.log(`✓ Exported backlog to ${mdPath}`);
      } catch (error) {
        console.error(`Error exporting to Markdown: ${error}`);
      }
      break;

    case 'summary':
      displaySummary(backlog);
      break;

    case 'dependencies':
      const graph = backlog.generateDependencyGraph();
      console.log('\n=== Dependency Graph ===\n');
      Object.entries(graph).forEach(([item, deps]) => {
        if (deps.length > 0) {
          console.log(`${item}:`);
          deps.forEach(dep => console.log(`  → ${dep}`));
          console.log();
        }
      });
      break;

    case 'ready':
      const readyItems = backlog.getReadyItems();
      displayItems(readyItems, 'Ready to Start Items (No Dependencies)');
      break;

    case 'help':
    default:
      displayHelp();
      break;
  }
}

if (require.main === module) {
  main();
}

export { main };
