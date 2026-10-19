# Atlas Phase 1 patch register

Base: official v0.22.2 / d923a5eb487a17c0a68801bba9ef0f56c81040a8.

- H01 bootstrap: `agent/managed_runtime.py` and `tools/registry.py` enforce a required authenticated owner/profile context at final registry dispatch for the two enabled fixture reads. Every other registered tool is denied while the source-tree managed manifest is present. No effect capability tokens or production write grants are enabled. Inline tools and arbitrary execution still require the full Phase 1 containment proof before enabling them.
- H02: reuse update admission with an immutable-tree managed manifest and refuse direct update implementation entry before any mutation. Automatic upstream integration remains controller-owned future work; this does not create a watcher or disable that requirement.
- H03: companion ingress currently admits owner-only, synthetic, read-only requests. Private/contact model requests and unrestricted shell/network are not enabled. Full auxiliary/model egress and sandbox containment are outstanding release gates; the bootstrap is not production-ready.
- H04: no patch. Use the dedicated memory-provider entry point; the current provider is a read-only fixture activation spike, not migrated personal memory.

Regression tests live in mirrored `tests/agent/`, `tests/tools/` and `tests/hermes_cli/` locations according to upstream AGENTS.md, rather than the preliminary brief's proposed `tests/atlas_contract/` directory. Use `scripts/run_tests.sh`.

Retire each patch only when equivalent upstream behavior passes the same execution and identity contracts. Candidate and production manifests must pin both companion and fork SHAs. The development manifest is not a signed production release.
