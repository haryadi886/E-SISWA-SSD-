from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
main=(root/'app/src/main/java/id/sch/smpn4dumai/esiswa/MainActivity.java').read_text(encoding='utf-8')
gradle=(root/'app/build.gradle').read_text(encoding='utf-8')
manifest=(root/'app/src/main/AndroidManifest.xml').read_text(encoding='utf-8')
layout=(root/'app/src/main/res/layout/activity_main.xml').read_text(encoding='utf-8')
service=(root/'app/src/main/java/id/sch/smpn4dumai/esiswa/PushMessagingService.java').read_text(encoding='utf-8')
checks={
 'version 1.1.3.5.9 code 19': "versionName '1.1.3.5.9'" in gradle and 'versionCode 19' in gradle,
 'package preserved': "applicationId 'id.sch.smpn4dumai.esiswa'" in gradle,
 'sdk 36 preserved': 'compileSdk 36' in gradle and 'targetSdk 36' in gradle,
 'ETAMU wide viewport': 'setUseWideViewPort(true)' in main and 'setLoadWithOverviewMode(true)' in main,
 'ETAMU text/native scale': 'setTextZoom(96)' in main and 'setInitialScale(0)' in main,
 'old 0.88 injection removed': 'MOBILE_PAGE_SCALE' not in main and 'enforceResponsiveViewport' not in main and 'initial-scale=" + scale' not in main,
 'Apps Script frame normalization': 'normalizeAppsScriptOuterFrame' in main and "querySelectorAll('iframe')" in main,
 'frame fill 100 percent': "setProperty('width','100%','important')" in main and "setProperty('height','100%','important')" in main,
 'delayed normalization': 'postDelayed(() -> normalizeAppsScriptOuterFrame(view, url), 250)' in main and 'postDelayed(() -> normalizeAppsScriptOuterFrame(view, url), 900)' in main,
 'root fits system windows': 'android:fitsSystemWindows="true"' in layout,
 'decor fits system windows': 'setDecorFitsSystemWindows(true)' in main,
 'nav contrast handling': 'setNavigationBarContrastEnforced(false)' in main,
 'keyboard adjust resize': 'android:windowSoftInputMode="adjustResize"' in manifest,
 'orientation/screen resize preserved': 'orientation|screenLayout|screenSize|smallestScreenSize|uiMode' in manifest,
 'camera popup safe area retained': 'applyCameraPopupSafeArea' in main and '--esiswa-native-nav-bottom' in main,
 'persistent login native retained': 'esiswa_android_persistent_auth' in main and 'getPersistentSessionCredential()' in main and 'savePersistentSessionCredential(String refreshToken, String expiresAt)' in main and '.commit()' in main,
 'FCM retained': 'FirebaseMessaging' in main and 'ESISWAAndroidPush' in main and 'extends FirebaseMessagingService' in service,
 'native print retained': 'PrintManager' in main and '__ESISWA_NATIVE_PRINT_V4_INSTALLED' in main,
 'native download retained': 'DownloadManager.Request' in main and 'handleBlobDownload' in main,
 'security cleartext disabled': 'android:usesCleartextTraffic="false"' in manifest,
 'security backup disabled': 'android:allowBackup="false"' in manifest,
 'trusted origin checks retained': 'isTrustedWebOrigin' in main and 'isTrustedCameraOrigin' in main,
 'R7 deployment preserved': 'AKfycbwkTSTL8b7A1DsRA-t79v1dheMq0BSQ0PYq_DtSd6dAlaSHAOEeGFSBaPZ7_6Bf1h3jAg' in main,
}
bad=[]
for k,v in checks.items():
    print(('PASS' if v else 'FAIL')+' | '+k)
    if not v: bad.append(k)
print(f'SUMMARY: {len(checks)-len(bad)}/{len(checks)} PASS; failures={len(bad)}')
sys.exit(1 if bad else 0)
