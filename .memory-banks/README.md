# Memory Banks

## Overview
This directory contains the "memory banks" for the Mount Doom project - living documentation that must stay synchronized with the codebase.

## Purpose
Memory banks provide critical project context that may not be immediately obvious from reading code alone. They serve as the single source of truth for:
- Architectural decisions and patterns
- Development conventions and best practices
- Use case workflows and requirements

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

### use-cases.md
Documents the four main use cases:
1. Persona Generation
2. General Prompt
3. Prompt Validator
4. Conversation Simulation

Includes workflows, metrics, and implementation details for each.

## For GitHub Copilot

### Before Making Changes
**ALWAYS read these memory bank files first** before making any changes to the codebase. This ensures:
- Your changes align with existing patterns
- You understand the full context
- You avoid introducing inconsistencies

### After Making Changes
**ALWAYS update the relevant memory bank files** when your changes affect:
- Architecture (new services, components, data flow changes)
- Conventions (new patterns, naming standards, coding practices)
- Use cases (new features, workflow changes, metric updates)

## Maintenance
These files are living documentation and must be updated whenever the codebase evolves. Failing to keep them synchronized makes future development harder and can lead to architectural drift.

## Questions?
If you're unsure whether your change requires a memory bank update, ask yourself:
- Would someone working on this project 6 months from now benefit from knowing about this change?
- Does this change introduce a new pattern or convention?
- Does this change affect the overall architecture or a use case workflow?

If the answer to any of these is "yes", update the appropriate memory bank file.
