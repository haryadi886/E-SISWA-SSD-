#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if command -v gradle >/dev/null 2>&1; then
  gradle clean assembleDebug
elif [[ -x ./gradlew && -f gradle/wrapper/gradle-wrapper.jar ]]; then
  ./gradlew clean assembleDebug
else
  echo "Gradle belum tersedia. Buka project ini di Android Studio atau instal Gradle 8.13 lalu jalankan: gradle clean assembleDebug" >&2
  exit 2
fi
printf '\nAPK: app/build/outputs/apk/debug/app-debug.apk\n'
