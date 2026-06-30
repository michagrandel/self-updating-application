"""Startup update check against the git repository configured in pyproject.toml.

At the start of every console entrypoint the application verifies whether the
configured git repository publishes a newer release (git tag) than the version
that is currently installed. If a newer release exists, the user is asked to
upgrade and the program exits.
"""

from __future__ import annotations

import subprocess

from importlib.metadata import PackageNotFoundError, metadata, version
from rich.console import Console

#: Distribution name as declared in ``pyproject.toml`` (``[project].name``).
DISTRIBUTION_NAME = "self-updating-application"

_stdout = Console()
_stderr = Console(stderr=True)


def _get_repository_url() -> str | None:
    """Return the ``Repository`` URL from the installed package metadata."""
    try:
        package_metadata = metadata(DISTRIBUTION_NAME)
    except PackageNotFoundError:
        return None

    for entry in package_metadata.get_all("Project-URL") or []:
        label, _, url = entry.partition(",")
        if label.strip().lower() == "repository":
            url = url.strip()
            return url or None
    return None


def _get_current_version() -> tuple[int, ...] | None:
    """Return the installed version of this package as a comparable tuple."""
    try:
        return _parse_version(version(DISTRIBUTION_NAME))
    except PackageNotFoundError:
        return None


def _parse_version(tag: str) -> tuple[int, ...] | None:
    """Parse a tag like ``v1.2.3`` into ``(1, 2, 3)``.

    Returns ``None`` if the tag does not look like a numeric version.
    """
    cleaned = tag.strip()
    if cleaned[:1].lower() == "v":
        cleaned = cleaned[1:]

    parts: list[int] = []
    for piece in cleaned.split("."):
        digits = ""
        for char in piece:
            if char.isdigit():
                digits += char
            else:
                break
        if not digits:
            return None
        parts.append(int(digits))

    return tuple(parts) if parts else None


def _is_newer(latest: tuple[int, ...], current: tuple[int, ...]) -> bool:
    """Return ``True`` if ``latest`` is a higher version than ``current``."""
    length = max(len(latest), len(current))
    latest_padded = latest + (0,) * (length - len(latest))
    current_padded = current + (0,) * (length - len(current))
    return latest_padded > current_padded


def _run_git(*args: str) -> subprocess.CompletedProcess[str] | None:
    """Run a git command, returning ``None`` if git is unavailable."""
    try:
        return subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, FileNotFoundError):
        return None


def _remote_branch_exists(url: str, branch: str) -> bool:
    """Return ``True`` if ``branch`` exists on the remote repository."""
    result = _run_git("ls-remote", "--heads", url, branch)
    return bool(result and result.returncode == 0 and result.stdout.strip())


def _remote_release_versions(url: str) -> list[tuple[int, ...]]:
    """Return all release versions (parsed tags) from the remote repository."""
    result = _run_git("ls-remote", "--tags", url)
    if not result or result.returncode != 0:
        return []

    versions: list[tuple[int, ...]] = []
    for line in result.stdout.splitlines():
        _, _, ref = line.partition("\t")
        ref = ref.strip()
        if not ref.startswith("refs/tags/"):
            continue
        tag = ref[len("refs/tags/") :]
        if tag.endswith("^{}"):  # dereferenced annotated tag
            tag = tag[:-3]
        parsed = _parse_version(tag)
        if parsed is not None:
            versions.append(parsed)
    return versions


def check_for_updates() -> None:
    """Check the configured repository for a newer release and exit if found.

    Behaviour:
    * No repository URL configured -> treat as up to date and return.
    * Neither ``main`` nor ``master`` branch exists -> treat as up to date.
    * A release tag newer than the installed version exists -> print an error
      asking the user to upgrade and exit with a non-zero status.
    """
    url = _get_repository_url()
    if not url:
        return

    _stdout.print(f"Checking for updates in [bold cyan]{url}[/bold cyan] ...")

    branch = next(
        (name for name in ("main", "master") if _remote_branch_exists(url, name)),
        None,
    )
    if branch is None:
        return

    versions = _remote_release_versions(url)
    if not versions:
        return

    latest = max(versions, key=lambda parts: parts + (0,) * (4 - len(parts)))
    current = _get_current_version()
    if current is None:
        return

    if _is_newer(latest, current):
        latest_str = ".".join(str(part) for part in latest)
        current_str = ".".join(str(part) for part in current)
        _stderr.print(
            f"[bold red]A newer release is available:[/bold red] "
            f"v{latest_str} (installed: v{current_str})."
        )
        _stderr.print(
            "Please upgrade to the latest version before continuing."
        )
        raise SystemExit(1)
