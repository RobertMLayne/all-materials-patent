"""Report manifest drift, or intentionally refresh reviewed artifact hashes.

This does not approve a change. Inspect its diff, then run the package verifier.
Default operation is read-only; --write is an explicit maintenance action.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Refresh reviewed hashes, then verify separately")
    args = parser.parse_args()
    specification = importlib.util.spec_from_file_location("package_verifier", ROOT / "verify_package.py")
    verifier = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(verifier)
    verifier.check_inventory(ROOT)
    path = ROOT / verifier.MANIFEST
    previous_bytes = path.read_bytes()
    previous = json.loads(previous_bytes)
    updated = dict(previous)
    updated["files"] = [
        {"path": relative, "size_bytes": (ROOT / relative).stat().st_size,
         "sha256": hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()}
        for relative in sorted(verifier.EXPECTED_HASHED)
    ]
    updated["file_count"] = len(updated["files"])
    old_entries = {entry["path"]: entry for entry in previous["files"]}
    new_entries = {entry["path"]: entry for entry in updated["files"]}
    changed = sorted(path for path in old_entries.keys() | new_entries.keys()
                     if old_entries.get(path) != new_entries.get(path))
    manifest_changed = updated != previous
    if args.write and manifest_changed:
        # Exclusive scratch creation and atomic replacement avoid a partial
        # manifest after interruption. Cleanup only the file created here.
        temporary = path.with_name(".manifest-update-" + uuid.uuid4().hex + ".tmp")
        temporary_created = False
        try:
            with temporary.open("x", encoding="utf-8", newline="\n") as stream:
                temporary_created = True
                stream.write(json.dumps(updated, indent=2) + "\n")
            if path.read_bytes() != previous_bytes:
                raise RuntimeError("Manifest changed during refresh; preserve and inspect the other writer's work")
            temporary.replace(path)
        finally:
            if temporary_created:
                temporary.unlink(missing_ok=True)
    print(json.dumps({"changed_artifacts": changed, "manifest_written": args.write and manifest_changed,
                      "verification_required": True}, indent=2))
    return 0 if args.write or not manifest_changed else 1


if __name__ == "__main__":
    raise SystemExit(main())
