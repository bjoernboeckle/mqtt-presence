#!/bin/bash

# Variablen anpassen
WIN_SRC="/mnt/c/development/mqtt-presence"
WSL_BUILD_DIR="$HOME/mqtt-presence-build"

echo "Kopiere Projekt von $WIN_SRC nach $WSL_BUILD_DIR ..."
rm -rf "$WSL_BUILD_DIR"
cp -r "$WIN_SRC" "$WSL_BUILD_DIR"

cd "$WSL_BUILD_DIR" || exit 1

echo "Starte dpkg-buildpackage ..."
dpkg-buildpackage -us -uc
BUILD_RESULT=$?

if [ $BUILD_RESULT -eq 0 ]; then
  echo "Build erfolgreich. Kopiere .deb und andere Artefakte zurück nach $WIN_SRC ..."
  cp ../*.deb ../*.changes ../*.tar.* "$WIN_SRC"
else
  echo "Build fehlgeschlagen."
fi
