# Notes Directory

This folder is intended for personal notes, scratch files, and ad-hoc artifacts related to the project. It is tracked in Git so files can be shared or versioned, but its contents are considered private and non-source.

Important:
- Do not read, parse, or reference files in this directory for memory banks or any AI/Copilot workflows.
- Do not import or depend on files in `notes/` from application code.
- Avoid committing secrets or sensitive data. Prefer environment variables or secure stores.
- Large binaries should be avoided; use external storage when possible.

Scope:
- The `notes/` directory is not part of the project’s architecture, conventions, or use cases.
- CI/CD, documentation generators, and analysis tools should ignore `notes/` content unless explicitly needed.

If you need to share non-private information broadly, prefer adding appropriate documentation under the repository’s standard docs or READMEs instead of `notes/`.