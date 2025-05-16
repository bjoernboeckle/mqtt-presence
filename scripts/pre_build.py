# scripts/pre_build.py

import toml
from pathlib import Path

# Pfade
pyproject_file = Path("pyproject.toml")
output_file = Path("mqtt_presence/version.py")

# Version aus pyproject.toml lesen
pyproject_data = toml.load(pyproject_file)
version = pyproject_data["project"]["version"]

# version.py schreiben
output_file.write_text(f'__version__ = "{version}"\n')

print(f"✅ Created {output_file} with version {version}")
