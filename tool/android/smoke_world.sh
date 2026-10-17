#!/bin/bash
set -euo pipefail
APK="$1"
PKG=com.pazzia.bytecraftworld
adb root > /dev/null 2>&1 || true
sleep 2
adb install -r "$APK" > smoke-world.txt 2>&1
adb logcat -c
adb shell am start -W -n "$PKG/.MainActivity" >> smoke-world.txt 2>&1
sleep 55
PID=$(adb shell pidof "$PKG" | tr -d '\r')
echo "--- pid: $PID" >> smoke-world.txt
adb shell uiautomator dump /sdcard/world-ui.xml >> smoke-world.txt 2>&1
adb pull /sdcard/world-ui.xml world-ui.xml >> smoke-world.txt 2>&1
adb shell screencap -p /sdcard/world-screen.png
adb pull /sdcard/world-screen.png world-screen.png > /dev/null 2>&1
adb logcat -d > world-logcat.txt
if [ -n "$PID" ]; then
  adb logcat -d --pid="$PID" > world-app-log.txt
fi
# On a fresh install onboarding may be the first screen. Either the branded
# title or existing onboarding copy proves the Flutter app started.
if grep -qE 'Bytecraft World|Bytecraft|Какой у тебя опыт|Начать|Выбери' world-ui.xml; then
  echo "started=true" >> smoke-world.txt
else
  echo "started=false" >> smoke-world.txt
  tail -n 200 world-logcat.txt >> smoke-world.txt
  exit 1
fi
