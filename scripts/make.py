import sys
import io
import re
import shutil
import toml
import subprocess
import sys
import hashlib

from pathlib import Path
from typing import Optional

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


available_commands = ["clean", "pylint", "pytest","build", "build-exe", "installer", "winget", "chocolatey", "all"]


# toml file
pyproject_file = Path("pyproject.toml")

#version.py
output_version_file = Path("mqtt_presence/version.py")

# exe spec file
exe_spec_file = Path("mqtt-presence.spec")


# inno setup
inno_iss_file = Path("installer/inno/mqtt-presence-setup.iss")


# chocolatey
chocolatey_nuspec = Path("installer/chocolatey/mqtt-presence.nuspec")
chocolatey_install = Path("installer/chocolatey/tools/chocolateyinstall.ps1")


# winget manifest
winget_installer = Path("installer/winget/manifest/BjoernBoeckle.mqtt-presence.installer.yaml")
winget_locale = Path("installer/winget/manifest/BjoernBoeckle.mqtt-presence.locale.en-US.yaml")
winget_main = Path("installer/winget/manifest/BjoernBoeckle.mqtt-presence.yaml")




def sanitize_version(version: str) -> str:
    """Remove leading 'v' if present (e.g. 'v1.2.3' -> '1.2.3')"""
    return version.lstrip('v')


def update_toml_version(pyproject_path: Path, new_version: str):
    data = toml.load(pyproject_path)

    # Für Poetry ist die Version unter [tool.poetry]
    if "tool" not in data or "poetry" not in data["tool"] or "version" not in data["tool"]["poetry"]:
        print("❌ [tool.poetry] section or version missing in pyproject.toml")
        sys.exit(1)

    data["tool"]["poetry"]["version"] = new_version
    pyproject_path.write_text(toml.dumps(data), encoding="utf-8")
    print(f"✏️  {pyproject_path} updated with version {new_version}.")



def get_version_from_toml(pyproject_path: Path):
    data = toml.load(pyproject_path)
    return data["tool"]["poetry"]["version"]    


def get_description_from_toml(pyproject_path: Path):
    data = toml.load(pyproject_path)
    return data["tool"]["poetry"]["description"]


def create_version_py(output_file, pyproject_path: Path):
    """
    Creates version file from pyproject.toml.
    :param output_file: Path to the output file (e.g. mqtt_presence/version.py)
    :param pyproject_path: Path to the pyproject.toml file
    :return: None
    """
    pyproject_data = toml.load(pyproject_path)
    # write version.py
    version = pyproject_data["tool"]["poetry"]["version"]
    name = pyproject_data["tool"]["poetry"]["name"]
    description = pyproject_data["tool"]["poetry"]["description"]
    repository = pyproject_data["tool"]["poetry"]["repository"]
    documentation = pyproject_data["tool"]["poetry"]["documentation"]
    authors = pyproject_data["tool"]["poetry"]["authors"]

    output_file.write_text(f'VERSION = "{version}"\nNAME = "{name}"\nDESCRIPTION = "{description}"\nREPOSITORY = "{repository}"\nDOCUMENTATION = "{documentation}"\nAUTHORS = "{authors}"\n')
    print(f"✏️  Created {output_file} for '{name}' with version {version}.")



def calculate_sha256(file_path: str) -> str:
    """Berechnet die SHA256-Checksumme der angegebenen Datei."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)
    return sha256.hexdigest()


def replace_url_version(content: str, version: str) -> str:
    """
    Ersetzt die Version in einer GitHub-URL-Zeile wie:
    $url = 'https://github.com/.../v0.2.8/mqtt-presence-v0.2.8-setup.exe'
    durch die übergebene Version.
    """
    pattern = r"(https://github\.com/.+?/releases/download/)v[\d\.]+/(mqtt-presence-v)[\d\.]+(-setup\.exe)"
    replacement = fr"\g<1>v{version}/\g<2>{version}\g<3>"
    return re.sub(pattern, replacement, content)



def replace_checksum(content: str, checksum: Optional[str] = None) -> str:
    """
    Ersetzt die Checksumme in einer Zeile wie:
    $checksum = '...'
    durch den übergebenen Wert.
    """
    pattern = r"(\$checksum\s*=\s*')[^']*(')"
    replacement = fr"\g<1>{checksum}\g<2>"
    return re.sub(pattern, replacement, content)


def replace_package_version(content: str, new_version: str) -> str:
    pattern = r"(PackageVersion:\s*)[\d\.]+"

    def repl(m):
        return m.group(1) + new_version

    return re.sub(pattern, repl, content)


def replace_installer_info(content: str, version: str, sha256: Optional[str]) -> str:
    url_pattern = (
        r"(InstallerUrl:\s*https://github\.com/bjoernboeckle/mqtt-presence/releases/download/)"
        r"v[\d\.]+/(mqtt-presence-v)[\d\.]+(-setup\.exe)"
    )
    def url_repl(m):
        return f"{m.group(1)}v{version}/{m.group(2)}{version}{m.group(3)}"
    content = re.sub(url_pattern, url_repl, content)

    sha_pattern = r"(InstallerSha256:\s*)[A-Fa-f0-9]{64}"
    def sha_repl(m):
        return m.group(1) + sha256
    content = re.sub(sha_pattern, sha_repl, content)

    return content


def update_version_and_checksum(file_path: Path, version: str, checksum: Optional[str] = None, desc: Optional[str] = None) -> None:
    """
    Ersetzt __VERSION__ und __CHECKSUM__ in der Datei durch die übergebenen Werte.

    :param file_path: Pfad zur Datei (z. B. chocolateyinstall.ps1)
    :param version: Neue Versionsnummer, z. B. '0.2.7'
    :param checksum: Neuer SHA256-Hash-Wert als Hex-String
    :param desc: New description
    """

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    if file_path==exe_spec_file:
        content = re.sub(r"name=\s*'[^']+'", f"name='mqtt-presence-v{version}'", content)
    elif file_path==inno_iss_file:
        content = re.sub(r'#define MyAppVersion\s+"[^"]+"', f'#define MyAppVersion "{version}"', content)
        content = re.sub(r'#define MyAppExeName\s+"[^"]+"', f'#define MyAppExeName "mqtt-presence-v{version}.exe"', content)
    elif file_path==chocolatey_nuspec:
        content = re.sub(r'<version>[^<]+</version>', f'<version>{version}</version>', content)
        content = re.sub(r'<summary>[^<]+</summary>', f'<summary>{desc}</summary>', content)
        content = re.sub(r'<description>[^<]+</description>', f'<description>{desc}</description>', content)
    elif file_path==chocolatey_install:
        content = replace_url_version(content, version)   # URL in chocolateyinstall.ps1 ersetzen
        content = replace_checksum(content, checksum)     # Checksumme in chocolateyinstall.ps1 ersetzen
    elif file_path==winget_installer:
        content = replace_package_version(content, version)   # replace package version
        content = replace_installer_info(content, version, checksum)         # Checksumme in chocolateyinstall.ps1 ersetzen
    elif file_path==winget_locale:
        content = replace_package_version(content, version)   # replace package version
        content = re.sub(r'ShortDescription:\s+.*', f'ShortDescription: "{desc}"', content)
    elif file_path==winget_main:
        content = replace_package_version(content, version)   # replace package version

    # Datei überschreiben
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"✏️  {file_path} updated with version {version} {'and checksum ' + checksum if checksum is not None else ''}.")



def run_command(command: str):
    """Führt einen Shell-Befehl aus und gibt Fehler aus, falls einer auftritt."""
    print(f"🚀  Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌  Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)




def clean():
    print(f"🧹  Clean")
    path = Path("dist")
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
    path = Path("build")
    if path.exists() and path.is_dir():
        shutil.rmtree(path)        


def update_version(new_version: str):
    print(f"⬆️  Updating version to {new_version}...")
    update_toml_version(pyproject_file, new_version)
    create_version_py(output_version_file, pyproject_file)
    update_version_and_checksum(exe_spec_file, new_version)



def execute_pylint():
    print(f"🧠   Running pylint")
    run_command("poetry run pylint mqtt_presence")


def execute_pytest():
    print(f"🧪  Running pytest")
    run_command("poetry run pytest tests")



def build_packages():
    print("🐍  Building packages")
    run_command("poetry build")


def build_exe(version):
    print("⚙️  Building exe")
    update_version_and_checksum(exe_spec_file, version)    
    run_command("poetry run python -m PyInstaller mqtt-presence.spec")


def build_inno_setup(version):
    print("💿  Building Inno setup...")
    update_version_and_checksum(inno_iss_file, version)
    run_command(r'iscc.exe ./installer/inno/mqtt-presence-setup.iss')


def prepare_chocolatey(version, description):
    print("📦  Prepeare chocolatey")
    checksum = calculate_sha256("dist/mqtt-presence-v" + version + "-setup.exe")
    update_version_and_checksum(chocolatey_nuspec, version, desc=description)
    update_version_and_checksum(chocolatey_install, version, checksum)
    run_command("choco pack installer/chocolatey/mqtt-presence.nuspec")
    nuget_file = f"mqtt-presence.{version}.nupkg"
    shutil.move(nuget_file, f"./dist/{nuget_file}")


def prepare_winget(version, description):
    print("🪟  Building winget...")
    checksum = calculate_sha256("dist/mqtt-presence-v" + version + "-setup.exe")
    update_version_and_checksum(winget_installer, version, checksum)
    update_version_and_checksum(winget_locale, version, desc=description)
    update_version_and_checksum(winget_main, version)


def print_usage():
    print(f"❌  Invalid command - Usage: python make.py [ {' | '.join(available_commands)} | set-version <new_version> ]")    


def handle_set_version(new_version):
    version_clean = sanitize_version(new_version)
    update_version(version_clean)


def handle_make():
    run_clean =  command == "clean" or command == "all"
    run_pylint = command == "pylint" or command == "all"
    run_pytest = command == "pytest" or command == "all"
    run_build = command == "build" or command == "build-exe" or command == "installer" or command == "all"
    run_build_exe = command == "build-exe" or command == "installer" or command == "all"
    run_installer = command == "installer" or command == "all"
    run_winget = command == "winget" or command == "all"
    run_chocolatey = command == "chocolatey" or command == "all"
    

    version = get_version_from_toml(pyproject_file)
    toml_description = get_description_from_toml(pyproject_file)

    # Always ensure latest version infos
    create_version_py(output_version_file, pyproject_file)

    if run_clean: clean()
    if run_pylint: execute_pylint()
    if run_pytest: execute_pytest()
    if run_build: build_packages()
    if run_build_exe: build_exe(version)
    if run_installer: build_inno_setup(version)
    if run_winget: prepare_winget(version, toml_description)
    if run_chocolatey: prepare_chocolatey(version, toml_description)




if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]


    if command == "set-version":
        if len(sys.argv) != 3:
            print_usage()
            sys.exit(1)
        else:
            print("=========================================================================")
            print(f"Set Version {sys.argv[2]}")
            handle_set_version(sys.argv[2])
    else:       
        if len(sys.argv) != 2:
            print_usage()
            sys.exit(1)
        else:
            if command in available_commands:
                print("=========================================================================")
                print(f"Start Make '{command}'")
                handle_make()
            else:
                print_usage()
                sys.exit(1)                
 
    print("=========================================================================")
    print("✅  Make successfully completed.")
