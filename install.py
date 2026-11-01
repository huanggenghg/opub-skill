#!/usr/bin/env python3
"""Install the payment skills bundled with the opub skill.

The opub skill ships the official Alipay buyer skills in ``bundled/``.  This
script places them next to the host's other skills, verifies every file against
the signed ``.signature/code-resources.json`` manifest, and reports whether the
``alipay-bot`` CLI is available.

Usage:
    python install.py
    python install.py --skills-dir ~/.workbuddy/skills
    python install.py --install-cli
    python install.py --dry-run
    python install.py --json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

SKILL_NAMES = ("alipay-payment-skill", "alipay-authenticate-wallet")
NPM_PACKAGE = "@alipay/agent-payment@1.0.12"
EXPECTED_INTEGRITY = (
    "sha512-WpJNa5rK6pXaLqKbvfHNI6iG0n0/+dX/ETmtWqH2SWeS2hDnpGbjFiLaZDyZ"
    "HXqPlGNTEzrPWnP4p4Ruy+DOTg=="
)


class InstallError(RuntimeError):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def default_skills_root() -> Path:
    # When this script is installed as <skills_root>/<skill>/install.py, the
    # sibling skills belong in its parent directory.
    parent = repo_root().parent
    if parent.name == "skills":
        return parent
    candidates = (
        Path.home() / ".workbuddy" / "skills",
        Path.home() / ".claude" / "skills",
        Path.home() / ".openclaw" / "workspace" / "skills",
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return candidates[0]


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_skill(skill: Path) -> None:
    """Verify every signed file against the bundled manifest."""
    manifest_path = skill / ".signature" / "code-resources.json"
    if not manifest_path.is_file():
        raise InstallError(f"{skill.name}: missing .signature/code-resources.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise InstallError(f"{skill.name}: empty signature manifest")
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("signed"):
            continue
        relative = entry.get("path")
        expected_hash = entry.get("hash")
        expected_size = entry.get("size")
        if (
            not isinstance(relative, str)
            or not isinstance(expected_hash, str)
            or not isinstance(expected_size, int)
        ):
            raise InstallError(f"{skill.name}: invalid signature manifest entry")
        target = (skill / relative).resolve()
        if skill.resolve() not in target.parents:
            raise InstallError(f"{skill.name}: unsafe manifest path: {relative}")
        if not target.is_file():
            raise InstallError(f"{skill.name}: missing {relative}")
        if target.stat().st_size != expected_size or file_digest(target) != expected_hash:
            raise InstallError(f"{skill.name}: integrity check failed for {relative}")


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_digest(path).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def install_skill(
    source: Path, destination: Path, *, force: bool, dry_run: bool
) -> str:
    verify_skill(source)
    if destination.exists() and tree_digest(source) == tree_digest(destination):
        return "unchanged"
    if destination.exists() and not force:
        return "exists"
    if dry_run:
        return "would_install"
    if destination.exists():
        backup = destination.with_name(
            f"{destination.name}.bak-{datetime.now():%Y%m%d%H%M%S}"
        )
        destination.rename(backup)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    return "installed"


def find_cli() -> str | None:
    return shutil.which("alipay-bot")


def install_cli() -> dict[str, str | None]:
    existing = find_cli()
    if existing:
        return {"status": "found", "path": existing}
    npm = shutil.which("npm")
    if npm is None:
        return {"status": "npm_missing", "path": None}
    try:
        verified = subprocess.run(
            [npm, "view", NPM_PACKAGE, "dist.integrity"],
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {"status": "integrity_check_failed", "path": None}
    if verified.returncode != 0 or verified.stdout.strip() != EXPECTED_INTEGRITY:
        return {"status": "integrity_check_failed", "path": None}
    npx = shutil.which("npx")
    if npx is None:
        return {"status": "npx_missing", "path": None}
    with tempfile.TemporaryDirectory(prefix="opub-payment-cli-") as temporary:
        try:
            subprocess.run(
                [npm, "install", NPM_PACKAGE],
                cwd=temporary,
                check=True,
                timeout=600,
                capture_output=True,
            )
            subprocess.run(
                [npx, NPM_PACKAGE, "install-cli"],
                cwd=temporary,
                check=True,
                timeout=600,
                capture_output=True,
            )
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return {"status": "install_failed", "path": None}
    found = find_cli()
    if found:
        return {"status": "installed", "path": found}
    return {"status": "installed_not_on_path", "path": None}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install payment skills bundled with the opub skill."
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        help="Host skills directory (default: the first known host skills directory).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing skill directory with different contents.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would happen without writing files.",
    )
    parser.add_argument(
        "--install-cli",
        action="store_true",
        help="Install the pinned alipay-bot CLI when it is missing.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a machine-readable summary.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    skills_root = (
        args.skills_dir.expanduser().resolve()
        if args.skills_dir
        else default_skills_root()
    )
    bundled = repo_root() / "bundled"
    summary: dict[str, object] = {
        "skills_root": str(skills_root),
        "skills": {},
        "cli": {"status": "found" if find_cli() else "missing", "path": find_cli()},
    }
    errors: list[str] = []
    for name in SKILL_NAMES:
        source = bundled / name
        if not source.is_dir():
            errors.append(f"missing bundled skill: {name}")
            continue
        try:
            status = install_skill(
                source,
                skills_root / name,
                force=args.force,
                dry_run=args.dry_run,
            )
        except (InstallError, OSError) as exc:
            errors.append(str(exc))
            continue
        summary["skills"][name] = status
    if args.install_cli and not args.dry_run:
        summary["cli"] = install_cli()
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"skills_root={skills_root}")
        for name, status in summary["skills"].items():
            print(f"{name}={status}")
        cli = summary["cli"]
        assert isinstance(cli, dict)
        suffix = f" ({cli['path']})" if cli.get("path") else ""
        print(f"alipay-bot={cli['status']}{suffix}")
        for error in errors:
            print(f"error={error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
