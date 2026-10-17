#!/bin/bash
# Installs and launches the APK in a running emulator, then saves what is
# on the screen (ui.xml, screen.png) and the log (logcat.txt).
APK="$1"
adb install -r "$APK" > smoke.txt 2>&1
adb logcat -c
adb shell am start -W -n com.pazzia.bytecraft/.MainActivity >> smoke.txt 2>&1
sleep 60
echo "--- pid: $(adb shell pidof com.pazzia.bytecraft)" >> smoke.txt
adb shell uiautomator dump /sdcard/ui.xml >> smoke.txt 2>&1
adb pull /sdcard/ui.xml ui.xml >> smoke.txt 2>&1
adb shell screencap -p /sdcard/screen.png
adb pull /sdcard/screen.png screen.png > /dev/null 2>&1
adb logcat -d > logcat.txt
true
