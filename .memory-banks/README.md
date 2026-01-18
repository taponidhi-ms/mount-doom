# Memory Banks

## What are Memory Banks?
Memory banks are structured documentation files that serve as the project's "institutional memory" - capturing important context, decisions, and patterns that may not be immediately obvious from reading code alone. Think of them as the project's knowledge base that helps both human developers and AI assistants understand the "why" behind the "what".

## Overview
This directory contains the "memory banks" for the Mount Doom project - living documentation that must stay synchronized with the codebase.

## Purpose
Memory banks provide critical project context that may not be immediately obvious from reading code alone. They serve as the single source of truth for:
- Architectural decisions and patterns
- Development conventions and best practices
- Feature workflows and requirements

## Files

### architecture.md
Documents the project's architecture, including:
- Backend and frontend structure
- Key principles and patterns
- Services and routes
- Data flow
- Authentication and error handling

### conventions.md
Documents development conventions, including:
- Code style guidelines (Python/TypeScript)
- Naming conventions
- File organization patterns
- API design standards
- Database strategies
- Testing approaches

### features.md
Documents the main features:
- Agents (persona distribution, persona generator, transcript parser, C2 message generation)
- Workflows (conversation simulation)
- Includes workflows, metrics, and implementation details for each

### antd-context.md
Documents Ant Design UI library context and usage, including:
- Core components used in the project
- Common patterns and conventions
- Integration with Next.js
- Accessibility best practices
- Styling approach
- Component usage examples
- Official documentation references

This file provides essential context for understanding and working with the Ant Design component library used throughout the frontend.

### antd-llms-reference.txt
Official llms.txt file from ant.design containing comprehensive links to:
- All Ant Design components documentation
- Design pattern guides and specifications
- React integration guides (Vite, Next.js, Umi, etc.)
- Advanced topics (theming, SSR, i18n, custom date libraries)
- Blog posts covering implementation details and best practices
- Migration guides for version upgrades

This is the official LLM context file provided by Ant Design for AI assistants and serves as a complete reference index.

## Usage Protocol

### Before Making Changes
**ALWAYS read these memory bank files first** before making any changes to the codebase. This ensures:
- Your changes align with existing patterns
- You understand the full context
- You avoid introducing inconsistencies

**Key files to read**:
- `architecture.md` - Project structure and patterns
- `conventions.md` - Development standards and best practices
- `features.md` - Feature workflows and requirements
- `antd-context.md` - Ant Design component library usage (for frontend UI work)
- `antd-llms-reference.txt` - Official Ant Design documentation index

### After Making Changes
**ALWAYS update the relevant memory bank files** when your changes affect:
- Architecture (new services, components, data flow changes)
- Conventions (new patterns, naming standards, coding practices)
- Features (new features, workflow changes, metric updates)

## Maintenance
These files are living documentation and must be updated whenever the codebase evolves. Failing to keep them synchronized makes future development harder and can lead to architectural drift.

## Questions?
If you're unsure whether your change requires a memory bank update, ask yourself:
- Would someone working on this project 6 months from now benefit from knowing about this change?
- Does this change introduce a new pattern or convention?
- Does this change affect the overall architecture or a feature workflow?

If the answer to any of these is "yes", update the appropriate memory bank file.
