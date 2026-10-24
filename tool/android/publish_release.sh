#!/usr/bin/env bash
set -euo pipefail

: "${GITHUB_REPOSITORY:?}"
: "${GITHUB_SHA:?}"
: "${GITHUB_RUN_ID:?}"
: "${GITHUB_RUN_NUMBER:?}"
: "${GITHUB_RUN_ATTEMPT:?}"
: "${GITHUB_SERVER_URL:?}"
: "${GITHUB_REF:?}"
: "${RUNNER_TEMP:?}"

if [[ "$GITHUB_REF" != refs/heads/main ]]; then
  echo 'Only the main branch can publish an APK.' >&2
  exit 1
fi
test -s release/app-release.apk
RELEASE_VERSION="$(sed -n 's/^version: *\([^+ ]*\).*$/\1/p' pubspec.yaml)"
[[ "$RELEASE_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]
[[ "$GITHUB_SHA" =~ ^[0-9a-f]{40}$ ]]
[[ "$GITHUB_RUN_NUMBER" =~ ^[0-9]+$ ]]
[[ "$GITHUB_RUN_ATTEMPT" =~ ^[0-9]+$ ]]
export RELEASE_VERSION

RELEASE_TAG="world-career-v${RELEASE_VERSION}-build.${GITHUB_RUN_NUMBER}.${GITHUB_RUN_ATTEMPT}"
RELEASE_APK=release/Bytecraft-World-Career.apk
cp release/app-release.apk "$RELEASE_APK"

python3 - <<'PY'
import datetime
import hashlib
import json
import os
from pathlib import Path

apk = Path('release/Bytecraft-World-Career.apk')
digest = hashlib.sha256(apk.read_bytes()).hexdigest()
Path(str(apk) + '.sha256').write_text(f'{digest}  {apk.name}\n')
run_url = (f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}"
           f"/actions/runs/{os.environ['GITHUB_RUN_ID']}")
info = {
    'version': os.environ['RELEASE_VERSION'],
    'build_number': int(os.environ['GITHUB_RUN_NUMBER']),
    'attempt': int(os.environ['GITHUB_RUN_ATTEMPT']),
    'commit': os.environ['GITHUB_SHA'],
    'workflow_run': run_url,
    'package_name': 'com.pazzia.bytecraftworld',
    'sha256': digest,
    'published_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
Path('release/build-info.json').write_text(json.dumps(info, indent=2) + '\n')
notes = (
    f"Android APK · версия {info['version']} · сборка {info['build_number']}.\n\n"
    "Проверки контента, Flutter analyze, Flutter tests, подпись, идентификатор "
    "пакета, установка и запуск на Android успешно пройдены.\n\n"
    f"Исходники: {info['commit']}\n\n[Результаты CI]({run_url}).\n\n"
    "Установочный файл: **Bytecraft-World-Career.apk**. "
    "Рядом находятся SHA-256 и build-info.json с точной версией исходников.\n"
)
Path(os.environ['RUNNER_TEMP'], 'world-career-release-notes.md').write_text(notes)
PY

# Keep each attempt separate; never replace an APK from an existing release.
gh release create "$RELEASE_TAG" \
  "$RELEASE_APK" "$RELEASE_APK.sha256" release/build-info.json \
  --repo "$GITHUB_REPOSITORY" --target "$GITHUB_SHA" --draft \
  --title "Bytecraft World + Career ${RELEASE_VERSION} (build ${GITHUB_RUN_NUMBER})" \
  --notes-file "$RUNNER_TEMP/world-career-release-notes.md"

# Verify uploaded bytes while the release is still a draft.
RELEASE_VERIFY_DIR="$(mktemp -d "$RUNNER_TEMP/world-release-verify.XXXXXX")"
gh release download "$RELEASE_TAG" --repo "$GITHUB_REPOSITORY" \
  --pattern 'Bytecraft-World-Career*' --dir "$RELEASE_VERIFY_DIR"
cmp "$RELEASE_APK" "$RELEASE_VERIFY_DIR/Bytecraft-World-Career.apk"
(
  cd "$RELEASE_VERIFY_DIR"
  sha256sum --check Bytecraft-World-Career.apk.sha256
)
gh release edit "$RELEASE_TAG" --repo "$GITHUB_REPOSITORY" --draft=false --latest

RELEASE_URL="$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/releases/tag/$RELEASE_TAG"
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
  {
    echo '## Android APK published'
    echo
    echo "[Download APK]($GITHUB_SERVER_URL/$GITHUB_REPOSITORY/releases/download/$RELEASE_TAG/Bytecraft-World-Career.apk)"
    echo
    echo "[Release and checksums]($RELEASE_URL)"
    echo
    echo "Source commit: $GITHUB_SHA"
  } >> "$GITHUB_STEP_SUMMARY"
fi
echo "Release published: $RELEASE_URL"
