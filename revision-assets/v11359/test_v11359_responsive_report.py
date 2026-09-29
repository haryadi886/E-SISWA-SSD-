from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
main=(root/'app/src/main/java/id/sch/smpn4dumai/esiswa/MainActivity.java').read_text(encoding='utf-8')
gradle=(root/'app/build.gradle').read_text(encoding='utf-8')
manifest=(root/'app/src/main/AndroidManifest.xml').read_text(encoding='utf-8')
push=(root/'app/src/main/java/id/sch/smpn4dumai/esiswa/PushMessagingService.java').read_text(encoding='utf-8')
checks={
 'version 1.1.3.5.9 code 19': "versionName '1.1.3.5.9'" in gradle and 'versionCode 19' in gradle,
 'package preserved': "applicationId 'id.sch.smpn4dumai.esiswa'" in gradle,
 'sdk preserved': 'compileSdk 36' in gradle and 'targetSdk 36' in gradle,
 'E-TAMU viewport settings': 'setUseWideViewPort(true)' in main and 'setLoadWithOverviewMode(true)' in main and 'setTextZoom(100)' in main,
 'forced 0.88 scale removed': 'MOBILE_PAGE_SCALE' not in main and 'initial-scale=" + scale' not in main and 'setInitialScale(0)' not in main,
 'native JS alert branding': 'onJsAlert' in main and '.setTitle("E-SISWA")' in main,
 'native JS confirm branding': 'onJsConfirm' in main,
 'native JS prompt branding': 'onJsPrompt' in main,
 'direct Google export interception': 'isGoogleDirectExportUri' in main and 'startNativeGoogleExportDownload' in main,
 'docs export recognized': 'host.equals("docs.google.com")' in main and 'path.contains("/export")' in main,
 'drive direct download recognized': 'host.equals("drive.google.com")' in main and '"download".equalsIgnoreCase(export)' in main,
 'native DownloadManager retained': 'DownloadManager.Request' in main and 'enqueueDownload' in main,
 'native print retained': 'PrintManager' in main and '__ESISWA_NATIVE_PRINT_V4_INSTALLED' in main,
 'persistent login retained': 'getPersistentSessionCredential' in main and 'savePersistentSessionCredential' in main and 'esiswa_android_persistent_auth' in main,
 'FCM retained': 'FirebaseMessaging' in main and 'ESISWAAndroidPush' in main and 'extends FirebaseMessagingService' in push,
 'camera retained': 'Manifest.permission.CAMERA' in main and 'android.permission.CAMERA' in manifest and 'applyCameraPopupSafeArea' in main,
 'notification permission retained': 'android.permission.POST_NOTIFICATIONS' in manifest,
 'cleartext disabled': 'android:usesCleartextTraffic="false"' in manifest,
}
bad=[]
for name,ok in checks.items():
    print(('PASS' if ok else 'FAIL')+' | '+name)
    if not ok: bad.append(name)
print(f'SUMMARY: {len(checks)-len(bad)}/{len(checks)} PASS; failures={len(bad)}')
sys.exit(1 if bad else 0)
