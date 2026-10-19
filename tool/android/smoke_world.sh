#!/bin/bash
set -euo pipefail
APK="$1"
PKG=com.pazzia.bytecraftworld
adb root > /dev/null 2>&1 || true
sleep 2
adb install -r "$APK" > smoke-world.txt 2>&1
adb logcat -c
adb shell am start -W -n "$PKG/.MainActivity" >> smoke-world.txt 2>&1
# Pyodide also warms in the background; give Flutter enough time on CI.
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
# Prove that this fork starts on the NEW game hub, not on the legacy
# Bytecraft onboarding/home screen.
grep -q 'Bytecraft World' world-ui.xml
grep -q 'Твой маршрут' world-ui.xml
grep -q 'Сейчас: Восстанови API' world-ui.xml
echo "started=true" >> smoke-world.txt
