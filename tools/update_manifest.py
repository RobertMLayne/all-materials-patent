"""Report manifest drift, or intentionally refresh reviewed artifact hashes.

This does not approve a change. Inspect its diff, then run the package verifier.
Default operation is read-only; --write is an explicit maintenance action.

An exclusively created generated_reports/manifest-update.lock serializes
cooperating --write invocations for the complete read/hash/publish transaction.
An interrupted process may leave its lock: inspect it manually, never steal it
based on age or a process identifier. External editors do not honor this lock;
the byte-drift check detects changes observed before replacement, but it is not
an atomic compare-and-swap against those editors.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager, nullcontext
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import os
import sys
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def manifest_write_lock():
    """Own an exclusive lock marker; only its successful creator removes it."""
    directory = ROOT / "generated_reports"
    if directory.is_symlink() or directory.is_junction() or not directory.resolve().is_relative_to(ROOT.resolve()):
        raise RuntimeError("Manifest lock directory must be an ordinary directory inside the package")
    directory.mkdir(exist_ok=True)
    lock = directory / "manifest-update.lock"
    try:
        stream = lock.open("x", encoding="utf-8", newline="\n")
    except FileExistsError as error:
        raise RuntimeError("Manifest update lock already exists; inspect generated_reports/manifest-update.lock manually") from error
    try:
        with stream:
            json.dump({"pid": os.getpid(), "created_utc": datetime.now(timezone.utc).isoformat(),
                       "policy": "No stale-lock stealing; manual inspection required after interruption."}, stream)
            stream.write("\n")
            stream.flush()
            yield
    finally:
        # The lock belongs to this process because exclusive creation succeeded.
        # Keep it until manifest publication and temporary-file cleanup finish.
        lock.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Refresh reviewed hashes, then verify separately")
    args = parser.parse_args()
    specification = importlib.util.spec_from_file_location("package_verifier", ROOT / "verify_package.py")
    verifier = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(verifier)
    with manifest_write_lock() if args.write else nullcontext():
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
            temporary = ROOT / "generated_reports" / (".manifest-update-" + uuid.uuid4().hex + ".tmp")
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
