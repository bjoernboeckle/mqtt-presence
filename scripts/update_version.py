import sys
import io
from pathlib import Path

import toml

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def sanitize_version(version: str) -> str:
    """Remove leading 'v' if present (e.g. 'v1.2.3' -> '1.2.3')"""
    return version.lstrip('v')

def update_version(pyproject_path: Path, new_version: str):
    version_clean = sanitize_version(new_version)
    print(f"📦 Updating version in {pyproject_path} to {version_clean}")

    data = toml.load(pyproject_path)

    if "project" not in data or "version" not in data["project"]:
        print("❌ [project] section or version missing in pyproject.toml")
        sys.exit(1)

    data["project"]["version"] = version_clean
    pyproject_path.write_text(toml.dumps(data), encoding="utf-8")
    print("✅ Version updated successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/update_version.py <new_version>")
        sys.exit(1)

    ver = sys.argv[1]
    update_version(Path("pyproject.toml"), ver)
