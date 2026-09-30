from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
g=(root/'app/build.gradle').read_text(encoding='utf-8')
icon=(root/'app/src/main/res/drawable/ic_launcher_foreground.xml').read_text(encoding='utf-8')
push=(root/'app/src/main/java/id/sch/smpn4dumai/esiswa/PushMessagingService.java').read_text(encoding='utf-8')
manifest=(root/'app/src/main/AndroidManifest.xml').read_text(encoding='utf-8')
main=(root/'app/src/main/java/id/sch/smpn4dumai/esiswa/MainActivity.java').read_text(encoding='utf-8')
checks={
 'versionCode 20':'versionCode 20' in g,
 'versionName 1.1.3.5.10':"versionName '1.1.3.5.10'" in g,
 'package preserved':"applicationId 'id.sch.smpn4dumai.esiswa'" in g,
 'launcher inset enlarged visual':'android:insetLeft="10dp"' in icon and 'android:insetTop="10dp"' in icon and 'android:insetRight="10dp"' in icon and 'android:insetBottom="10dp"' in icon,
 'old 18dp inset removed':'18dp' not in icon,
 'badge number':'setNumber(1)' in push,
 'attendance badge':'attendance.setShowBadge(true)' in push,
 'coaching badge':'coaching.setShowBadge(true)' in push,
 'general badge':'general.setShowBadge(true)' in push,
 'notification auto cancel retained':'setAutoCancel(true)' in push,
 'notification icon retained':'R.drawable.ic_stat_notification' in push,
 'persistent login retained':'getPersistentSessionCredential()' in main and 'savePersistentSessionCredential(String refreshToken, String expiresAt)' in main,
 'FCM service retained':'extends FirebaseMessagingService' in push,
 'notification permission retained':'android.permission.POST_NOTIFICATIONS' in manifest,
 'security backup disabled':'android:allowBackup="false"' in manifest,
 'security cleartext disabled':'android:usesCleartextTraffic="false"' in manifest,
}
bad=[]
for k,v in checks.items():
    print(('PASS' if v else 'FAIL')+' | '+k)
    if not v: bad.append(k)
print(f'SUMMARY: {len(checks)-len(bad)}/{len(checks)} PASS; failures={len(bad)}')
sys.exit(1 if bad else 0)
