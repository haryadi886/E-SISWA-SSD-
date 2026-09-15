@echo off
where gradle >nul 2>nul
if %errorlevel%==0 (
  gradle clean assembleDebug
  goto :done
)
if exist gradle\wrapper\gradle-wrapper.jar if exist gradlew.bat (
  call gradlew.bat clean assembleDebug
  goto :done
)
echo Gradle belum tersedia. Buka project ini di Android Studio atau instal Gradle 8.13.
exit /b 2
:done
echo APK: app\build\outputs\apk\debug\app-debug.apk
