#!/usr/bin/env python3
"""Serve the JiRiPPLE static site in Tencent SCF web-function runtime."""

from __future__ import annotations

import mimetypes
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

SITE_ROOT = Path(__file__).resolve().parent
HOST = "0.0.0.0"
DEFAULT_PORT = 9000

# Deliberately narrow public surface. Keep this in sync with scripts/build_scf_package.py.
PUBLIC_ROOT_FILES = frozenset({
    "index.html",
    "llms.txt",
    "robots.txt",
    "sitemap.xml",
})
PUBLIC_ROOT_DIRECTORIES = frozenset({
    "assets",
    "reliablereader",
    "xiaoheiniao",
})

mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("text/markdown", ".md")


def is_public_relative_path(relative_path: str) -> bool:
    parts = relative_path.split("/")
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return False
    if relative_path in PUBLIC_ROOT_FILES:
        return True
    return parts[0] in PUBLIC_ROOT_DIRECTORIES


def resolve_request_path(raw_path: str) -> Path | None:
    request_path = unquote(urlsplit(raw_path).path)
    if not request_path.startswith("/") or "\x00" in request_path or "\\" in request_path:
        return None

    relative_path = request_path.lstrip("/")
    if not relative_path or request_path.endswith("/"):
        relative_path = f"{relative_path}index.html"
    if not is_public_relative_path(relative_path):
        return None

    try:
        candidate = (SITE_ROOT / relative_path).resolve()
        resolved_relative_path = candidate.relative_to(SITE_ROOT).as_posix()
    except (OSError, RuntimeError, ValueError):
        return None

    if not is_public_relative_path(resolved_relative_path):
        return None

    try:
        return candidate if candidate.is_file() else None
    except OSError:
        return None


class StaticSiteHandler(BaseHTTPRequestHandler):
    server_version = "JiRippleStaticSite/1.1"

    def version_string(self) -> str:
        return self.server_version

    def do_GET(self) -> None:  # noqa: N802
        self._serve(include_body=True)

    def do_HEAD(self) -> None:  # noqa: N802
        self._serve(include_body=False)

    def _serve(self, *, include_body: bool) -> None:
        file_path = resolve_request_path(self.path)
        if file_path is None:
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        try:
            payload = file_path.read_bytes()
        except OSError:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        content_type, _ = mimetypes.guess_type(file_path.name)
        if content_type and content_type.startswith("text/"):
            content_type = f"{content_type}; charset=utf-8"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if include_body:
            self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}", flush=True)


def main() -> None:
    port = int(os.environ.get("PORT", str(DEFAULT_PORT)))
    server = ThreadingHTTPServer((HOST, port), StaticSiteHandler)
    print(f"JiRiPPLE static site listening on {HOST}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
