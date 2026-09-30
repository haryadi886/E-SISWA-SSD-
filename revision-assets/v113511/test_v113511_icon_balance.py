from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
g=(root/'app/build.gradle').read_text(encoding='utf-8')
icon=(root/'app/src/main/res/drawable/ic_launcher_foreground.xml').read_text(encoding='utf-8')
push=(root/'app/src/main/java/id/sch/smpn4dumai/esiswa/PushMessagingService.java').read_text(encoding='utf-8')
main=(root/'app/src/main/java/id/sch/smpn4dumai/esiswa/MainActivity.java').read_text(encoding='utf-8')
manifest=(root/'app/src/main/AndroidManifest.xml').read_text(encoding='utf-8')
checks={
 'versionCode 21':'versionCode 21' in g,
 'versionName 1.1.3.5.11':"versionName '1.1.3.5.11'" in g,
 'icon inset 13dp':all(f'android:inset{x}="13dp"' in icon for x in ['Left','Top','Right','Bottom']),
 'badge number preserved':'setNumber(1)' in push,
 'all channel badge preserved':all(x in push for x in ['attendance.setShowBadge(true)','coaching.setShowBadge(true)','general.setShowBadge(true)']),
 'persistent login preserved':'getPersistentSessionCredential()' in main and 'savePersistentSessionCredential(String refreshToken, String expiresAt)' in main,
 'FCM service preserved':'extends FirebaseMessagingService' in push,
 'responsive combo preserved':'normalizeAppsScriptOuterFrame' in main and 'setDecorFitsSystemWindows(true)' in main,
 'native print preserved':'__ESISWA_NATIVE_PRINT_V4_INSTALLED' in main,
 'security preserved':'android:allowBackup="false"' in manifest and 'android:usesCleartextTraffic="false"' in manifest,
}
bad=[]
for k,v in checks.items():
    print(('PASS' if v else 'FAIL')+' | '+k)
    if not v: bad.append(k)
print(f'SUMMARY: {len(checks)-len(bad)}/{len(checks)} PASS; failures={len(bad)}')
sys.exit(1 if bad else 0)
