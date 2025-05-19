import sys
import io
from pathlib import Path

import toml

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Pfade
pyproject_file = Path("pyproject.toml")
output_version_file = Path("mqtt_presence/version.py")

def sanitize_version(version: str) -> str:
    """Remove leading 'v' if present (e.g. 'v1.2.3' -> '1.2.3')"""
    return version.lstrip('v')


def update_version(pyproject_path: Path, new_version: str):
    data = toml.load(pyproject_path)

    # Für Poetry ist die Version unter [tool.poetry]
    if "tool" not in data or "poetry" not in data["tool"] or "version" not in data["tool"]["poetry"]:
        print("❌ [tool.poetry] section or version missing in pyproject.toml")
        sys.exit(1)

    data["tool"]["poetry"]["version"] = version_clean
    pyproject_path.write_text(toml.dumps(data), encoding="utf-8")
    print(f"{pyproject_path} updated with version {new_version}.")


def create_version_py(output_file, pyproject_path: Path):
    pyproject_data = toml.load(pyproject_path)
    # version.py schreiben
    version = pyproject_data["tool"]["poetry"]["version"]
    name = pyproject_data["tool"]["poetry"]["name"]
    description = pyproject_data["tool"]["poetry"]["description"]
    repository = pyproject_data["tool"]["poetry"]["repository"]
    documentation = pyproject_data["tool"]["poetry"]["documentation"]
    authors = pyproject_data["tool"]["poetry"]["authors"]

    output_file.write_text(f'VERSION = "{version}"\nNAME = "{name}"\nDESCRIPTION = "{description}"\nREPOSITORY = "{repository}"\nDOCUMENTATION = "{documentation}"\nAUTHORS = "{authors}"\n') 
    print(f"{output_file} for app {name} with version {version} created.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/update_version.py <new_version>")
        sys.exit(1)
    
    version_clean = sanitize_version(sys.argv[1])
    print(f"📦 Updating version to {version_clean}...")


    update_version(pyproject_file, version_clean)           # 1. update toml
    create_version_py(output_version_file, pyproject_file)  # 2. create information from toml
    print("✅ Version updated successfully.")