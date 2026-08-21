#!/usr/bin/env python3
"""Build the deployable Tencent SCF ZIP from the canonical public-site repo."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RUNTIME = ROOT / "scf"

PUBLIC_ROOT_FILES = (
    "index.html",
    "llms.txt",
    "robots.txt",
    "sitemap.xml",
)
PUBLIC_ROOT_DIRECTORIES = (
    "assets",
    "reliablereader",
    "xiaoheiniao",
)
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)


def git_short_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short=8", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def load_runtime_module():
    path = RUNTIME / "server.py"
    spec = importlib.util.spec_from_file_location("jiripple_scf_server", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load scf/server.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_contract() -> None:
    runtime = load_runtime_module()
    if set(runtime.PUBLIC_ROOT_FILES) != set(PUBLIC_ROOT_FILES):
        raise RuntimeError("SCF server root-file allowlist is out of sync with package builder")
    if set(runtime.PUBLIC_ROOT_DIRECTORIES) != set(PUBLIC_ROOT_DIRECTORIES):
        raise RuntimeError("SCF server directory allowlist is out of sync with package builder")

    for name in PUBLIC_ROOT_FILES:
        if not (ROOT / name).is_file():
            raise RuntimeError(f"Required public file is missing: {name}")

    for required in ("reliablereader", "xiaoheiniao"):
        if not (ROOT / required / "index.html").is_file():
            raise RuntimeError(f"Required public entry is missing: {required}/index.html")

    for runtime_file in ("server.py", "scf_bootstrap"):
        if not (RUNTIME / runtime_file).is_file():
            raise RuntimeError(f"Required SCF runtime file is missing: scf/{runtime_file}")

    # Validate the exact production routing contract against the current source tree.
    runtime.SITE_ROOT = ROOT
    expected_200 = (
        "/",
        "/xiaoheiniao/",
        "/xiaoheiniao/context.md",
        "/reliablereader/",
        "/reliablereader/privacy/",
        "/llms.txt",
        "/robots.txt",
        "/sitemap.xml",
    )
    for request_path in expected_200:
        if runtime.resolve_request_path(request_path) is None:
            raise RuntimeError(f"SCF runtime would not serve required path: {request_path}")

    expected_404 = (
        "/AGENTS.md",
        "/README.md",
        "/ops/",
        "/scf/server.py",
        "/scripts/build_scf_package.py",
        "/../README.md",
    )
    for request_path in expected_404:
        if runtime.resolve_request_path(request_path) is not None:
            raise RuntimeError(f"SCF runtime would expose non-public path: {request_path}")


def iter_public_files():
    for name in PUBLIC_ROOT_FILES:
        yield ROOT / name, name

    for directory in PUBLIC_ROOT_DIRECTORIES:
        source_root = ROOT / directory
        if not source_root.exists():
            continue
        for path in sorted(source_root.rglob("*")):
            if path.is_symlink():
                raise RuntimeError(f"Symlink is not allowed in SCF public package: {path}")
            if path.is_file():
                yield path, path.relative_to(ROOT).as_posix()

    yield RUNTIME / "server.py", "server.py"
    yield RUNTIME / "scf_bootstrap", "scf_bootstrap"


def write_member(zf: zipfile.ZipFile, source: Path, arcname: str) -> None:
    mode = 0o755 if arcname == "scf_bootstrap" else 0o644
    info = zipfile.ZipInfo(arcname, date_time=FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (stat.S_IFREG | mode) << 16
    zf.writestr(info, source.read_bytes())


def build() -> Path:
    validate_contract()
    DIST.mkdir(exist_ok=True)
    for stale in DIST.glob("jiripple-public-site-scf-*.zip"):
        stale.unlink()

    output = DIST / f"jiripple-public-site-scf-{git_short_sha()}.zip"
    with zipfile.ZipFile(output, "w") as zf:
        seen: set[str] = set()
        for source, arcname in iter_public_files():
            if arcname in seen:
                raise RuntimeError(f"Duplicate archive path: {arcname}")
            seen.add(arcname)
            write_member(zf, source, arcname)

    with zipfile.ZipFile(output) as zf:
        names = set(zf.namelist())
        required_entries = {
            "server.py",
            "scf_bootstrap",
            "index.html",
            "xiaoheiniao/index.html",
            "xiaoheiniao/context.md",
            "reliablereader/index.html",
            "reliablereader/privacy/index.html",
            "llms.txt",
            "robots.txt",
            "sitemap.xml",
        }
        missing = sorted(required_entries - names)
        if missing:
            raise RuntimeError(f"SCF ZIP is missing required entries: {missing}")

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    manifest = {
        "zip": output.name,
        "sha256": digest,
        "bytes": output.stat().st_size,
        "entries": len(names),
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    try:
        build()
    except Exception as exc:
        print(f"SCF package build failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
