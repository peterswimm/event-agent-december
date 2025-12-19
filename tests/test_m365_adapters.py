from __future__ import annotations

from typing import Any, Dict, Optional

from knowledge-agent-poc.integrations.m365_adapters import (
    SharePointSource,
    SharePointSink,
    OneDrivePathSource,
    OneDriveSink,
    TeamsNotifier,
)


class FakeConnector:
    def __init__(self) -> None:
        self.downloaded: list[tuple[str, str, Optional[str]]] = []
        self.uploaded: list[tuple[str, str, str, bytes, Optional[str]]] = []
        self.channel_posts: list[str] = []
        self.od_downloads: list[str] = []
        self.od_uploads: list[tuple[str, str, bytes]] = []

    # Mirror M365KnowledgeConnector signatures used by adapters
    def download_file(self, site_id: str, file_path: str, drive_name: Optional[str] = None) -> bytes:
        self.downloaded.append((site_id, file_path, drive_name))
        return b"content"

    def upload_file(self, site_id: str, folder_path: str, filename: str, content: bytes, drive_name: Optional[str] = None) -> Dict[str, Any]:
        self.uploaded.append((site_id, folder_path, filename, content, drive_name))
        return {"webUrl": f"https://contoso.sharepoint.com{folder_path}/{filename}"}

    def get_onedrive_file_by_path(self, file_path: str) -> bytes:
        self.od_downloads.append(file_path)
        return b"od-content"

    def upload_to_onedrive(self, folder_path: str, filename: str, content: bytes) -> Dict[str, Any]:
        self.od_uploads.append((folder_path, filename, content))
        return {"webUrl": f"https://contoso-my.sharepoint.com{folder_path}/{filename}"}

    def post_to_channel(self, team_id: str, channel_id: str, message: str) -> Dict[str, Any]:
        self.channel_posts.append(message)
        return {"id": "msg1"}


def test_sharepoint_source_and_sink_roundtrip():
    connector = FakeConnector()
    source = SharePointSource(connector, site_id="site123", drive_name=None)
    sink = SharePointSink(connector, site_id="site123", folder_path="/Knowledge Artifacts")

    raw = source.fetch("/Shared Documents/file.pdf")
    assert raw == b"content"
    assert connector.downloaded[0] == ("site123", "/Shared Documents/file.pdf", None)

    artifact = {"id": "file", "title": "File", "summary": "ok"}
    location = sink.save(artifact)
    assert location.endswith("/file.json")
    assert connector.uploaded[0][1] == "/Knowledge Artifacts"


def test_teams_notifier_posts_channel_message():
    connector = FakeConnector()
    notifier = TeamsNotifier(connector, team_id="team1", channel_id="chan1")
    notifier.notify("Hello", meta={"location": "https://contoso.sharepoint.com/file.json"})
    assert len(connector.channel_posts) == 1
    assert "Hello" in connector.channel_posts[0]
    assert "file.json" in connector.channel_posts[0]


def test_onedrive_source_and_sink_roundtrip():
    connector = FakeConnector()
    source = OneDrivePathSource(connector)
    sink = OneDriveSink(connector, folder_path="/Documents/Knowledge Artifacts")

    raw = source.fetch("/Documents/file.pdf")
    assert raw == b"od-content"
    assert connector.od_downloads[0] == "/Documents/file.pdf"

    artifact = {"id": "file", "title": "File", "summary": "ok"}
    location = sink.save(artifact)
    assert location.endswith("/file.json")
    assert connector.od_uploads[0][0] == "/Documents/Knowledge Artifacts"
