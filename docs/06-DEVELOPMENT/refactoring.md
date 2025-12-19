# Refactoring Plan: Ports & Adapters

Goal: make the codebase more elegant, testable, and maintainable by isolating external dependencies and standardizing orchestration.

## Key Concepts

- Source: fetches input (local file, SharePoint, OneDrive)
- Extractor: produces structured artifacts (paper/talk/repo agents)
- LLMProvider: model client (Azure AI Foundry, OpenAI, etc.)
- Sink: persists artifacts (filesystem, SharePoint, API)
- Notifier: sends updates (Teams, Power Automate flows)

## Entry Point

- New module: [knowledge-agent-poc/core_interfaces.py](../../knowledge-agent-poc/core_interfaces.py)
- Example: [knowledge-agent-poc/refactor_examples.py](../../knowledge-agent-poc/refactor_examples.py)

## Incremental Migration

1. Wrap existing agents to implement `Extractor.extract(raw, provider) -> dict`.
2. Add adapters:
   - `SharePointSource` and `OneDriveSource` using `m365_connector.py`
   - `SharePointSink` (save JSON artifacts back to libraries)
   - `TeamsNotifier` using Graph/Connectors
3. Add `FoundryProviderAdapter` that satisfies `LLMProvider.generate()`.
4. Replace bespoke orchestration with `ExtractionPipeline` for new routes and CLI paths.

## Testing Strategy

- Use stub adapters and run focused pipeline tests (see `tests/test_pipeline_refactor.py`).
- Mock HTTP with `respx` for `httpx` clients; mock MSAL tokens for Graph.
- Keep tests close to adapters; avoid end-to-end dependency coupling.

## Benefits

- Clear seams for external systems; easier mocking and substitution.
- Smaller, composable units; fewer cross-module imports.
- Consistent artifact format and save/notify life cycle.

## Next Steps

- Introduce a shared `http_client` wrapper with retries and timeouts.
- Define artifact schema package and validators.
- Add Teams/Power Automate notifiers behind the `Notifier` protocol.

