#!/bin/bash
set -euo pipefail

APK="$1"
PKG=com.pazzia.bytecraftcareer

adb root >/dev/null 2>&1 || true
sleep 3
adb install -r "$APK" > smoke.txt 2>&1
adb logcat -c
adb shell am start -W -n "$PKG/.MainActivity" >> smoke.txt 2>&1
sleep 35
PID="$(adb shell pidof "$PKG" | tr -d '\r')"
echo "--- pid: $PID" >> smoke.txt

adb shell uiautomator dump /sdcard/ui.xml >> smoke.txt 2>&1
adb pull /sdcard/ui.xml ui.xml >> smoke.txt 2>&1
adb shell screencap -p /sdcard/screen.png
adb pull /sdcard/screen.png screen.png >/dev/null 2>&1
adb logcat -d > logcat.txt

if [ -n "$PID" ]; then
  adb logcat -d --pid="$PID" > app-log.txt
fi

if ! adb shell pm path "$PKG" | grep -q '^package:'; then
  echo "Package $PKG is not installed" >&2
  exit 1
fi

if [ -z "$PID" ]; then
  echo "Package $PKG is installed but not running" >&2
  exit 1
fi

if grep -qE 'Bytecraft Career|Главная|Начать|Код за пару минут|Выбери' ui.xml; then
  echo 'started=true' >> smoke.txt
else
  echo 'Application started, but expected Bytecraft UI text was not found' >&2
  exit 1
fi
