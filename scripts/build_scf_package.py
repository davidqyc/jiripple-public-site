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
ICP_NUMBER = "辽ICP备2024033740号-2"
PUBLIC_SECURITY_NUMBER = "辽公网安备21011202001353号"
PUBLIC_SECURITY_URL = (
    "https://beian.mps.gov.cn/#/query/webSearch?code=21011202001353"
)
PUBLIC_SECURITY_ICON = "/assets/beian.png"
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


def git_tracked_files() -> frozenset[str]:
    output = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", "-z", "HEAD"],
        cwd=ROOT,
    )
    return frozenset(
        name.decode("utf-8") for name in output.split(b"\0") if name
    )


def tracked_source_bytes(source: Path, tracked_files: frozenset[str]) -> bytes:
    relative_path = source.relative_to(ROOT).as_posix()
    if relative_path not in tracked_files:
        raise RuntimeError(
            f"SCF package source is not tracked by the current Git commit: {relative_path}"
        )
    if source.is_symlink():
        raise RuntimeError(f"Symlink is not allowed in SCF package: {relative_path}")
    if not source.is_file():
        raise RuntimeError(f"Tracked SCF package source is missing: {relative_path}")

    committed = subprocess.check_output(
        ["git", "show", f"HEAD:{relative_path}"],
        cwd=ROOT,
    )
    working_tree = source.read_bytes()
    if working_tree != committed:
        raise RuntimeError(
            "SCF package source differs from the current Git commit: "
            f"{relative_path}"
        )
    return committed


def html_route(arcname: str) -> str:
    if arcname == "index.html":
        return "/"
    if arcname.endswith("/index.html"):
        return f"/{arcname[:-len('index.html')]}"
    return f"/{arcname}"


def validate_public_html(
    public_files: tuple[tuple[Path, str], ...],
    tracked_files: frozenset[str],
) -> None:
    arcnames = {arcname for _, arcname in public_files}
    if "assets/beian.png" not in arcnames:
        raise RuntimeError("Public-security icon is missing from the SCF package")

    for source, arcname in public_files:
        if not arcname.endswith(".html"):
            continue
        try:
            html = tracked_source_bytes(source, tracked_files).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise RuntimeError(f"Public HTML is not valid UTF-8: {arcname}") from exc

        required_values = (
            ICP_NUMBER,
            PUBLIC_SECURITY_NUMBER,
            PUBLIC_SECURITY_URL,
            PUBLIC_SECURITY_ICON,
        )
        for value in required_values:
            if value not in html:
                raise RuntimeError(
                    f"Public HTML is missing required filing content {value!r}: {arcname}"
                )

        icon_position = html.index(PUBLIC_SECURITY_ICON)
        security_link_position = html.index(PUBLIC_SECURITY_URL)
        security_text_position = html.index(PUBLIC_SECURITY_NUMBER)
        if icon_position >= min(security_link_position, security_text_position):
            raise RuntimeError(
                "Public-security icon must precede its filing link and text in public HTML: "
                f"{arcname}"
            )


def validate_contract(
    public_files: tuple[tuple[Path, str], ...],
    tracked_files: frozenset[str],
) -> None:
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

    validate_public_html(public_files, tracked_files)

    # Validate every published HTML route plus the explicit non-HTML surfaces.
    runtime.SITE_ROOT = ROOT
    html_routes = tuple(
        html_route(arcname)
        for _, arcname in public_files
        if arcname.endswith(".html")
    )
    non_html_routes = (
        "/xiaoheiniao/context.md",
        "/llms.txt",
        "/robots.txt",
        "/sitemap.xml",
    )
    for request_path in (*html_routes, *non_html_routes):
        if runtime.resolve_request_path(request_path) is None:
            raise RuntimeError(f"SCF runtime would not serve required path: {request_path}")

    expected_404 = (
        "/server.py",
        "/scf_bootstrap",
        "/MANIFEST.sha256",
        "/%73erver.py",
        "/%4dANIFEST.sha256",
        "/%2e%2e/server.py",
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


def iter_public_files(tracked_files: frozenset[str]):
    for name in PUBLIC_ROOT_FILES:
        source = ROOT / name
        tracked_source_bytes(source, tracked_files)
        yield source, name

    for directory in PUBLIC_ROOT_DIRECTORIES:
        prefix = f"{directory}/"
        for relative_path in sorted(
            name for name in tracked_files if name.startswith(prefix)
        ):
            parts = Path(relative_path).parts
            if any(part == ".DS_Store" or part.startswith("._") for part in parts):
                raise RuntimeError(
                    f"OS metadata is not allowed in SCF public package: {relative_path}"
                )
            source = ROOT / relative_path
            tracked_source_bytes(source, tracked_files)
            yield source, relative_path

    for source_name, arcname in (
        ("server.py", "server.py"),
        ("scf_bootstrap", "scf_bootstrap"),
    ):
        source = RUNTIME / source_name
        tracked_source_bytes(source, tracked_files)
        yield source, arcname


def write_member(
    zf: zipfile.ZipFile,
    source: Path,
    arcname: str,
    tracked_files: frozenset[str],
) -> None:
    mode = 0o755 if arcname == "scf_bootstrap" else 0o644
    info = zipfile.ZipInfo(arcname, date_time=FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (stat.S_IFREG | mode) << 16
    zf.writestr(info, tracked_source_bytes(source, tracked_files))


def build() -> Path:
    tracked_files = git_tracked_files()
    public_files = tuple(iter_public_files(tracked_files))
    validate_contract(public_files, tracked_files)
    DIST.mkdir(exist_ok=True)
    for stale in DIST.glob("jiripple-public-site-scf-*.zip"):
        stale.unlink()

    output = DIST / f"jiripple-public-site-scf-{git_short_sha()}.zip"
    with zipfile.ZipFile(output, "w") as zf:
        seen: set[str] = set()
        for source, arcname in public_files:
            if arcname in seen:
                raise RuntimeError(f"Duplicate archive path: {arcname}")
            seen.add(arcname)
            write_member(zf, source, arcname, tracked_files)

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
