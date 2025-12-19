from __future__ import annotations

from typing import Any, Dict, Optional

from knowledge-agent-poc.core_interfaces import ExtractionPipeline


class StubSource:
    def __init__(self) -> None:
        self.fetched: Optional[str] = None

    def fetch(self, resource_id: str) -> Any:
        self.fetched = resource_id
        return "hello world"


class StubExtractor:
    def __init__(self) -> None:
        self.called: bool = False

    def extract(self, raw: Any, provider=None) -> Dict[str, Any]:
        self.called = True
        return {"id": "hello", "title": "Hello", "summary": "ok"}


class StubSink:
    def __init__(self) -> None:
        self.saved: Optional[Dict[str, Any]] = None

    def save(self, artifact: Dict[str, Any]) -> str:
        self.saved = artifact
        return "mem://artifact"


class StubNotifier:
    def __init__(self) -> None:
        self.messages: list[tuple[str, Dict[str, Any] | None]] = []

    def notify(self, message: str, meta: Optional[Dict[str, Any]] = None) -> None:
        self.messages.append((message, meta))


def test_pipeline_orchestrates_components():
    source = StubSource()
    extractor = StubExtractor()
    sink = StubSink()
    notifier = StubNotifier()

    pipeline = ExtractionPipeline(source=source, extractor=extractor, sink=sink, notifier=notifier)
    artifact = pipeline.run("/tmp/input.txt")

    assert source.fetched == "/tmp/input.txt"
    assert extractor.called is True
    assert sink.saved is not None
    assert artifact["location"] == "mem://artifact"
    assert len(notifier.messages) == 1
    msg, meta = notifier.messages[0]
    assert "Hello" in msg
    assert meta and meta.get("location") == "mem://artifact"
