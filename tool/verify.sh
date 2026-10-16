#!/usr/bin/env bash
# One-shot setup + verification:
#   1. generates android/ios platform folders if missing (flutter create
#      never overwrites existing lib/, test/, pubspec.yaml, README.md)
#   2. resolves packages
#   3. re-verifies course content with real Python (if python3 exists)
#   4. flutter analyze + flutter test
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d android ] || [ ! -d ios ]; then
  flutter create --platforms=android,ios --project-name bytecraft --org com.pazzia .
fi

flutter pub get

if command -v python3 >/dev/null 2>&1; then
  tmp="$(mktemp -d)"
  python3 tool/content/generate_python_course.py "$tmp"
  diff -r "$tmp" assets/content/python/modules && echo "Content: OK (matches generator)"
  rm -rf "$tmp"
fi

flutter analyze
flutter test
