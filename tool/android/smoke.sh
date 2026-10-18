#!/bin/bash
# Installs and launches the APK in a running emulator, then saves what is
# on the screen (ui.xml, screen.png), the app's own log (app-log.txt) and,
# if it is stuck, stack traces of its threads (stacks.txt).
APK="$1"
PKG=com.pazzia.bytecraft
adb root > /dev/null 2>&1; sleep 3
# Control: an older release that is known to start (CONTROL_APK, optional).
if [ -n "$CONTROL_APK" ] && [ -f "$CONTROL_APK" ]; then
  adb install -r "$CONTROL_APK" > control.txt 2>&1
  adb shell am start -W -n $PKG/.MainActivity >> control.txt 2>&1
  sleep 45
  adb shell uiautomator dump /sdcard/ui.xml >> control.txt 2>&1
  adb pull /sdcard/ui.xml control-ui.xml >> control.txt 2>&1
  echo "--- control texts:" >> control.txt
  grep -o 'text="[^"]*"' control-ui.xml | sed 's/text="//; s/"$//' | grep -v '^$' | head -20 >> control.txt
  adb uninstall $PKG >> control.txt 2>&1
fi
adb install -r "$APK" > smoke.txt 2>&1
adb logcat -c
adb shell am start -W -n $PKG/.MainActivity >> smoke.txt 2>&1
sleep 60
PID=$(adb shell pidof $PKG | tr -d '\r')
echo "--- pid: $PID" >> smoke.txt
adb shell uiautomator dump /sdcard/ui.xml >> smoke.txt 2>&1
adb pull /sdcard/ui.xml ui.xml >> smoke.txt 2>&1
adb shell screencap -p /sdcard/screen.png
adb pull /sdcard/screen.png screen.png > /dev/null 2>&1
adb logcat -d > logcat.txt
if [ -n "$PID" ]; then
  adb logcat -d --pid="$PID" > app-log.txt
  # Native stacks of every thread (the Flutter UI/raster threads included).
  adb shell debuggerd -b "$PID" > stacks.txt 2>&1
  # Java stacks.
  adb shell kill -3 "$PID"; sleep 3
  adb shell 'ls -t /data/anr/ | head -1 | xargs -I{} cat /data/anr/{}' > java-stacks.txt 2>&1
fi
grep -iE "flutter|bytecraft|$PID" logcat.txt | grep -v "nativeloader" | tail -200 > app-related.txt
true
