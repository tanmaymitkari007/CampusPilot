# Graph Report - CampusPilot  (2026-10-22)

## Corpus Check
- Corpus is ~6,059 words - fits in a single context window. You may not need a graph.

## Summary
- 128 nodes · 220 edges · 12 communities (6 shown, 6 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- AI Provider Adapters
- WhatsApp Import Pipeline
- Task Deadline Processing
- Frontend Build Tooling
- Frontend Package Metadata
- CampusPilot Interface
- Graphify Instructions
- Social Icon Sprite
- Hero Illustration
- React Logo Asset
- Vite Logo Asset

## God Nodes (most connected - your core abstractions)
1. `AIProvider` - 10 edges
2. `process_whatsapp_zip()` - 10 edges
3. `build_deadline_report()` - 9 edges
4. `extract_tasks()` - 9 edges
5. `OllamaProvider` - 7 edges
6. `ExtractedTask` - 7 edges
7. `parse_whatsapp_zip()` - 7 edges
8. `create_provider()` - 6 edges
9. `generate_with_fallback()` - 6 edges
10. `GemmaProvider` - 6 edges

## Surprising Connections (you probably didn't know these)
- `process_whatsapp_zip()` --uses--> `ExtractedTask`  [INFERRED]
  backend/pipeline.py → backend/extraction.py
- `extract_tasks()` --uses--> `ChatMessage`  [INFERRED]
  backend/extraction.py → backend/parser.py
- `React and Vite Starter Template` --references--> `react`  [EXTRACTED]
  frontend/README.md → frontend/package.json
- `React and Vite Starter Template` --references--> `vite`  [EXTRACTED]
  frontend/README.md → frontend/package.json
- `Graphify Skill Trigger` --references--> `Graphify Repository Workflow`  [EXTRACTED]
  .claude/CLAUDE.md → CLAUDE.md

## Import Cycles
- None detected.

## Communities (12 total, 6 thin omitted)

### Community 0 - "AI Provider Adapters"
Cohesion: 0.18
Nodes (6): AIProvider, create_provider(), generate_with_fallback(), get_provider(), GemmaProvider, OllamaProvider

### Community 1 - "WhatsApp Import Pipeline"
Cohesion: 0.15
Nodes (8): analyze_chat(), health(), ChatMessage, group_messages_by_day(), parse_chat_text(), parse_timestamp(), parse_whatsapp_zip(), process_whatsapp_zip()

### Community 2 - "Task Deadline Processing"
Cohesion: 0.17
Nodes (8): build_deadline_report(), has_explicit_year(), normalize_title(), urgency_for(), extract_tasks(), ExtractedTask, ExtractionResult, _parse_json_response()

### Community 3 - "Frontend Build Tooling"
Cohesion: 0.12
Nodes (18): name, private, scripts, build, dev, lint, preview, type (+10 more)

### Community 4 - "Frontend Package Metadata"
Cohesion: 0.12
Nodes (16): dependencies, react, react-dom, devDependencies, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+8 more)

### Community 5 - "CampusPilot Interface"
Cohesion: 0.19
Nodes (8): Frontend HTML Shell, Purple Lightning Favicon, App(), initialTasks, navItems, StatCard(), react, react-dom

## Knowledge Gaps
- **11 isolated node(s):** `@types/react`, `@types/react-dom`, `Graphify Skill Trigger`, `Graphify Repository Workflow`, `React Compiler Guidance` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 56 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `devDependencies` connect `Frontend Package Metadata` to `Frontend Build Tooling`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `AIProvider` (e.g. with `create_provider()` and `get_provider()`) actually correct?**
  _`AIProvider` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `@types/react`, `@types/react-dom`, `Graphify Skill Trigger` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Frontend Build Tooling` be split into smaller, more focused modules?**
  _Cohesion score 0.11904761904761904 - nodes in this community are weakly interconnected._
- **Why does `react` connect `CampusPilot Interface` to `Frontend Build Tooling`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Should `Frontend Package Metadata` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Why does `process_whatsapp_zip()` connect `WhatsApp Import Pipeline` to `Task Deadline Processing`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._